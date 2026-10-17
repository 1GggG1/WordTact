#!/usr/bin/env python3
"""Version-bound revision snapshots, batch writes and validation receipts.

Only the explicitly named project and session are used. Receipt checks verify
integrity and completeness; they do not establish literary or semantic truth.
"""
from __future__ import annotations

import argparse
import contextlib
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import uuid


class GuardError(ValueError):
    """A revision precondition was not met."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise GuardError("invalid JSON: {}".format(path)) from exc


def require(condition, message):
    if not condition:
        raise GuardError(message)


def safe_path(root, name):
    """Project-relative path with no symlinks, even for existing ancestors."""
    require(isinstance(name, str) and bool(name), "path must be a nonempty string")
    relative = Path(name)
    require(not relative.is_absolute() and ".." not in relative.parts,
            "path must remain relative to project: " + name)
    require(relative.as_posix() == name and name != ".", "path must be canonical: " + name)
    path = root
    for part in relative.parts:
        path = path / part
        require(not path.is_symlink(), "symlink paths are not supported: " + name)
    require(path.resolve().is_relative_to(root), "path escapes project: " + name)
    return path


def source_bytes(path):
    require(path.is_file() and not path.is_symlink(), "expected regular file: {}".format(path))
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeError as exc:
        raise GuardError("source must be UTF-8: {}".format(path)) from exc
    return data


def atomic_bytes(path, data, mode=0o600, expected_sha=None):
    """Per-file replacement, with the source rechecked immediately beforehand."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".revision-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), mode)
        if expected_sha is not None:
            require(digest(source_bytes(path)) == expected_sha,
                    "source changed immediately before write: {}".format(path))
        require(not path.is_symlink(), "refusing symlink write: {}".format(path))
        os.replace(temporary, path)
        directory_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def seal(path, payload):
    value = {"payload": payload, "sha256": digest(canonical(payload))}
    atomic_bytes(path, canonical(value) + b"\n")
    return value["sha256"]


def unseal(path):
    value = read_json(path)
    require(isinstance(value, dict) and set(value) == {"payload", "sha256"},
            "invalid sealed manifest: {}".format(path))
    require(digest(canonical(value["payload"])) == value["sha256"],
            "manifest integrity mismatch: {}".format(path))
    return value["payload"], value["sha256"]


