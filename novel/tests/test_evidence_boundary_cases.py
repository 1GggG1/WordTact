"""Validate trial inputs and their isolation; model judgments need forward evaluation."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidence_boundary_cases import FIXTURE, materialize


class EvidenceBoundaryCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.expected = json.loads(
            FIXTURE.with_name("expectations.json").read_text(encoding="utf-8")
        )

    def test_answer_keys_cover_cases_and_cite_actual_prose(self) -> None:
        for group in ("audit_cases", "writing_cases"):
            cases = self.inputs[group]
            ids = [case["id"] for case in cases]
            self.assertTrue(ids)
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(set(ids), set(self.expected[group]))
        for case in self.inputs["audit_cases"]:
            expectation = self.expected["audit_cases"][case["id"]]
            with self.subTest(case=case["id"]):
                self.assertTrue(expectation["anchors"])
                for anchor in expectation["anchors"]:
                    self.assertIn(anchor, case["prose"])

    def test_paired_contexts_keep_prose_and_narrative_contract_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            brief, expanded = (Path(directory) / name for name in ("brief", "expanded"))
            materialize(brief, "brief")
            materialize(expanded, "expanded")
            for case in self.inputs["audit_cases"]:
                with self.subTest(case=case["id"]):
                    relative = Path("audits") / case["id"]
                    self.assertEqual(
                        (brief / relative / "prose.md").read_bytes(),
                        (expanded / relative / "prose.md").read_bytes(),
                    )
                    short = (brief / relative / "context.md").read_text(encoding="utf-8")
                    long = (expanded / relative / "context.md").read_text(encoding="utf-8")
                    self.assertNotEqual(short, long)
                    self.assertEqual(short.split("# 项目资料")[0], long.split("# 项目资料")[0])

    def test_materialized_inputs_exclude_criteria_and_match_recorded_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            hashes = materialize(output, "expanded")
            allowed = {"audit-request.txt", "writing-request.txt", "input-hashes.json"}
            for case in self.inputs["audit_cases"]:
                allowed.update(f"audits/{case['id']}/{name}" for name in ("prose.md", "context.md"))
            for case in self.inputs["writing_cases"]:
                allowed.add(f"writers/{case['id']}/brief.md")
                self.assertEqual(
                    (output / f"writers/{case['id']}/brief.md").read_text(encoding="utf-8"),
                    case["brief"] + "\n",
                )
            actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
            self.assertEqual(actual, allowed)
            self.assertEqual(set(hashes), allowed - {"input-hashes.json"})
            for relative, digest in hashes.items():
                self.assertEqual(hashlib.sha256((output / relative).read_bytes()).hexdigest(), digest)

    def test_existing_trial_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            hashes = materialize(output, "brief")
            with self.assertRaises(FileExistsError):
                materialize(output, "expanded")
            for relative, digest in hashes.items():
                self.assertEqual(hashlib.sha256((output / relative).read_bytes()).hexdigest(), digest)
            invalid = Path(directory) / "invalid"
            with self.assertRaises(ValueError):
                materialize(invalid, "unknown")
            self.assertFalse(invalid.exists())


if __name__ == "__main__":
    unittest.main()
