from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "user/novel-ci/scripts/revision_guard.py"
SPEC = importlib.util.spec_from_file_location("revision_guard", SCRIPT)
guard_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard_module)
Guard = guard_module.RevisionGuard
Error = guard_module.GuardError
digest = guard_module.digest


class RevisionGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="revision-tests-")
        self.root = Path(self.temp.name)
        (self.root / "manuscript").mkdir()
        self.texts = {
            "manuscript/one.md": "门还开着。\n她已经核对过名单。\n",
            "manuscript/two.md": "他不能排除夜里仍有人来。\n",
        }
        for name, text in self.texts.items():
            (self.root / name).write_text(text, encoding="utf-8")
        self.guard = Guard(self.root, "agent/audits/session")
        self.snapshot_spec = {"schema_version": 1, "files": list(self.texts), "mapping_required": False}
        self.guard.snapshot(self.snapshot_spec)

    def tearDown(self):
        self.temp.cleanup()

    def edits(self, two=False):
        entries = []
        changes = [("manuscript/one.md", "门还开着", "门敞着")]
        if two:
            changes.append(("manuscript/two.md", "仍有人", "有人"))
        for name, old, new in changes:
            data = (self.root / name).read_bytes()
            entries.append({"path": name, "sha256": digest(data),
                            "allowed_ranges": [[0, len(data.decode("utf-8"))]],
                            "edits": [{"old": old, "new": new}]})
        return {"schema_version": 1, "files": entries}

    def receipt(self, prepared):
        report_name = "report-" + prepared["batch_id"] + ".json"
        report = self.root / report_name
        report.write_text(json.dumps({"files": prepared["files"], "observations": []}), encoding="utf-8")
        checks = {name: {"status": "PASS", "evidence": report_name, "sha256": digest(report.read_bytes())}
                  for name in ["semantics", "frequency", "punctuation", "mapping"]}
        checks["mapping"].update(status="NOT_APPLICABLE", reason="No publication mapping in this scope")
        result = {key: prepared[key] for key in ["batch_id", "manifest_sha256",
                                                "original_manifest_sha256", "latest_manifest_sha256", "files"]}
        result.update(schema_version=1, checks=checks)
        return result

    def test_snapshot_is_immutable_and_separate_from_latest(self):
        original = self.guard.internal("original.json").read_bytes()
        with self.assertRaisesRegex(Error, "never overwritten"):
            self.guard.snapshot(self.snapshot_spec)
        prepared = self.guard.prepare(self.edits())
        self.guard.apply(prepared["batch_id"])
        self.guard.accept(prepared["batch_id"], self.receipt(prepared))
        latest, _ = self.guard.load_latest()
        self.assertEqual(latest["state"], "ACCEPTED")
        self.assertEqual(latest["files"], prepared["files"])
        self.assertEqual(original, self.guard.internal("original.json").read_bytes())
        snapshot, _ = self.guard.load_original()
        self.assertEqual(self.guard.blob(snapshot["files"]["manuscript/one.md"]["sha256"]).decode(),
                         self.texts["manuscript/one.md"])

    def test_all_files_preflight_before_any_candidate_or_source_write(self):
        edits = self.edits(two=True)
        edits["files"][1]["edits"][0]["old"] = "does not exist"
        with self.assertRaisesRegex(Error, "not unique"):
            self.guard.prepare(edits)
        self.assertFalse(self.guard.internal("batches").exists())
        self.assertEqual((self.root / "manuscript/one.md").read_text(), self.texts["manuscript/one.md"])

    def test_nonunique_quote_needs_offsets_and_unicode_character_scope(self):
        path = self.root / "manuscript/one.md"
        text = "甲说门开着。乙说门开着。"
        path.write_text(text, encoding="utf-8")
        entry = {"path": "manuscript/one.md", "sha256": digest(path.read_bytes()),
                 "allowed_ranges": [[2, 5]], "edits": [{"old": "门开着", "new": "门敞着"}]}
        spec = {"schema_version": 1, "files": [entry]}
        with self.assertRaisesRegex(Error, "not unique"):
            self.guard.prepare(spec)
        entry["edits"][0].update(start=2, end=5)
        prepared = self.guard.prepare(spec)
        self.guard.apply(prepared["batch_id"])
        self.assertEqual(path.read_text(), "甲说门敞着。乙说门开着。")

    def test_scope_overlap_and_insertion_checks(self):
        spec = self.edits()
        spec["files"][0]["allowed_ranges"] = [[0, 2]]
        with self.assertRaisesRegex(Error, "exceeds"):
            self.guard.prepare(spec)
        spec = self.edits()
        spec["files"][0]["edits"].append({"old": "还开", "new": "敞"})
        with self.assertRaisesRegex(Error, "overlap"):
            self.guard.prepare(spec)
        spec = self.edits()
        spec["files"][0]["edits"] = [{"old": "", "new": "后来，"}]
        with self.assertRaisesRegex(Error, "insertions require"):
            self.guard.prepare(spec)
        spec["files"][0]["edits"][0].update(start=0, end=0)
        prepared = self.guard.prepare(spec)
        self.guard.apply(prepared["batch_id"])
        self.assertTrue((self.root / "manuscript/one.md").read_text().startswith("后来，"))

    def test_stale_prepare_and_stale_apply_touch_no_other_source(self):
        spec = self.edits(two=True)
        spec["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(Error, "stale source"):
            self.guard.prepare(spec)
        prepared = self.guard.prepare(self.edits(two=True))
        (self.root / "manuscript/two.md").write_text("并发修改", encoding="utf-8")
        with self.assertRaisesRegex(Error, "source changed"):
            self.guard.apply(prepared["batch_id"])
        self.assertEqual((self.root / "manuscript/one.md").read_text(), self.texts["manuscript/one.md"])

    def test_apply_recovers_after_middle_write_failure(self):
        prepared = self.guard.prepare(self.edits(two=True))
        real = self.guard.replace_source
        calls = []

        def fail_second(*args):
            calls.append(args[0])
            if len(calls) == 2:
                raise OSError("simulated disk error")
            real(*args)

        with mock.patch.object(self.guard, "replace_source", side_effect=fail_second):
            with self.assertRaises(OSError):
                self.guard.apply(prepared["batch_id"])
        _, _, _, journal = self.guard.load_batch(prepared["batch_id"])
        self.assertEqual(journal["status"], "PARTIAL")
        self.assertEqual(journal["files"], {"manuscript/one.md": "WRITTEN", "manuscript/two.md": "PENDING"})
        self.assertEqual(self.guard.apply(prepared["batch_id"])["status"], "APPLIED")
        self.assertEqual(self.guard.apply(prepared["batch_id"])["status"], "APPLIED")
        self.assertEqual(self.guard.verify(prepared["batch_id"])["files"], prepared["files"])

    def test_apply_recovers_if_process_dies_between_replace_and_journal(self):
        prepared = self.guard.prepare(self.edits(two=True))
        real = self.guard.save_journal
        calls = []

        def die_after_write(*args):
            calls.append(1)
            if len(calls) == 2:
                raise KeyboardInterrupt()
            real(*args)

        with mock.patch.object(self.guard, "save_journal", side_effect=die_after_write):
            with self.assertRaises(KeyboardInterrupt):
                self.guard.apply(prepared["batch_id"])
        self.assertEqual(self.guard.apply(prepared["batch_id"])["status"], "APPLIED")

    def test_immediate_source_recheck_protects_other_writer(self):
        prepared = self.guard.prepare(self.edits())
        real = self.guard.replace_source

        def competing_write(name, *args):
            (self.root / name).write_text("不同编辑器写入", encoding="utf-8")
            real(name, *args)

        with mock.patch.object(self.guard, "replace_source", side_effect=competing_write):
            with self.assertRaisesRegex(Error, "immediately before"):
                self.guard.apply(prepared["batch_id"])
        self.assertEqual((self.root / "manuscript/one.md").read_text(), "不同编辑器写入")

    def test_partial_rollback_recovery_and_no_reapply(self):
        prepared = self.guard.prepare(self.edits(two=True))
        self.guard.apply(prepared["batch_id"])
        real = self.guard.replace_source
        calls = []

        def fail_second(*args):
            calls.append(1)
            if len(calls) == 2:
                raise OSError("simulated restore error")
            real(*args)

        with mock.patch.object(self.guard, "replace_source", side_effect=fail_second):
            with self.assertRaises(OSError):
                self.guard.rollback(prepared["batch_id"])
        self.assertEqual(self.guard.rollback(prepared["batch_id"])["status"], "ROLLED_BACK")
        self.assertEqual(self.guard.rollback(prepared["batch_id"])["status"], "ROLLED_BACK")
        for name, text in self.texts.items():
            self.assertEqual((self.root / name).read_text(), text)
        with self.assertRaisesRegex(Error, "cannot be reapplied"):
            self.guard.apply(prepared["batch_id"])

    def test_rollback_does_not_overwrite_concurrent_change(self):
        prepared = self.guard.prepare(self.edits(two=True))
        self.guard.apply(prepared["batch_id"])
        path = self.root / "manuscript/two.md"
        path.write_text("另一位作者的修改", encoding="utf-8")
        before = (self.root / "manuscript/one.md").read_bytes()
        with self.assertRaisesRegex(Error, "concurrent change"):
            self.guard.rollback(prepared["batch_id"])
        self.assertEqual(path.read_text(), "另一位作者的修改")
        self.assertEqual((self.root / "manuscript/one.md").read_bytes(), before)

    def test_original_candidate_diff_and_manifest_tamper_rejected(self):
        prepared = self.guard.prepare(self.edits())
        directory, manifest, _, _ = self.guard.load_batch(prepared["batch_id"])
        path = self.guard.internal("objects/" + manifest["files"][0]["candidate_sha256"])
        original = path.read_bytes()
        path.write_bytes(b"tampered")
        with self.assertRaisesRegex(Error, "corrupted"):
            self.guard.apply(prepared["batch_id"])
        path.write_bytes(original)
        diff = (directory / "changes.diff").read_bytes()
        (directory / "changes.diff").write_bytes(b"different diff")
        with self.assertRaisesRegex(Error, "diff integrity"):
            self.guard.verify(prepared["batch_id"])
        (directory / "changes.diff").write_bytes(diff)
        snapshot, _ = self.guard.load_original()
        self.guard.internal("objects/" + snapshot["files"]["manuscript/one.md"]["sha256"]).write_bytes(b"bad")
        with self.assertRaisesRegex(Error, "corrupted"):
            self.guard.apply(prepared["batch_id"])

    def test_accept_requires_applied_complete_current_bound_evidence(self):
        prepared = self.guard.prepare(self.edits())
        receipt = self.receipt(prepared)
        with self.assertRaisesRegex(Error, "fully applied"):
            self.guard.accept(prepared["batch_id"], receipt)
        self.guard.apply(prepared["batch_id"])
        for field in ["batch_id", "manifest_sha256", "original_manifest_sha256", "latest_manifest_sha256", "files"]:
            bad = copy.deepcopy(receipt)
            bad[field] = "wrong"
            with self.subTest(field=field), self.assertRaisesRegex(Error, "mismatch"):
                self.guard.accept(prepared["batch_id"], bad)
        for status in ["SKIPPED", "UNRESOLVED", "NEEDS_VERIFICATION", "FAIL"]:
            bad = copy.deepcopy(receipt)
            bad["checks"]["frequency"]["status"] = status
            with self.subTest(status=status), self.assertRaisesRegex(Error, "unresolved or skipped"):
                self.guard.accept(prepared["batch_id"], bad)
        bad = copy.deepcopy(receipt)
        del bad["checks"]["semantics"]
        with self.assertRaisesRegex(Error, "must include"):
            self.guard.accept(prepared["batch_id"], bad)
        (self.root / receipt["checks"]["semantics"]["evidence"]).write_text("edited report", encoding="utf-8")
        with self.assertRaisesRegex(Error, "evidence hash"):
            self.guard.accept(prepared["batch_id"], receipt)
        receipt = self.receipt(prepared)
        (self.root / "manuscript/two.md").write_text("changed unrelated scope file", encoding="utf-8")
        with self.assertRaisesRegex(Error, "final text"):
            self.guard.accept(prepared["batch_id"], receipt)

    def test_frequency_retention_requires_reason_does_not_change_hash_or_count(self):
        prepared = self.guard.prepare(self.edits())
        self.guard.apply(prepared["batch_id"])
        receipt = self.receipt(prepared)
        receipt["checks"]["frequency"]["status"] = "RETAINED"
        with self.assertRaisesRegex(Error, "specific reason"):
            self.guard.accept(prepared["batch_id"], receipt)
        receipt["checks"]["frequency"]["reason"] = "See the occurrence-specific and overall-density discussion in evidence"
        self.assertEqual(self.guard.accept(prepared["batch_id"], receipt)["status"], "ACCEPTED")
        self.assertEqual(self.guard.accept(prepared["batch_id"], receipt)["status"], "ACCEPTED")
        with self.assertRaisesRegex(Error, "reviewed reversal"):
            self.guard.rollback(prepared["batch_id"])

    def test_mapping_cannot_be_skipped_when_required(self):
        other = Guard(self.root, "agent/audits/mapped-session")
        other.snapshot(dict(self.snapshot_spec, mapping_required=True))
        prepared = other.prepare(self.edits())
        other.apply(prepared["batch_id"])
        receipt = self.receipt(prepared)
        with self.assertRaisesRegex(Error, "mapping"):
            other.accept(prepared["batch_id"], receipt)
        receipt["checks"]["mapping"]["status"] = "PASS"
        (self.root / "mapping.json").write_text("{}", encoding="utf-8")
        (self.root / "published.md").write_text("发布正文", encoding="utf-8")
        receipt["checks"]["mapping"]["artifacts"] = {
            name: digest((self.root / name).read_bytes()) for name in ["mapping.json", "published.md"]}
        (self.root / "published.md").write_text("另一个版本", encoding="utf-8")
        with self.assertRaisesRegex(Error, "artifact hash"):
            other.accept(prepared["batch_id"], receipt)
        (self.root / "published.md").write_text("发布正文", encoding="utf-8")
        self.assertEqual(other.accept(prepared["batch_id"], receipt)["status"], "ACCEPTED")
        (self.root / "published.md").write_text("下一轮生成的发布版本", encoding="utf-8")
        self.assertEqual(other.load_latest()[0]["state"], "ACCEPTED")
        self.assertEqual(other.blob(receipt["checks"]["mapping"]["artifacts"]["published.md"]),
                         "发布正文".encode("utf-8"))

    def test_receipt_mutation_and_latest_history_are_detected(self):
        first = self.guard.prepare(self.edits())
        self.guard.apply(first["batch_id"])
        receipt = self.receipt(first)
        self.guard.accept(first["batch_id"], receipt)
        saved_latest = self.guard.internal("latest.json").read_bytes()
        directory, _, _, _ = self.guard.load_batch(first["batch_id"])
        stored_receipt = (directory / "receipt.json").read_bytes()
        value = json.loads(stored_receipt)
        value["payload"]["checks"]["semantics"]["status"] = "FAIL"
        (directory / "receipt.json").write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(Error, "integrity"):
            self.guard.load_latest()
        (directory / "receipt.json").write_bytes(stored_receipt)
        spec = self.edits(two=True)
        spec["files"] = spec["files"][1:]
        second = self.guard.prepare(spec)
        self.guard.apply(second["batch_id"])
        self.guard.accept(second["batch_id"], self.receipt(second))
        previous = self.guard.internal("latest-history/" + second["latest_manifest_sha256"] + ".json")
        self.assertEqual(previous.read_bytes(), saved_latest)
        latest, _ = self.guard.load_latest()
        self.assertEqual(latest["accepted_batch"], second["batch_id"])

    def test_manifest_tamper_and_session_lock_are_rejected(self):
        prepared = self.guard.prepare(self.edits())
        directory, _, _, _ = self.guard.load_batch(prepared["batch_id"])
        value = json.loads((directory / "manifest.json").read_text())
        value["payload"]["files"][0]["edits"][0]["new"] = "unauthorized"
        (directory / "manifest.json").write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(Error, "integrity"):
            self.guard.apply(prepared["batch_id"])
        with self.guard.locked():
            with self.assertRaisesRegex(Error, "lock"):
                self.guard.prepare(self.edits())

    def test_accept_recovers_after_latest_write_before_journal(self):
        prepared = self.guard.prepare(self.edits())
        self.guard.apply(prepared["batch_id"])
        receipt = self.receipt(prepared)
        with mock.patch.object(self.guard, "save_journal", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.guard.accept(prepared["batch_id"], receipt)
        self.assertEqual(self.guard.accept(prepared["batch_id"], receipt)["status"], "ACCEPTED")

    def test_stale_latest_rejects_prepared_batch(self):
        first = self.guard.prepare(self.edits())
        second = self.guard.prepare(self.edits(two=True))
        self.guard.apply(first["batch_id"])
        self.guard.accept(first["batch_id"], self.receipt(first))
        with self.assertRaisesRegex(Error, "baseline changed"):
            self.guard.apply(second["batch_id"])

    def test_old_unaccepted_batch_cannot_rollback_new_acceptance(self):
        first = self.guard.prepare(self.edits(two=True))
        self.guard.apply(first["batch_id"])
        path = self.root / "manuscript/one.md"
        second = self.guard.prepare({"schema_version": 1, "files": [{
            "path": "manuscript/one.md", "sha256": digest(path.read_bytes()),
            "allowed_ranges": [[0, len(path.read_text())]],
            "edits": [{"old": "门敞着", "new": "门还开着"}]}]})
        self.guard.apply(second["batch_id"])
        self.guard.accept(second["batch_id"], self.receipt(second))
        with self.assertRaisesRegex(Error, "baseline changed"):
            self.guard.rollback(first["batch_id"])
        self.assertEqual(self.guard.verify(second["batch_id"])["files"], second["files"])

    def test_path_and_project_isolation(self):
        with self.assertRaisesRegex(Error, "relative"):
            Guard(self.root, "../outside")
        (self.root / "alias").symlink_to(self.root / "manuscript", target_is_directory=True)
        spec = self.edits()
        spec["files"][0]["path"] = "alias/one.md"
        with self.assertRaisesRegex(Error, "outside frozen"):
            self.guard.prepare(spec)
        guard = Guard(self.root, "agent/audits/alias-session")
        with self.assertRaisesRegex(Error, "symlink"):
            guard.snapshot({"schema_version": 1, "files": ["alias/one.md"], "mapping_required": False})
        other = self.root / "other-project"
        other.mkdir()
        other_guard = Guard(other, "session")
        other_guard.session.mkdir()
        for item in ["original.json", "latest.json"]:
            (other_guard.session / item).write_bytes((self.guard.session / item).read_bytes())
        with self.assertRaisesRegex(Error, "another project"):
            other_guard.load_original()

    def test_unversioned_baseline_rejected_and_verification_is_read_only(self):
        other = Guard(self.root, "agent/audits/bad-baseline")
        with self.assertRaisesRegex(Error, "immutable"):
            other.snapshot(dict(self.snapshot_spec, baseline_commit="HEAD"))
        prepared = self.guard.prepare(self.edits())
        self.guard.apply(prepared["batch_id"])
        before = {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.guard.verify(prepared["batch_id"])
        after = {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_cli_json_and_help(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        prepared = self.guard.prepare(self.edits())
        result = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(self.root),
                                 "--session", "agent/audits/session", "apply", "--batch", prepared["batch_id"]],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "APPLIED")


if __name__ == "__main__":
    unittest.main()
