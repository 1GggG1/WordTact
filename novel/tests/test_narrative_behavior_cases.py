from __future__ import annotations

import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "narrative_behavior_cases.yaml"


class NarrativeBehaviorCaseTests(unittest.TestCase):
    def test_all_eight_acceptance_scenarios_have_enforced_contract_markers(self) -> None:
        payload = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(len(cases), 8)
        self.assertEqual(
            {case["id"] for case in cases},
            {
                "quiet_breakfast",
                "information_dialogue",
                "years_fast_forward",
                "documentary_form",
                "functional_sensory_density",
                "character_contradiction",
                "recurring_object",
                "reader_prescription",
            },
        )

        for case in cases:
            with self.subTest(case=case["id"]):
                source = (REPO / case["source"]).resolve()
                self.assertTrue(source.is_relative_to(REPO.resolve()))
                text = source.read_text(encoding="utf-8")
                self.assertTrue(case["scenario"].strip())
                self.assertTrue(case["expected"].strip())
                for marker in case["markers"]:
                    self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
