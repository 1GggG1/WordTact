#!/usr/bin/env python3
"""Versioned, source-anchored reader knowledge index; Python 3.9+, stdlib only.

This validates provenance, not the truth of fiction or an LLM's editorial judgment.
See ../references/reader-index.md for the input contract.
"""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


SCHEMA_VERSION = 1
DEFAULT_INDEX = "agent/reader-index/index.json"
EPISTEMIC = {"fact", "assertion", "inference", "lie", "unresolved"}


class IndexValidationError(ValueError):
    """Input or on-disk state cannot safely be accepted."""


def require(condition, message):
    if not condition:
        raise IndexValidationError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_digest(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def rooted(root, relative):
    root = root.resolve()
    require(isinstance(relative, str) and relative, "path must be a nonempty relative string")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, "path must remain inside project")
    target = (root / path).resolve()
    require(target != root and root in target.parents, "path escapes project or names project root")
    return target


def read_json(path):
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise IndexValidationError("cannot read JSON {}: {}".format(path.name, exc)) from exc
    require(isinstance(value, dict), "JSON root must be an object")
    return value


def text_file(root, relative):
    path = rooted(root, relative)
    try:
        raw = path.read_bytes()
        return raw.decode("utf-8"), digest(raw)
    except (OSError, UnicodeError) as exc:
        raise IndexValidationError("cannot read UTF-8 source {}: {}".format(relative, exc)) from exc


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def span_text(root, span, snapshot=False, exact_file=True):
    require(isinstance(span, dict), "span must be an object")
    text, sha = text_file(root, span.get("path"))
    start, end = span.get("start"), span.get("end")
    require(integer(start) and integer(end) and 0 <= start < end <= len(text),
            "invalid nonempty character span for {}".format(span.get("path")))
    excerpt = text[start:end]
    if snapshot:
        require(isinstance(span.get("sha256"), str) and len(span["sha256"]) == 64,
                "whole-file sha256 is required")
        require(not exact_file or sha == span["sha256"], "stale whole-file hash")
        require(digest(excerpt.encode("utf-8")) == span.get("slice_sha256"), "stale slice hash")
    return excerpt, sha


def span_key(span):
    return (span["path"], span["start"], span["end"])


def plain_spans(spans):
    return [{key: span[key] for key in ("path", "start", "end")} for span in spans]


def normalized_intervals(root, spans, verify_sources=True):
    """Reject duplicates/overlaps before coalescing adjacent intervals."""
    by_path = {}
    for span in spans:
        if verify_sources:
            span_text(root, span)
        else:
            require(isinstance(span, dict) and integer(span.get("start")) and integer(span.get("end"))
                    and 0 <= span["start"] < span["end"], "invalid declared span")
        canonical = str(rooted(root, span["path"]))
        by_path.setdefault(canonical, []).append((span["start"], span["end"]))
    result = {}
    for path, intervals in by_path.items():
        merged = []
        for start, end in sorted(intervals):
            require(not merged or start >= merged[-1][1], "duplicate or overlapping source slices")
            if merged and start == merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))
        result[path] = merged
    return result


def load_manifest(root, reference, exact_hash=False, verify_sources=True, fallback_defs=None):
    require(isinstance(reference, dict), "manifest reference is required")
    path = rooted(root, reference.get("path"))
    data = read_json(path)
    sha = digest(path.read_bytes())
    require(not exact_hash or reference.get("sha256") == sha, "stale manifest hash")
    require(data.get("schema_version") == SCHEMA_VERSION, "unsupported manifest schema")
    units = data.get("units")
    require(isinstance(units, list) and units, "manifest requires ordered units")
    data = copy.deepcopy(data)
    units = data["units"]
    fallback = {unit["unit_id"]: unit for unit in (fallback_defs or [])}
    shorthand_only = all(isinstance(unit, dict) and "path" in unit and "reading" not in unit for unit in units)
    for unit in units:
        require(isinstance(unit, dict), "manifest unit must be an object")
        if "unit_id" not in unit and "id" in unit:
            unit["unit_id"] = unit.pop("id")
        if "path" in unit and "reading" not in unit:
            try:
                length = len(text_file(root, unit["path"])[0])
            except IndexValidationError:
                require(not verify_sources and unit.get("unit_id") in fallback,
                        "cannot resolve whole-file manifest source")
                length = fallback[unit["unit_id"]]["reading"][0]["end"]
            unit["reading"] = [{"path": unit.pop("path"), "start": 0, "end": length}]
    ids = []
    reading, canonical = [], []
    for unit in units:
        require(isinstance(unit, dict), "manifest unit must be an object")
        uid = unit.get("unit_id")
        require(isinstance(uid, str) and uid and uid not in ids, "unit IDs must be unique nonempty strings")
        ids.append(uid)
        spans = unit.get("reading")
        require(isinstance(spans, list) and spans, "unit requires reading slices")
        actual = "".join(span_text(root, span)[0] for span in spans) if verify_sources else None
        reading.extend(spans)
        mapped = unit.get("canonical", [])
        require(isinstance(mapped, list), "canonical slices must be a list")
        if mapped and verify_sources:
            require(actual == "".join(span_text(root, span)[0] for span in mapped),
                    "reading/canonical mapping is not exact or is out of order")
        canonical.extend(mapped)
    if shorthand_only and "coverage" not in data:
        data["coverage"] = {"reading": copy.deepcopy(reading), "canonical": []}
    coverage = data.get("coverage")
    require(isinstance(coverage, dict) and isinstance(coverage.get("reading"), list),
            "manifest requires explicit reading coverage")
    for role, actual in (("reading", reading), ("canonical", canonical)):
        declared = coverage.get(role, [])
        require(isinstance(declared, list), "coverage must be a list")
        require(normalized_intervals(root, actual, verify_sources) == normalized_intervals(root, declared, verify_sources),
                "{} coverage has gaps or undeclared slices".format(role))
    return data, sha


