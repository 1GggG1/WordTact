"""Filesystem integration tests for provenance, invalidation and atomic index updates."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "user/novel-ci/scripts/reader_index.py"
SPEC = importlib.util.spec_from_file_location("reader_index", SCRIPT)
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)


def sha(value):
    return hashlib.sha256(value).hexdigest()


class ReaderIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="reader-index-")
        self.root = Path(self.temp.name)
        self.write("a.md", "甲说：“桥还没有开放。”\n")
        self.write("b.md", "乙猜测今晚可能有人过桥。\n")
        self.write("c.md", "丙其实保留着钥匙。\n")
        self.write("acceptance.md", "作者已接受本次正文。\n")
        self.write("decisions.md", "保留人物的不确定判断。\n")
        self.manifest = {"schema_version": 1, "units": [
            {"unit_id": uid, "path": uid + ".md", "complete_chapter": True}
            for uid in ("a", "b", "c")]}
        self.save_manifest()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))

    def save_manifest(self):
        self.write("reading.json", json.dumps(self.manifest, ensure_ascii=False, indent=2))

    def reference(self):
        return {"path": "reading.json", "sha256": sha((self.root / "reading.json").read_bytes())}

    def anchor(self, path):
        raw = (self.root / path).read_bytes()
        text = raw.decode("utf-8")
        return {"path": path, "sha256": sha(raw), "start": 0, "end": len(text), "quote": text}

    def snapshot(self, span):
        raw = (self.root / span["path"]).read_bytes()
        text = raw.decode("utf-8")
        return dict(span, sha256=sha(raw), slice_sha256=sha(text[span["start"]:span["end"]].encode("utf-8")))

    def unit(self, uid, revision=0):
        manifest, _ = reader.load_manifest(self.root, self.reference(), exact_hash=True)
        definition = next(item for item in manifest["units"] if item["unit_id"] == uid)
        slices = [self.snapshot(item) for item in definition["reading"]]
        content = "".join((self.root / item["path"]).read_bytes().decode("utf-8")[item["start"]:item["end"]]
                          for item in slices)
        first = slices[0]
        quote = (self.root / first["path"]).read_bytes().decode("utf-8")[first["start"]:first["end"]]
        return {"unit_id": uid, "reading": slices,
                "canonical": [self.snapshot(item) for item in definition.get("canonical", [])],
                "acceptance": {"status": "accepted", "content_sha256": sha(content.encode("utf-8")),
                               "evidence": self.anchor("acceptance.md")},
                "review": {"base_revision": revision, "confirmed": True},
                "disclosures": [{"id": "disclosure-" + uid, "summary": "本单元披露：" + quote,
                                 "epistemic": "inference", "speaker": "叙述者", "pov": "甲",
                                 "first_in": uid, "anchors": [{"slice": 0, "start": first["start"],
                                                               "end": first["end"], "quote": quote}]}],
                "protected": [{"reason": "保留推测强度", "source": self.anchor("decisions.md")}]}

    def candidate(self, units=("a", "b", "c"), revision=0):
        return {"schema_version": 1, "expected_revision": revision, "manifest": self.reference(),
                "units": [self.unit(uid, revision) for uid in units]}

    def commit(self, units=("a", "b", "c"), revision=0):
        return reader.commit(self.root, self.candidate(units, revision))

    def index_bytes(self):
        return (self.root / reader.DEFAULT_INDEX).read_bytes()

    def test_uninitialized_read_only_status_does_not_create_directories(self):
        before = sorted(str(p) for p in self.root.rglob("*"))
        self.assertEqual(reader.status(self.root)["state"], "UNINITIALIZED")
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob("*")))

    def test_full_commit_prefix_query_and_read_only_status(self):
        self.assertEqual(self.commit()["coverage"]["state"], "VALID")
        before = self.index_bytes()
        context = reader.context(self.root, "c")
        self.assertEqual([unit["unit_id"] for unit in context["units"]], ["a", "b"])
        self.assertNotIn("保留着钥匙", json.dumps(context, ensure_ascii=False))
        self.assertEqual(reader.context(self.root, "a")["units"], [])
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a", "b", "c"])
        self.assertEqual(before, self.index_bytes())

    def test_partial_prefix_and_incremental_extension(self):
        self.commit(("a",))
        report = reader.context(self.root, "c")
        self.assertEqual(report["uncovered_before_target"], ["b"])
        self.assertEqual(report["state"], "NEEDS_VERIFICATION")
        self.commit(("b", "c"), 1)
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a", "b", "c"])

    def test_gap_cannot_be_committed(self):
        with self.assertRaisesRegex(reader.IndexValidationError, "coverage gap"):
            self.commit(("a", "c"))
        self.assertFalse((self.root / reader.DEFAULT_INDEX).exists())

    def test_stale_source_invalidates_suffix_and_requires_explicit_rereview(self):
        self.commit()
        self.write("b.md", "乙猜测今晚也许有人过桥。\n")
        before = self.index_bytes()
        report = reader.status(self.root)
        self.assertEqual(report["valid_prefix"], ["a"])
        self.assertEqual(report["invalidated"], ["b", "c"])
        self.assertEqual(before, self.index_bytes())
        self.commit(("b",), 1)
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a", "b"])
        self.assertEqual(reader.status(self.root)["missing"], ["c"])

    def test_changed_source_cannot_be_restored_by_updating_hashes_only(self):
        stale = self.candidate()
        self.commit()
        self.write("b.md", "乙确认今晚一定有人过桥。\n")
        stale["expected_revision"] = 1
        stale["units"][1]["reading"][0] = self.unit("b", 1)["reading"][0]
        with self.assertRaises(reader.IndexValidationError):
            reader.commit(self.root, stale)

    def test_reinterpreting_unchanged_earlier_unit_drops_unreviewed_suffix(self):
        self.commit()
        candidate = self.candidate(("a",), 1)
        candidate["units"][0]["disclosures"][0]["epistemic"] = "assertion"
        reader.commit(self.root, candidate)
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a"])

    def test_source_deleted_preserves_earlier_prefix(self):
        self.commit()
        (self.root / "b.md").unlink()
        report = reader.status(self.root)
        self.assertEqual(report["valid_prefix"], ["a"])
        self.assertEqual(report["invalidated"], ["b", "c"])

    def test_reordered_manifest_invalidates_from_first_moved_unit(self):
        self.commit()
        self.manifest["units"][1:] = list(reversed(self.manifest["units"][1:]))
        self.save_manifest()
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a"])
        self.assertEqual(reader.context(self.root, "b")["uncovered_before_target"], ["c"])
        self.commit(("c", "b"), 1)
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a", "c", "b"])

    def test_deleted_reading_unit_is_removed_on_next_commit(self):
        self.commit()
        self.manifest["units"].pop(1)
        self.save_manifest()
        self.assertEqual(reader.status(self.root)["invalidated"], ["b", "c"])
        self.commit(("c",), 1)
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a", "c"])

    def test_append_reading_unit_keeps_old_prefix(self):
        self.commit()
        self.write("d.md", "丁关上了门。\n")
        self.manifest["units"].append({"unit_id": "d", "path": "d.md", "complete_chapter": True})
        self.save_manifest()
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a", "b", "c"])
        self.commit(("d",), 1)
        self.assertEqual(reader.status(self.root)["state"], "VALID")

    def test_quote_outside_slice_or_mismatch_rejected(self):
        for change in ({"end": 999}, {"quote": "伪造原文"}):
            candidate = self.candidate(("a",))
            candidate["units"][0]["disclosures"][0]["anchors"][0].update(change)
            with self.subTest(change=change), self.assertRaises(reader.IndexValidationError):
                reader.commit(self.root, candidate)

    def test_future_first_occurrence_is_rejected(self):
        candidate = self.candidate()
        candidate["units"][0]["disclosures"][0]["first_in"] = "c"
        with self.assertRaisesRegex(reader.IndexValidationError, "future unit"):
            reader.commit(self.root, candidate)

    def test_repeated_disclosure_preserves_first_occurrence(self):
        candidate = self.candidate()
        candidate["units"][1]["disclosures"][0].update(id="disclosure-a", first_in="a")
        reader.commit(self.root, candidate)
        self.assertEqual(reader.context(self.root, "c")["units"][1]["disclosures"][0]["first_in"], "a")

    def test_context_does_not_expose_editorial_report_spoilers(self):
        self.write("acceptance.md", "接受第一章。另：第三章揭露钥匙持有人。\n")
        self.commit()
        payload = json.dumps(reader.context(self.root, "b"), ensure_ascii=False)
        self.assertNotIn("第三章揭露", payload)
        self.assertNotIn("acceptance", payload)

    def test_second_writer_with_same_revision_cannot_overwrite_first(self):
        self.commit(("a",))
        first = self.candidate(("b",), 1)
        second = self.candidate(("b", "c"), 1)
        reader.commit(self.root, first)
        before = self.index_bytes()
        with self.assertRaisesRegex(reader.IndexValidationError, "expected_revision"):
            reader.commit(self.root, second)
        self.assertEqual(before, self.index_bytes())

    def test_manifest_hash_and_duplicate_candidate_are_rejected(self):
        candidate = self.candidate(("a",))
        candidate["manifest"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(reader.IndexValidationError, "manifest hash"):
            reader.commit(self.root, candidate)
        candidate = self.candidate(("a",))
        candidate["units"].append(copy.deepcopy(candidate["units"][0]))
        with self.assertRaisesRegex(reader.IndexValidationError, "duplicate candidate"):
            reader.commit(self.root, candidate)

    def test_reformatted_manifest_does_not_invalidate_semantically_identical_plan(self):
        self.commit()
        self.write("reading.json", json.dumps(self.manifest, separators=(",", ":")))
        self.assertEqual(reader.status(self.root)["state"], "VALID")

    def test_acceptance_review_and_protection_are_validated(self):
        mutations = [lambda u: u["acceptance"].update(status="draft"),
                     lambda u: u["acceptance"].update(content_sha256="0" * 64),
                     lambda u: u["review"].update(confirmed=False),
                     lambda u: u["review"].update(base_revision=7),
                     lambda u: u["protected"][0]["source"].update(quote="伪造决定"),
                     lambda u: u["acceptance"]["evidence"].update(sha256="0" * 64)]
        for number, mutate in enumerate(mutations):
            candidate = self.candidate(("a",))
            mutate(candidate["units"][0])
            with self.subTest(number=number), self.assertRaises(reader.IndexValidationError):
                reader.commit(self.root, candidate)

    def test_appended_acceptance_revocation_invalidates_unchanged_quote(self):
        original_candidate = self.candidate()
        reader.commit(self.root, original_candidate)
        self.write("acceptance.md", "作者已接受本次正文。\n更正：本次接受已撤回，须重新检查。\n")
        before = self.index_bytes()
        report = reader.status(self.root)
        self.assertEqual(report["state"], "NEEDS_VERIFICATION")
        self.assertEqual(report["valid_prefix"], [])
        self.assertEqual(report["invalidated"], ["a", "b", "c"])
        self.assertTrue(any("stale source evidence" in issue for issue in report["issues"]))
        self.assertEqual(reader.context(self.root, "c")["units"], [])
        with self.assertRaisesRegex(reader.IndexValidationError, "stale source"):
            reader.commit(self.root, original_candidate)
        self.assertEqual(self.index_bytes(), before)

    def test_changed_decision_evidence_cannot_be_silently_rehashed(self):
        self.commit()
        saved = reader.read_index(self.root)["units"][0]
        old_hash = saved["protected"][0]["source"]["sha256"]
        self.write("decisions.md", "保留人物的不确定判断。\n后续决定：上条只适用于另一场景。\n")
        report = reader.status(self.root)
        self.assertEqual(report["valid_prefix"], [])
        self.assertEqual(report["invalidated"], ["a", "b", "c"])
        refreshed = reader.refreshed_hashes(self.root, saved)
        self.assertEqual(refreshed["protected"][0]["source"]["sha256"], old_hash)
        with self.assertRaisesRegex(reader.IndexValidationError, "coverage gap"):
            self.commit(("c",), 1)

    def test_exact_retry_is_idempotent_but_stale_revision_is_not(self):
        candidate = self.candidate(("a",))
        reader.commit(self.root, candidate)
        before = self.index_bytes()
        self.assertTrue(reader.commit(self.root, candidate)["idempotent"])
        self.assertEqual(before, self.index_bytes())
        with self.assertRaisesRegex(reader.IndexValidationError, "expected_revision"):
            self.commit(("b",), 0)
        self.write("a.md", "甲改口了。\n")
        with self.assertRaisesRegex(reader.IndexValidationError, "stale source"):
            reader.commit(self.root, candidate)

    def test_existing_writer_lock_is_not_removed(self):
        target = self.root / reader.DEFAULT_INDEX
        target.parent.mkdir(parents=True)
        lock = Path(str(target) + ".lock")
        lock.write_text("other writer", encoding="utf-8")
        with self.assertRaisesRegex(reader.IndexValidationError, "locked"):
            self.commit()
        self.assertEqual(lock.read_text(), "other writer")

    def test_replace_failure_preserves_index_and_cleans_own_lock(self):
        self.commit(("a",))
        before = self.index_bytes()
        with mock.patch.object(reader.os, "replace", side_effect=OSError("simulated storage failure")):
            with self.assertRaisesRegex(OSError, "storage failure"):
                self.commit(("b",), 1)
        self.assertEqual(before, self.index_bytes())
        self.assertFalse(Path(str(self.root / reader.DEFAULT_INDEX) + ".lock").exists())
        self.assertEqual(list((self.root / reader.DEFAULT_INDEX).parent.glob("*.tmp")), [])

    def test_path_traversal_absolute_and_symlink_escape_rejected(self):
        for path in ("../outside.md", str(self.root / "a.md")):
            with self.subTest(path=path), self.assertRaises(reader.IndexValidationError):
                reader.rooted(self.root, path)
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(reader.IndexValidationError):
                reader.rooted(self.root, "escape/index.json")
        self.assertFalse((self.root / reader.DEFAULT_INDEX).exists())

    def test_duplicate_unit_or_source_alias_rejected(self):
        self.manifest["units"].append(copy.deepcopy(self.manifest["units"][0]))
        self.save_manifest()
        with self.assertRaisesRegex(reader.IndexValidationError, "unique"):
            reader.load_manifest(self.root, self.reference())
        self.manifest["units"].pop()
        (self.root / "alias.md").symlink_to(self.root / "a.md")
        self.manifest["units"][1]["path"] = "alias.md"
        self.save_manifest()
        with self.assertRaisesRegex(reader.IndexValidationError, "overlapping"):
            reader.load_manifest(self.root, self.reference())

    def mapped_manifest(self):
        self.write("logical.md", "甲打开门。乙走进来。")
        self.write("published-a.md", "甲打开门。")
        self.write("published-b.md", "乙走进来。")
        self.manifest = {"schema_version": 1, "units": [
            {"unit_id": "a", "reading": [{"path": "published-a.md", "start": 0, "end": 5}],
             "canonical": [{"path": "logical.md", "start": 0, "end": 5}]},
            {"unit_id": "b", "reading": [{"path": "published-b.md", "start": 0, "end": 5}],
             "canonical": [{"path": "logical.md", "start": 5, "end": 10}]}],
            "coverage": {"reading": [{"path": "published-a.md", "start": 0, "end": 5},
                                     {"path": "published-b.md", "start": 0, "end": 5}],
                         "canonical": [{"path": "logical.md", "start": 0, "end": 10}]}}
        self.save_manifest()

    def test_split_mapping_and_precise_slice_invalidation(self):
        self.mapped_manifest()
        self.commit(("a", "b"))
        self.write("logical.md", "甲打开门。乙跑进来。")
        self.write("published-b.md", "乙跑进来。")
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["a"])
        self.commit(("b",), 1)
        self.assertEqual(reader.status(self.root)["state"], "VALID")

    def test_context_refreshes_valid_slice_file_hash_without_writing_index(self):
        self.mapped_manifest()
        self.commit(("a", "b"))
        before = self.index_bytes()
        stored = json.loads(before)["units"][0]["canonical"][0]
        self.write("logical.md", "甲打开门。乙跑进来。")
        self.write("published-b.md", "乙跑进来。")
        response = reader.context(self.root, "b")
        self.assertEqual(response["valid_prefix"], ["a"])
        current = response["units"][0]["canonical"][0]
        self.assertNotEqual(current["sha256"], stored["sha256"])
        self.assertEqual(current["sha256"], sha((self.root / "logical.md").read_bytes()))
        self.assertEqual(current["slice_sha256"], stored["slice_sha256"])
        self.assertEqual(before, self.index_bytes())

    def test_mapping_gap_duplicate_and_out_of_order_fail(self):
        self.mapped_manifest()
        base = copy.deepcopy(self.manifest)
        variants = []
        gap = copy.deepcopy(base)
        gap["coverage"]["canonical"][0]["end"] = 9
        variants.append(gap)
        duplicate = copy.deepcopy(base)
        duplicate["units"][1]["canonical"] = copy.deepcopy(duplicate["units"][0]["canonical"])
        variants.append(duplicate)
        for number, variant in enumerate(variants):
            self.manifest = variant
            self.save_manifest()
            with self.subTest(number=number), self.assertRaises(reader.IndexValidationError):
                reader.load_manifest(self.root, self.reference())
        self.manifest = base
        self.manifest["units"] = [{"unit_id": "merged",
                                   "reading": base["coverage"]["reading"],
                                   "canonical": list(reversed([unit["canonical"][0] for unit in base["units"]]))}]
        self.save_manifest()
        with self.assertRaisesRegex(reader.IndexValidationError, "out of order"):
            reader.load_manifest(self.root, self.reference())

    def test_merge_mapping_requires_new_review_and_covers_both_sources(self):
        self.mapped_manifest()
        self.commit(("a", "b"))
        self.manifest["units"] = [{"unit_id": "merged", "reading": self.manifest["coverage"]["reading"],
                                   "canonical": self.manifest["coverage"]["canonical"]}]
        self.save_manifest()
        self.assertEqual(reader.status(self.root)["valid_prefix"], [])
        self.commit(("merged",), 1)
        self.assertEqual(reader.status(self.root)["valid_prefix"], ["merged"])

    def test_project_isolation_and_cli(self):
        self.commit(("a",))
        with tempfile.TemporaryDirectory() as other:
            self.assertEqual(reader.status(Path(other))["state"], "UNINITIALIZED")
        result = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(self.root),
                                 "context", "--before", "c"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["uncovered_before_target"], ["b"])
        missing = subprocess.run([sys.executable, str(SCRIPT), "status"], text=True,
                                 capture_output=True, check=False)
        self.assertNotEqual(missing.returncode, 0)


if __name__ == "__main__":
    unittest.main()
