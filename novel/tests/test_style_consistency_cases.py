"""Check reproducible trial inputs, not literary quality or generated wording."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import style_consistency_cases as trial


class StyleConsistencyCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = json.loads(trial.FIXTURE.read_text(encoding="utf-8"))
        self.expected = json.loads(
            trial.FIXTURE.with_name("expectations.json").read_text(encoding="utf-8")
        )

    def test_criteria_cover_cases_and_cite_original_text(self) -> None:
        cases = self.inputs["cases"]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(self.expected))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIn(case["mode"], {"audit", "writing"})
                self.assertTrue(case["context"].strip())
                self.assertTrue(case["request"].strip())
                self.assertTrue(self.expected[case["id"]]["criteria"])
                if case["mode"] == "audit":
                    anchors = self.expected[case["id"]]["anchors"]
                    self.assertTrue(anchors)
                    for anchor in anchors:
                        self.assertIn(anchor, case["prose"])

    def test_variants_differ_only_in_optional_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            a, b, c = (Path(directory) / name for name in ("a", "b", "c"))
            plain = trial.materialize(a, "plain")
            guided = trial.materialize(b, "guided")
            replica = trial.materialize(c, "guided")
            self.assertEqual(guided, replica)
            extra = set(guided) - set(plain)
            self.assertTrue(extra)
            self.assertTrue(all(Path(name).name == "style.md" for name in extra))
            self.assertEqual({name: digest for name, digest in guided.items() if name not in extra}, plain)

    def test_inputs_have_bound_hashes_and_no_evaluator_criteria(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            hashes = trial.materialize(root, "guided")
            files = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(files, set(hashes) | {"input-hashes.json"})
            self.assertEqual(json.loads((root / "input-hashes.json").read_text()), hashes)
            for name, digest in hashes.items():
                raw = (root / name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                for expected in self.expected.values():
                    for criterion in expected["criteria"]:
                        self.assertNotIn(criterion, raw.decode("utf-8"))

    def test_stale_sample_has_real_mismatched_digest_without_old_text(self) -> None:
        case = next(case for case in self.inputs["cases"] if case.get("stale_sample"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            trial.materialize(root, "guided")
            folder = root / "cases" / case["id"]
            record = json.loads((folder / "sample-record.json").read_text())
            old = case["stale_sample"]["approved_text"]
            self.assertEqual(record["sha256"], hashlib.sha256((old + "\n").encode()).hexdigest())
            self.assertNotEqual(record["sha256"], hashlib.sha256((folder / record["path"]).read_bytes()).hexdigest())
            for path in root.rglob("*"):
                if path.is_file():
                    self.assertNotIn(old, path.read_text(encoding="utf-8"))

    def test_invalid_context_and_existing_trial_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            hashes = trial.materialize(root, "plain")
            with self.assertRaises(FileExistsError):
                trial.materialize(root, "guided")
            for name, digest in hashes.items():
                self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), digest)
            invalid = Path(directory) / "invalid"
            with self.assertRaises(ValueError):
                trial.materialize(invalid, "unknown")
            self.assertFalse(invalid.exists())

    def test_escaping_input_path_fails_before_any_trial_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "malformed.json"
            self.inputs["cases"][0]["sources"] = {"../../../escape.md": "outside"}
            fixture.write_text(json.dumps(self.inputs), encoding="utf-8")
            root = Path(directory) / "run"
            with mock.patch.object(trial, "FIXTURE", fixture):
                with self.assertRaises(ValueError):
                    trial.materialize(root, "guided")
            self.assertFalse(root.exists())
            self.assertFalse((Path(directory) / "escape.md").exists())


if __name__ == "__main__":
    unittest.main()