def validate_anchor(root, anchor, exact_file=True):
    require(isinstance(anchor, dict), "source anchor must be an object")
    excerpt, sha = span_text(root, anchor)
    require(isinstance(anchor.get("sha256"), str) and len(anchor["sha256"]) == 64,
            "anchor requires whole-file sha256")
    require(not exact_file or sha == anchor["sha256"], "stale source evidence")
    require(anchor.get("quote") == excerpt, "source quote does not match its span")


def validate_unit(root, unit, definition, revision=None, exact_file=True):
    require(isinstance(unit, dict) and unit.get("unit_id") == definition["unit_id"], "unit ID mismatch")
    for role in ("reading", "canonical"):
        spans = unit.get(role, [])
        require(isinstance(spans, list), "unit slices must be lists")
        for span in spans:
            span_text(root, span, snapshot=True, exact_file=exact_file)
        require(plain_spans(spans) == plain_spans(definition.get(role, [])),
                "unit slices disagree with current manifest")
    content = "".join(span_text(root, span)[0] for span in unit["reading"])
    acceptance = unit.get("acceptance")
    require(isinstance(acceptance, dict) and acceptance.get("status") == "accepted",
            "unit must have explicit accepted status")
    require(acceptance.get("content_sha256") == digest(content.encode("utf-8")),
            "acceptance is not bound to this reading text")
    # Slice-preserving changes can leave earlier manuscript disclosures valid,
    # but an amended acceptance report may revoke the very status it attests.
    # Evidence files are therefore always bound as complete immutable versions.
    validate_anchor(root, acceptance.get("evidence"), exact_file=True)
    review = unit.get("review")
    require(isinstance(review, dict) and review.get("confirmed") is True,
            "unit must be explicitly re-reviewed")
    require(integer(review.get("base_revision")), "review requires base_revision")
    require(revision is None or review["base_revision"] == revision,
            "review does not attest current index revision")
    records = unit.get("disclosures")
    require(isinstance(records, list), "disclosures must be a list, including when empty")
    seen = set()
    for record in records:
        require(isinstance(record, dict), "disclosure must be an object")
        rid = record.get("id")
        require(isinstance(rid, str) and rid and rid not in seen, "duplicate or missing disclosure ID in unit")
        seen.add(rid)
        require(isinstance(record.get("summary"), str) and record["summary"].strip(), "summary required")
        require(record.get("epistemic") in EPISTEMIC, "unknown epistemic label")
        require(bool(record.get("speaker")) or bool(record.get("pov")), "speaker or POV required")
        anchors = record.get("anchors")
        require(isinstance(anchors, list) and anchors, "disclosure requires literal reading anchors")
        for anchor in anchors:
            require(isinstance(anchor, dict), "disclosure anchor must be an object")
            number = anchor.get("slice")
            require(integer(number) and 0 <= number < len(unit["reading"]), "invalid reading-slice number")
            source = unit["reading"][number]
            start, end = anchor.get("start"), anchor.get("end")
            require(integer(start) and integer(end) and source["start"] <= start < end <= source["end"],
                    "disclosure anchor is outside its reading slice")
            raw = text_file(root, source["path"])[0]
            require(raw[start:end] == anchor.get("quote"), "disclosure quote mismatch")
    protected = unit.get("protected", [])
    require(isinstance(protected, list), "protected must be a list")
    for item in protected:
        require(isinstance(item, dict) and isinstance(item.get("reason"), str) and item["reason"].strip(),
                "protection requires its reason")
        validate_anchor(root, item.get("source"), exact_file=True)


