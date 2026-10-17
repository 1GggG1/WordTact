import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("analysis", Path(__file__).resolve().parents[1] / "analyze.py")
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


class AnalysisTests(unittest.TestCase):
    def test_order_average_fidelity_union_and_quote_audit(self):
        records = [{"key": "job", "case_id": "C01", "model": "model", "method": "project",
                    "checks": {"hard_failures": []}, "elapsed_seconds": 12,
                    "usage": {"input_tokens": 10, "output_tokens": 2}}]
        mapping = {"C01": {"keys": {"job": "T1"}}}
        judgments = []
        for order, score, fidelity in (("forward", 4, "pass"), ("reverse", 6, "major")):
            judgments.append({"case_id": "C01", "order": order,
                "input": {"task": {"request": "task", "context": "", "source": "original"},
                          "candidates": [{"id": "T1", "text": "candidate"}]},
                "judgment": {"candidates": [{"id": "T1", **{k: score for k in analysis.DIMENSIONS},
                             "fidelity": fidelity, "issues": [] if fidelity == "pass" else [
                                 {"candidate_quote": "wrong quote", "source_quote": "original", "severity": "major", "reason": "test"}]}]}})
        pairs = {"pair": {"model": "model", "case_id": "C01", "control": "bare", "language_quality": "tie",
                          "usable_overall": "loss", "orders": {
                              "forward": {"language_quality": "win", "usable_overall": "loss"},
                              "reverse": {"language_quality": "loss", "usable_overall": "loss"}}}}
        result = analysis.analyze(records, judgments, mapping, pairs)
        group = result["groups"]["model|general|project"]
        self.assertEqual(group["mean_quality"]["voice"], 5)
        self.assertEqual(group["worst_fidelity_counts"], {"major": 1})
        self.assertEqual(group["both_fidelity_pass"], 0)
        self.assertEqual(group["fidelity_order_disagreements"], 1)
        self.assertEqual(group["tokens"]["input_tokens"], 10)
        self.assertEqual(len(result["quote_audit_flags"]), 1)
        self.assertEqual(result["per_case_pairs"]["model|C01|bare"]["language_quality"]["order_disagreements"], 1)


if __name__ == "__main__":
    unittest.main()