class RevisionGuard:
    def __init__(self, project_root, session):
        supplied = Path(project_root).absolute()
        require(supplied.is_dir(), "project root must be an existing directory")
        self.root = supplied.resolve()
        self.session_name = session
        self.session = safe_path(self.root, session)

    @contextlib.contextmanager
    def locked(self):
        self.session = safe_path(self.root, self.session_name)
        self.session.mkdir(parents=True, exist_ok=True)
        lock = safe_path(self.root, self.session_name + "/.lock")
        with lock.open("a+b") as stream:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise GuardError("another operation holds this session lock") from exc
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def internal(self, name):
        return safe_path(self.root, self.session_name + "/" + name)

    def source(self, name):
        path = safe_path(self.root, name)
        require(not path.is_relative_to(self.session), "source cannot be inside audit session")
        return path

    def put_blob(self, data):
        sha = digest(data)
        path = self.internal("objects/" + sha)
        if path.exists():
            require(digest(path.read_bytes()) == sha, "snapshot object corrupted: " + sha)
        else:
            atomic_bytes(path, data)
        return sha

    def blob(self, sha):
        require(isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha), "invalid object hash")
        data = self.internal("objects/" + sha).read_bytes()
        require(digest(data) == sha, "snapshot object corrupted: " + sha)
        return data

    def load_original(self):
        original, sha = unseal(self.internal("original.json"))
        require(original.get("schema_version") == 1, "unsupported snapshot version")
        require(original.get("project_root") == str(self.root), "snapshot belongs to another project")
        for name, item in original["files"].items():
            self.source(name)
            self.blob(item["sha256"])
        return original, sha

    def load_latest(self):
        original, original_sha = self.load_original()
        latest, sha = unseal(self.internal("latest.json"))
        require(latest["original_manifest_sha256"] == original_sha, "latest snapshot original mismatch")
        require(set(latest["files"]) == set(original["files"]), "latest snapshot scope mismatch")
        for value in latest["files"].values():
            self.blob(value)
        historical, historical_sha = unseal(self.internal("latest-history/" + sha + ".json"))
        require(historical_sha == sha and historical == latest, "latest history mismatch")
        require(latest["state"] in {"BASELINE", "ACCEPTED"}, "invalid latest state")
        if latest["state"] == "BASELINE":
            require(latest["files"] == {name: item["sha256"] for name, item in original["files"].items()} and
                    latest["accepted_batch"] is None, "baseline differs from original")
        else:
            directory, manifest, manifest_sha, _ = self.load_batch(latest["accepted_batch"])
            receipt, receipt_sha = unseal(directory / "receipt.json")
            require(receipt_sha == latest["receipt_sha256"] and latest["files"] == manifest["final_files"],
                    "latest accepted receipt mismatch")
            self.validate_receipt(receipt, manifest, manifest_sha, original, historical=True)
        return latest, sha

    def save_latest(self, latest):
        sha = digest(canonical(latest))
        history = self.internal("latest-history/" + sha + ".json")
        if history.exists():
            saved, saved_sha = unseal(history)
            require(saved_sha == sha and saved == latest, "latest history corruption")
        else:
            seal(history, latest)
        seal(self.internal("latest.json"), latest)

    def snapshot(self, specification):
        require(isinstance(specification, dict) and specification.get("schema_version") == 1,
                "snapshot requires schema_version 1")
        names = specification.get("files")
        require(isinstance(names, list) and names and all(isinstance(n, str) for n in names),
                "files must be a nonempty list of project-relative paths")
        require(len(set(names)) == len(names), "duplicate snapshot files")
        require(type(specification.get("mapping_required")) is bool,
                "mapping_required must explicitly be true or false")
        commit = specification.get("baseline_commit")
        require(commit is None or isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit),
                "baseline_commit must be a full immutable commit ID, not HEAD or a branch")
        with self.locked():
            require(not self.internal("original.json").exists(), "original snapshot already exists; never overwritten")
            require(not self.internal("latest.json").exists(), "session already has a latest snapshot")
            contents = [(name, source_bytes(self.source(name)), stat.S_IMODE(self.source(name).stat().st_mode))
                        for name in names]
            files = {name: {"sha256": self.put_blob(data), "mode": mode} for name, data, mode in contents}
            original = {"schema_version": 1, "project_root": str(self.root), "files": files,
                        "mapping_required": specification["mapping_required"], "baseline_commit": commit}
            original_sha = seal(self.internal("original.json"), original)
            latest = {"schema_version": 1, "original_manifest_sha256": original_sha,
                      "files": {name: item["sha256"] for name, item in files.items()},
                      "state": "BASELINE", "accepted_batch": None, "receipt_sha256": None}
            self.save_latest(latest)
            return {"status": "SNAPSHOT_CREATED", "original_manifest_sha256": original_sha,
                    "note": "BASELINE records input; it does not certify prior acceptance"}

    def resolve_edits(self, text, entry):
        ranges = entry.get("allowed_ranges")
        require(isinstance(ranges, list) and ranges, "explicit allowed_ranges required")
        for bounds in ranges:
            require(isinstance(bounds, list) and len(bounds) == 2 and
                    all(type(v) is int for v in bounds) and 0 <= bounds[0] <= bounds[1] <= len(text),
                    "invalid authorized character range")
        edits = entry.get("edits")
        require(isinstance(edits, list) and edits and all(isinstance(edit, dict) for edit in edits),
                "nonempty edit objects required")
        resolved = []
        for edit in edits:
            old, new = edit.get("old"), edit.get("new")
            require(isinstance(old, str) and isinstance(new, str) and old != new,
                    "edit old/new must be distinct strings")
            if "start" in edit or "end" in edit:
                start, end = edit.get("start"), edit.get("end")
                require(type(start) is int and type(end) is int and 0 <= start <= end <= len(text),
                        "invalid edit offsets")
                require(text[start:end] == old, "old text does not match offsets")
            else:
                require(bool(old), "insertions require explicit start/end offsets")
                positions = [match.start() for match in re.finditer("(?=" + re.escape(old) + ")", text)]
                require(len(positions) == 1, "old quote is not unique; provide exact offsets")
                start, end = positions[0], positions[0] + len(old)
            require(any(lo <= start and end <= hi for lo, hi in ranges), "edit exceeds authorized scope")
            resolved.append({"start": start, "end": end, "old": old, "new": new})
        resolved.sort(key=lambda item: (item["start"], item["end"]))
        for left, right in zip(resolved, resolved[1:]):
            require(left["end"] <= right["start"] and left["start"] != right["start"],
                    "edits overlap or insert at the same position")
        candidate = text
        for edit in reversed(resolved):
            candidate = candidate[:edit["start"]] + edit["new"] + candidate[edit["end"]:]
        require(candidate != text, "batch file must actually change")
        return resolved, candidate

    def prepare(self, specification):
        require(isinstance(specification, dict) and specification.get("schema_version") == 1,
                "prepare requires schema_version 1")
        entries = specification.get("files")
        require(isinstance(entries, list) and entries and all(isinstance(item, dict) for item in entries),
                "prepare files must be a nonempty list")
        with self.locked():
            original, original_sha = self.load_original()
            latest, latest_sha = self.load_latest()
            names = [entry.get("path") for entry in entries]
            require(all(isinstance(name, str) for name in names) and len(names) == len(set(names)),
                    "invalid or duplicate edit file")
            require(set(names).issubset(original["files"]), "edit file is outside frozen session scope")
            # Read the complete scope first, so receipts can bind unchanged files too.
            source_data = {name: source_bytes(self.source(name)) for name in original["files"]}
            prepared, diffs = [], []
            for entry in entries:
                name = entry["path"]
                data = source_data[name]
                source_sha = digest(data)
                require(entry.get("sha256") == source_sha, "stale source hash: " + name)
                text = data.decode("utf-8")
                edits, candidate = self.resolve_edits(text, entry)
                diffs.extend(difflib.unified_diff(text.splitlines(keepends=True), candidate.splitlines(keepends=True),
                                                fromfile=name + ":before", tofile=name + ":candidate"))
                prepared.append({"path": name, "source_sha256": source_sha,
                                 "candidate_sha256": digest(candidate.encode("utf-8")),
                                 "mode": stat.S_IMODE(self.source(name).stat().st_mode),
                                 "allowed_ranges": entry["allowed_ranges"], "edits": edits,
                                 "candidate_data": candidate.encode("utf-8")})
            # No session candidate data is created until every edit passes preflight.
            for data in source_data.values():
                self.put_blob(data)
            for entry in prepared:
                self.put_blob(entry.pop("candidate_data"))
            batch_id = uuid.uuid4().hex
            directory = self.internal("batches/" + batch_id)
            directory.mkdir(parents=True)
            diff_bytes = "".join(diffs).encode("utf-8")
            atomic_bytes(directory / "changes.diff", diff_bytes)
            sources = {name: digest(data) for name, data in source_data.items()}
            finals = dict(sources)
            finals.update({entry["path"]: entry["candidate_sha256"] for entry in prepared})
            manifest = {"schema_version": 1, "batch_id": batch_id,
                        "original_manifest_sha256": original_sha, "latest_manifest_sha256": latest_sha,
                        "source_files": sources, "final_files": finals, "files": prepared,
                        "diff_sha256": digest(diff_bytes)}
            manifest_sha = seal(directory / "manifest.json", manifest)
            journal = {"batch_id": batch_id, "manifest_sha256": manifest_sha, "status": "PREPARED",
                       "files": {name: "PENDING" for name in names}}
            seal(directory / "journal.json", journal)
            return {"status": "PREPARED", "batch_id": batch_id, "manifest_sha256": manifest_sha,
                    "original_manifest_sha256": original_sha, "latest_manifest_sha256": latest_sha,
                    "files": finals, "diff": str(directory / "changes.diff")}

    def load_batch(self, batch_id):
        require(isinstance(batch_id, str) and re.fullmatch(r"[0-9a-f]{32}", batch_id), "invalid batch ID")
        directory = self.internal("batches/" + batch_id)
        manifest, sha = unseal(directory / "manifest.json")
        original, original_sha = self.load_original()
        require(manifest.get("batch_id") == batch_id and manifest.get("schema_version") == 1,
                "batch identity/version mismatch")
        require(manifest["original_manifest_sha256"] == original_sha, "batch original mismatch")
        baseline, baseline_sha = unseal(self.internal("latest-history/" + manifest["latest_manifest_sha256"] + ".json"))
        require(baseline_sha == manifest["latest_manifest_sha256"] and
                baseline["original_manifest_sha256"] == original_sha and
                set(baseline["files"]) == set(original["files"]), "batch latest baseline mismatch")
        for object_sha in baseline["files"].values():
            self.blob(object_sha)
        require(set(manifest["source_files"]) == set(original["files"]) and
                set(manifest["final_files"]) == set(original["files"]), "batch frozen scope mismatch")
        names = [entry["path"] for entry in manifest["files"]]
        require(names and len(set(names)) == len(names), "duplicate/empty batch files")
        require(set(names).issubset(original["files"]), "batch file outside frozen scope")
        expected_final = dict(manifest["source_files"])
        for name, source_sha in manifest["source_files"].items():
            self.source(name)
            self.blob(source_sha)
        diffs = []
        for entry in manifest["files"]:
            name = entry["path"]
            require(entry["source_sha256"] == manifest["source_files"][name], "batch source mismatch")
            source = self.blob(entry["source_sha256"]).decode("utf-8")
            edits, candidate = self.resolve_edits(source, entry)
            require(edits == entry["edits"], "batch edits not canonical")
            require(candidate.encode("utf-8") == self.blob(entry["candidate_sha256"]),
                    "candidate differs from scoped edits")
            expected_final[name] = entry["candidate_sha256"]
            diffs.extend(difflib.unified_diff(source.splitlines(keepends=True), candidate.splitlines(keepends=True),
                                            fromfile=name + ":before", tofile=name + ":candidate"))
        require(expected_final == manifest["final_files"], "batch final scope mismatch")
        diff_bytes = (directory / "changes.diff").read_bytes()
        require(digest(diff_bytes) == manifest["diff_sha256"] and "".join(diffs).encode("utf-8") == diff_bytes,
                "batch diff integrity mismatch")
        journal, _ = unseal(directory / "journal.json")
        require(journal["manifest_sha256"] == sha and journal["batch_id"] == batch_id and
                set(journal["files"]) == set(names), "journal batch mismatch")
        return directory, manifest, sha, journal

    def save_journal(self, directory, journal):
        seal(directory / "journal.json", journal)

    def current_hashes(self, manifest):
        return {name: digest(source_bytes(self.source(name))) for name in manifest["source_files"]}

    def replace_source(self, name, data, expected_sha, mode):
        atomic_bytes(self.source(name), data, mode=mode, expected_sha=expected_sha)

    def apply(self, batch_id):
        with self.locked():
            directory, manifest, manifest_sha, journal = self.load_batch(batch_id)
            require(journal["status"] not in {"ROLLING_BACK", "ROLLBACK_PARTIAL", "ROLLED_BACK"},
                    "rolled-back batches cannot be reapplied; prepare a new batch")
            if journal["status"] == "ACCEPTED":
                return self._verify(manifest, manifest_sha)
            latest, latest_sha = self.load_latest()
            require(latest_sha == manifest["latest_manifest_sha256"], "latest accepted baseline changed")
            current = self.current_hashes(manifest)
            # Preflight all files, including ones left unchanged, before any write.
            for name, sha in current.items():
                require(sha in {manifest["source_files"][name], manifest["final_files"][name]},
                        "source changed since prepare: " + name)
            journal["status"] = "APPLYING"
            self.save_journal(directory, journal)
            try:
                for entry in manifest["files"]:
                    name = entry["path"]
                    actual = digest(source_bytes(self.source(name)))
                    if actual != entry["candidate_sha256"]:
                        require(actual == entry["source_sha256"], "source changed during batch: " + name)
                        self.replace_source(name, self.blob(entry["candidate_sha256"]),
                                            entry["source_sha256"], entry["mode"])
                    # Recovers a crash between replacement and the journal write.
                    journal["files"][name] = "WRITTEN"
                    self.save_journal(directory, journal)
                self._verify(manifest, manifest_sha)
                journal["status"] = "APPLIED"
                self.save_journal(directory, journal)
            except Exception:
                journal["status"] = "PARTIAL"
                self.save_journal(directory, journal)
                raise
            return {"status": "APPLIED", "batch_id": batch_id, "files": manifest["final_files"]}

    def _verify(self, manifest, manifest_sha):
        require(self.current_hashes(manifest) == manifest["final_files"], "final text differs from prepared scope")
        return {"status": "VERIFIED_BYTES", "batch_id": manifest["batch_id"],
                "manifest_sha256": manifest_sha, "files": manifest["final_files"],
                "note": "Byte/scope integrity only; literary checks still require bound evidence"}

    def verify(self, batch_id):
        # Does not acquire/create a session lock or mutate audit/source files.
        _, manifest, sha, _ = self.load_batch(batch_id)
        return self._verify(manifest, sha)

    def validate_receipt(self, receipt, manifest, manifest_sha, original, historical=False):
        require(isinstance(receipt, dict) and receipt.get("schema_version") == 1,
                "receipt requires schema_version 1")
        for field, expected in [("batch_id", manifest["batch_id"]), ("manifest_sha256", manifest_sha),
                                ("original_manifest_sha256", manifest["original_manifest_sha256"]),
                                ("latest_manifest_sha256", manifest["latest_manifest_sha256"]),
                                ("files", manifest["final_files"])]:
            require(receipt.get(field) == expected, "receipt {} mismatch".format(field))
        checks = receipt.get("checks")
        require(isinstance(checks, dict) and set(checks) == {"semantics", "frequency", "punctuation", "mapping"},
                "receipt must include semantics, frequency, punctuation and mapping")
        for name, check in checks.items():
            require(isinstance(check, dict), "invalid check receipt: " + name)
            allowed = {"PASS", "RETAINED"} if name == "frequency" else {"PASS"}
            if name == "mapping" and not original["mapping_required"]:
                allowed.add("NOT_APPLICABLE")
            require(check.get("status") in allowed, "check unresolved or skipped: " + name)
            if check.get("status") in {"RETAINED", "NOT_APPLICABLE"}:
                require(isinstance(check.get("reason"), str) and bool(check["reason"].strip()),
                        "specific reason required: " + name)
            evidence = safe_path(self.root, check.get("evidence"))
            if historical:
                self.blob(check.get("sha256"))
            else:
                require(evidence.is_file(), "missing evidence: " + name)
                require(digest(evidence.read_bytes()) == check.get("sha256"), "evidence hash mismatch: " + name)
            artifacts = check.get("artifacts", {})
            require(isinstance(artifacts, dict), "artifacts must map paths to hashes: " + name)
            if name == "mapping" and original["mapping_required"]:
                require(bool(artifacts), "mapping requires bound mapping/output artifacts")
            for artifact_name, artifact_sha in artifacts.items():
                artifact = safe_path(self.root, artifact_name)
                if historical:
                    self.blob(artifact_sha)
                else:
                    require(artifact.is_file() and digest(artifact.read_bytes()) == artifact_sha,
                            "artifact hash mismatch: " + artifact_name)

    def snapshot_receipt_evidence(self, receipt):
        for check in receipt["checks"].values():
            sources = dict(check.get("artifacts", {}))
            sources[check["evidence"]] = check["sha256"]
            for name, sha in sources.items():
                data = safe_path(self.root, name).read_bytes()
                require(digest(data) == sha, "evidence changed during acceptance: " + name)
                self.put_blob(data)

    def accept(self, batch_id, receipt):
        with self.locked():
            directory, manifest, manifest_sha, journal = self.load_batch(batch_id)
            require(journal["status"] in {"APPLIED", "ACCEPTED"}, "only a fully applied batch can be accepted")
            original, _ = self.load_original()
            self.validate_receipt(receipt, manifest, manifest_sha, original)
            self._verify(manifest, manifest_sha)
            latest, latest_sha = self.load_latest()
            receipt_sha = digest(canonical(receipt))
            if latest["accepted_batch"] == batch_id:
                require(latest["receipt_sha256"] == receipt_sha, "accepted receipt changed")
                saved, saved_sha = unseal(directory / "receipt.json")
                require(saved_sha == receipt_sha and saved == receipt, "stored receipt mismatch")
            else:
                require(latest_sha == manifest["latest_manifest_sha256"], "latest accepted baseline changed")
                self.snapshot_receipt_evidence(receipt)
                receipt_path = directory / "receipt.json"
                if receipt_path.exists():
                    saved, saved_sha = unseal(receipt_path)
                    require(saved_sha == receipt_sha and saved == receipt, "pending acceptance receipt changed")
                else:
                    seal(receipt_path, receipt)
                latest = {"schema_version": 1, "original_manifest_sha256": manifest["original_manifest_sha256"],
                          "files": manifest["final_files"], "state": "ACCEPTED", "accepted_batch": batch_id,
                          "receipt_sha256": receipt_sha}
                self.validate_receipt(receipt, manifest, manifest_sha, original)
                self._verify(manifest, manifest_sha)
                self.save_latest(latest)
            journal["status"] = "ACCEPTED"
            self.save_journal(directory, journal)
            return {"status": "ACCEPTED", "batch_id": batch_id, "receipt_sha256": receipt_sha,
                    "note": "Evidence receipts validated; the caller remains responsible for their judgments"}

    def rollback(self, batch_id):
        with self.locked():
            directory, manifest, _, journal = self.load_batch(batch_id)
            latest, latest_sha = self.load_latest()
            require(journal["status"] != "ACCEPTED" and latest["accepted_batch"] != batch_id,
                    "accepted revisions require a new reviewed reversal batch")
            require(latest_sha == manifest["latest_manifest_sha256"],
                    "latest accepted baseline changed; prepare a reviewed reversal instead")
            current = self.current_hashes(manifest)
            for name, sha in current.items():
                require(sha in {manifest["source_files"][name], manifest["final_files"][name]},
                        "refusing to overwrite concurrent change: " + name)
            journal["status"] = "ROLLING_BACK"
            self.save_journal(directory, journal)
            try:
                for entry in reversed(manifest["files"]):
                    name = entry["path"]
                    actual = digest(source_bytes(self.source(name)))
                    if actual != entry["source_sha256"]:
                        require(actual == entry["candidate_sha256"], "refusing concurrent rollback: " + name)
                        self.replace_source(name, self.blob(entry["source_sha256"]),
                                            entry["candidate_sha256"], entry["mode"])
                    journal["files"][name] = "RESTORED"
                    self.save_journal(directory, journal)
                require(self.current_hashes(manifest) == manifest["source_files"], "rollback source verification failed")
                journal["status"] = "ROLLED_BACK"
                self.save_journal(directory, journal)
            except Exception:
                journal["status"] = "ROLLBACK_PARTIAL"
                self.save_journal(directory, journal)
                raise
            return {"status": "ROLLED_BACK", "batch_id": batch_id,
                    "note": "Restored this batch's inputs; unresolved review findings are not cleared"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--session", required=True, help="project-relative audit session directory")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ["snapshot", "prepare"]:
        subparsers.add_parser(command).add_argument("--input", required=True, help="JSON input path")
    for command in ["apply", "verify", "rollback", "accept"]:
        sub = subparsers.add_parser(command)
        sub.add_argument("--batch", required=True)
        if command == "accept":
            sub.add_argument("--receipt", required=True)
    args = parser.parse_args(argv)
    try:
        guard = RevisionGuard(args.project_root, args.session)
        if args.command in {"snapshot", "prepare"}:
            result = getattr(guard, args.command)(read_json(Path(args.input)))
        elif args.command == "accept":
            result = guard.accept(args.batch, read_json(Path(args.receipt)))
        else:
            result = getattr(guard, args.command)(args.batch)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (GuardError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