def validate_links(units, order):
    """References only point backward to an already covered first disclosure."""
    first = {}
    by_id = {unit["unit_id"]: unit for unit in units}
    for uid in order:
        if uid not in by_id:
            continue
        for record in by_id[uid]["disclosures"]:
            rid = record["id"]
            require(record.get("first_in") == first.get(rid, uid),
                    "first_in must name the earliest covered occurrence, never a future unit")
            first.setdefault(rid, uid)


def read_index(root, relative=DEFAULT_INDEX):
    path = rooted(root, relative)
    if not path.exists():
        return None
    index = read_json(path)
    require(index.get("schema_version") == SCHEMA_VERSION, "unsupported index schema")
    require(integer(index.get("revision")) and index["revision"] >= 1, "invalid index revision")
    require(isinstance(index.get("order"), list) and isinstance(index.get("units"), list), "invalid index state")
    order = index["order"]
    require(all(isinstance(uid, str) and uid for uid in order) and len(set(order)) == len(order),
            "invalid stored order")
    unit_ids = [unit.get("unit_id") for unit in index["units"] if isinstance(unit, dict)]
    require(len(unit_ids) == len(index["units"]) and unit_ids == order[:len(unit_ids)],
            "stored units must be a unique contiguous prefix")
    return index


def inspect(root, index):
    if index is None:
        return {"state": "UNINITIALIZED", "revision": 0, "valid_prefix": [],
                "missing": [], "invalidated": [], "issues": ["no accepted index yet"]}
    old_order = index["order"]
    current_order = old_order
    valid, issues = [], []
    try:
        manifest, _ = load_manifest(root, index["manifest"], verify_sources=False,
                                    fallback_defs=index.get("definitions", []))
        current_order = [unit["unit_id"] for unit in manifest["units"]]
        old_defs = index.get("definitions", [])
        for number, uid in enumerate(current_order):
            if number >= len(old_order) or uid != old_order[number]:
                issues.append("reading order changed at {}".format(uid))
                break
            definition = manifest["units"][number]
            if number >= len(old_defs) or definition != old_defs[number]:
                issues.append("mapping changed at {}".format(uid))
                break
            if number >= len(index["units"]):
                break
            try:
                validate_unit(root, index["units"][number], definition, exact_file=False)
                validate_links(index["units"][:number + 1], current_order[:number + 1])
            except (IndexValidationError, KeyError, TypeError) as exc:
                issues.append("{}: {}".format(uid, exc))
                break
            valid.append(uid)
    except (IndexValidationError, KeyError, TypeError) as exc:
        issues.append(str(exc))
    covered = [unit["unit_id"] for unit in index["units"]]
    invalidated = [uid for uid in covered if uid not in valid]
    missing = current_order[len(valid):]
    return {"state": "VALID" if not issues and not missing and not invalidated else "NEEDS_VERIFICATION",
            "revision": index["revision"], "valid_prefix": valid, "order": current_order,
            "missing": missing, "invalidated": invalidated, "issues": issues}


def status(root, relative=DEFAULT_INDEX):
    return inspect(root, read_index(root, relative))


def context(root, before, relative=DEFAULT_INDEX):
    index = read_index(root, relative)
    report = inspect(root, index)
    require(index is not None, "no index: build accepted prefix before querying")
    order = report["order"]
    require(before in order, "target is absent from current reading order")
    preceding = order[:order.index(before)]
    allowed = set(report["valid_prefix"]) & set(preceding)
    report["target"] = before
    report["units"] = []
    for unit in index["units"]:
        if unit["unit_id"] in allowed:
            current = refreshed_hashes(root, unit)
            report["units"].append({key: current.get(key, [])
                                    for key in ("unit_id", "reading", "canonical", "disclosures")})
    report["uncovered_before_target"] = [uid for uid in preceding if uid not in allowed]
    # Acceptance reports and author directions are editorial metadata, not reader
    # knowledge. A report may mention later chapters; never expose it in context.
    return report


def refreshed_hashes(root, unit):
    unit = copy.deepcopy(unit)
    for role in ("reading", "canonical"):
        for span in unit.get(role, []):
            _, span["sha256"] = span_text(root, span, snapshot=True, exact_file=False)
    # Never refresh acceptance/decision evidence without an explicit re-review.
    # Only already-validated, unchanged manuscript slices retain their records.
    return unit


