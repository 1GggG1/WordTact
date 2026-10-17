"""Evidence contracts; these tests do not call models or grade prose."""
import copy
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("nine_case", Path(__file__).resolve().parents[1] / "benchmark.py")
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)


class BenchmarkTests(unittest.TestCase):
    def test_fixed_schedule_and_no_humanizer_generation(self):
        cases = bench.load_cases()
        tasks = bench.tasks(cases)
        self.assertEqual(len(tasks), 156)
        self.assertEqual(len({t["key"] for t in tasks}), 156)
        self.assertEqual(tasks, bench.tasks(cases))
        self.assertFalse(any(t["case_id"] == "F01" and t["method"] == "humanizer" for t in tasks))
        for model in bench.MODELS:
            self.assertEqual(sum(t["model"] == model for t in tasks), 78)

    def test_only_task_material_reaches_worker(self):
        for case in bench.load_cases():
            exposed = bench.public_case(case)
            self.assertNotIn("provenance", exposed)
            self.assertNotIn("constraints", exposed)
            self.assertNotIn("product", exposed)
            self.assertEqual(exposed["source"], case["source"])

    def test_explicit_standard_max_and_no_speed_inheritance(self):
        for model in (*bench.MODELS, "gpt-6-astra"):
            cmd = bench.cli_command(model, Path("work"), Path("output"))
            self.assertIn('--ignore-user-config', cmd)
            self.assertIn('service_tier="default"', cmd)
            self.assertIn('model_reasoning_effort="max"', cmd)
            self.assertEqual(cmd[cmd.index("-m") + 1], model)
            for feature in ("fast_mode", "ultrafast_mode", "multi_agent"):
                self.assertEqual(cmd[cmd.index(feature) - 1], "--disable")

    def test_han_limits_and_protected_content(self):
        cases = {c["id"]: c for c in bench.load_cases()}
        self.assertIn("han_below_minimum", bench.check_text(cases["F01"], "字" * 499)["hard_failures"])
        self.assertEqual(bench.check_text(cases["F01"], "字" * 500)["hard_failures"], [])
        self.assertIn("han_above_maximum", bench.check_text(cases["F01"], "字" * 751)["hard_failures"])
        self.assertEqual(bench.check_text(cases["C02"], cases["C02"]["source"])["hard_failures"], [])
        broken = cases["C02"]["source"].replace("week=42", "week=43")
        self.assertTrue(bench.check_text(cases["C02"], broken)["hard_failures"])
        diagnostic = bench.check_text(cases["C01"], "数字另用等价写法")
        self.assertEqual(diagnostic["hard_failures"], [])
        self.assertTrue(diagnostic["missing_literal_diagnostics"])

    def valid_judgment(self):
        payload = {"candidates": [{"id": "T1"}], "pairs": [{"id": "P1"}]}
        value = {"candidates": [{"id": "T1", "naturalness": 4, "voice": 5, "craft": 4,
                  "economy": 4, "fidelity": "pass", "issues": [], "reason": "Evidence"}],
                 "pairs": [{"id": "P1", "language_quality": "tie", "usable_overall": "tie", "reason": "Equal"}]}
        return payload, value

    def test_complete_unique_judgment_ids_required(self):
        payload, value = self.valid_judgment()
        bench.validate_judgment(payload, value)
        for mutate in (lambda v: v["candidates"].clear(),
                       lambda v: v["pairs"].append(copy.deepcopy(v["pairs"][0])),
                       lambda v: v["candidates"][0].update(id="other"),
                       lambda v: v["candidates"][0].update(voice=8),
                       lambda v: v["candidates"][0].update(voice=True),
                       lambda v: v["pairs"][0].update(usable_overall="maybe")):
            broken = copy.deepcopy(value)
            mutate(broken)
            with self.assertRaises(ValueError):
                bench.validate_judgment(payload, broken)

    def test_pair_position_is_decoded_and_disagreement_is_tie(self):
        forward = {"left": "project", "right": "control"}
        reverse = {"left": "control", "right": "project"}
        self.assertEqual(bench.pair_outcome(forward, {"quality": "left"}, "project", "quality"), "win")
        self.assertEqual(bench.pair_outcome(reverse, {"quality": "right"}, "project", "quality"), "win")
        self.assertEqual(bench.pair_outcome(reverse, {"quality": "left"}, "project", "quality"), "loss")
        self.assertEqual(bench.merge_orders("win", "win"), "win")
        self.assertEqual(bench.merge_orders("win", "loss"), "tie")
        self.assertEqual(bench.merge_orders("win", "tie"), "tie")
        self.assertEqual(bench.pair_outcome({"left": "x", "right": "x"}, {"quality": "left"}, "x", "quality"), "tie")

    def test_lock_rejects_later_input_or_snapshot_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "suite"
            evidence = Path(temp) / "evidence"
            for case in bench.load_cases():
                bench.write_json(root / "cases" / (case["id"] + ".json"), case)
            (root / "rubric.md").write_text("rubric")
            (evidence / "snapshots").mkdir(parents=True)
            sample = evidence / "snapshots" / "skill.md"
            sample.write_text("original")
            with patch.object(bench, "ROOT", root):
                original = bench.freeze(evidence)
                self.assertEqual(original, bench.freeze(evidence))
                sample.write_text("changed")
                with self.assertRaises(ValueError):
                    bench.freeze(evidence)
                sample.write_text("original")
                (root / "rubric.md").write_text("new rubric")
                with self.assertRaises(ValueError):
                    bench.freeze(evidence)

    def test_record_matches_saved_candidate_task_prompt_and_command(self):
        case = bench.load_cases()[0]
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            bench.write_json(folder / "workspace" / "case.json", bench.public_case(case))
            (folder / "candidate.txt").write_text("answer\n")
            prompt = bench.generation_prompt("bare")
            (folder / "prompt.txt").write_text(prompt)
            bench.write_json(folder / "command.json", bench.cli_command(bench.MODELS[0], folder / "workspace", folder / "candidate.txt"))
            record = {"method": "bare", "model": bench.MODELS[0], "text": "answer",
                      "text_sha256": bench.digest(b"answer"), "prompt_sha256": bench.digest(prompt.encode()),
                      "case_sha256": bench.digest((folder / "workspace" / "case.json").read_bytes())}
            bench.verify_record(folder, record, case)
            (folder / "candidate.txt").write_text("improved after seeing scores")
            with self.assertRaises(ValueError):
                bench.verify_record(folder, record, case)

    def test_public_metadata_drops_local_tools_and_thread_ids(self):
        original = {"key": "job", "thread_id": "private", "tool_calls": [{"command": "/private/path"}], "usage": {"input_tokens": 3}}
        exposed = bench.public_metadata(original)
        self.assertEqual(exposed, {"key": "job", "usage": {"input_tokens": 3}})

    def test_mocked_end_to_end_keeps_all_pairs_and_both_orders(self):
        def fake_execute(cmd, prompt, folder, timeout):
            (folder / "prompt.txt").write_text(prompt)
            bench.write_json(folder / "command.json", cmd)
            output = Path(cmd[cmd.index("-o") + 1])
            if "--output-schema" in cmd:
                payload = bench.read_json(folder / "workspace" / "input.json")
                bench.write_json(output, {
                    "candidates": [{"id": c["id"], "naturalness": 4, "voice": 4, "craft": 4,
                                    "economy": 4, "fidelity": "pass", "issues": [], "reason": "test"}
                                   for c in payload["candidates"]],
                    "pairs": [{"id": p["id"], "language_quality": "left", "usable_overall": "left", "reason": "test"}
                              for p in payload["pairs"]]})
            else:
                output.write_text("fixed test candidate")
            return {"exit_code": 0, "elapsed_seconds": 0, "prompt_sha256": bench.digest(prompt.encode()),
                    "status": "transport_failure", "usage": {}, "tool_calls": []}

        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "evidence"
            for name in ("project_novel", "project_general", "humanizer_zh", "humanizer_en"):
                directory = evidence / "snapshots" / name
                directory.mkdir(parents=True)
                (directory / "SKILL.md").write_text("test")
            bench.freeze(evidence)
            cases = {c["id"]: c for c in bench.load_cases()}
            with patch.object(bench, "execute", fake_execute):
                for task in bench.tasks(list(cases.values())):
                    bench.generate_one(task, cases[task["case_id"]], evidence, 1)
                jobs = bench.prepare_judges(evidence)
                self.assertEqual(len(jobs), 18)
                for job in jobs:
                    self.assertEqual(bench.judge_one(job, evidence, 1)["status"], "ok")
            destination = Path(temp) / "public"
            with contextlib.redirect_stdout(io.StringIO()):
                bench.export(evidence, destination)
            self.assertEqual(len(bench.read_json(destination / "generations.json")), 156)
            self.assertEqual(len(bench.read_json(destination / "judgments.json")), 18)
            pairs = bench.read_json(destination / "pairs.json")
            self.assertEqual(len(pairs), 150)
            # A judge that always chooses the left side must never create a win.
            self.assertTrue(all(p["usable_overall"] == "tie" for p in pairs.values()))


if __name__ == "__main__":
    unittest.main()