def commit(root, candidate, relative=DEFAULT_INDEX):
    require(isinstance(candidate, dict) and candidate.get("schema_version") == SCHEMA_VERSION,
            "unsupported candidate schema")
    expected = candidate.get("expected_revision")
    require(integer(expected) and expected >= 0, "expected_revision must be a nonnegative integer")
    supplied = candidate.get("units")
    require(isinstance(supplied, list), "candidate units must be a list")
    target = rooted(root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = rooted(root, relative + ".lock")
    try:
        lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise IndexValidationError("index is locked; do not remove a live writer's lock") from exc
    temp_path = None
    try:
        os.write(lock_fd, str(os.getpid()).encode("ascii"))
        os.close(lock_fd)
        index = read_index(root, relative)
        previous_revision = index["revision"] if index else 0
        fingerprint = json_digest(candidate)
        if index and fingerprint == index.get("last_candidate_sha256"):
            report = inspect(root, index)
            require(not report["invalidated"] and not report["issues"],
                    "identical retry has stale source; re-review and submit new candidate")
            return {"revision": previous_revision, "idempotent": True, "coverage": report}
        require(expected == previous_revision, "stale expected_revision")
        manifest, sha = load_manifest(root, candidate.get("manifest"), exact_hash=True)
        order = [unit["unit_id"] for unit in manifest["units"]]
        definitions = {unit["unit_id"]: unit for unit in manifest["units"]}
        old_report = inspect(root, index)
        retain_ids = old_report["valid_prefix"]
        # Changing manifest identity is a change of reading plan, requiring re-review.
        if index and candidate["manifest"]["path"] != index["manifest"]["path"]:
            retain_ids = []
        old_units = {unit["unit_id"]: unit for unit in index["units"]} if index else {}
        merged = {uid: refreshed_hashes(root, old_units[uid]) for uid in retain_ids if uid in order}
        seen = set()
        for unit in copy.deepcopy(supplied):
            if isinstance(unit, dict) and "unit_id" not in unit and "id" in unit:
                unit["unit_id"] = unit.pop("id")
            require(isinstance(unit, dict), "candidate unit must be an object")
            uid = unit.get("unit_id")
            require(isinstance(uid, str) and uid in definitions and uid not in seen, "unknown or duplicate candidate unit")
            seen.add(uid)
            validate_unit(root, unit, definitions[uid], revision=expected)
            merged[uid] = copy.deepcopy(unit)
        # Re-reviewing old disclosures also invalidates their unreviewed downstream
        # records even when the manuscript bytes have not changed.
        replaced = [order.index(uid) for uid in seen if uid in retain_ids]
        if replaced:
            for uid in order[min(replaced):]:
                if uid not in seen:
                    merged.pop(uid, None)
        units = []
        for uid in order:
            if uid not in merged:
                break
            units.append(merged[uid])
        require(not (seen - {unit["unit_id"] for unit in units}),
                "candidate leaves a coverage gap; submit a contiguous accepted prefix")
        validate_links(units, order)
        result = {"schema_version": SCHEMA_VERSION, "revision": previous_revision + 1,
                  "manifest": {"path": candidate["manifest"]["path"], "sha256": sha},
                  "order": order, "definitions": manifest["units"],
                  "coverage_definition": manifest["coverage"], "units": units,
                  "last_candidate_sha256": fingerprint}
        # Revalidate all data immediately before replacement to catch source changes
        # during preparation. External manuscript editors do not share our index lock.
        current_manifest, current_sha = load_manifest(root, result["manifest"], exact_hash=True)
        require(current_manifest == manifest and current_sha == sha, "manifest changed during commit")
        for unit in units:
            validate_unit(root, unit, definitions[unit["unit_id"]])
        descriptor, name = tempfile.mkstemp(prefix=".reader-index-", suffix=".tmp", dir=str(target.parent))
        temp_path = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        require(rooted(root, relative) == target, "index path changed during commit")
        os.replace(str(temp_path), str(target))
        temp_path = None
        return {"revision": result["revision"], "idempotent": False, "coverage": inspect(root, result)}
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--index", default=DEFAULT_INDEX, help="project-relative index path")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    query = commands.add_parser("context")
    query.add_argument("--before", required=True)
    writer = commands.add_parser("commit")
    writer.add_argument("--input", required=True, type=Path, help="candidate JSON path (never inferred)")
    args = parser.parse_args(argv)
    try:
        root = args.project_root.resolve()
        require(root.is_dir(), "project root must be an existing directory")
        if args.command == "status":
            result = status(root, args.index)
        elif args.command == "context":
            result = context(root, args.before, args.index)
        else:
            result = commit(root, read_json(args.input), args.index)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (IndexValidationError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
