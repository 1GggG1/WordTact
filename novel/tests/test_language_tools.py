from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "user" / "novel-auditor" / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


language = load("language_scan")
repeats = load("repeat_scan")


class LanguageToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.manifest = {"schema_version": 1, "units": []}
        self.profile = {
            "schema_version": 1, "profile_id": "sample", "revision": 1,
            "scope": "test prose", "calibration_sources": ["test fixture"],
            "categories": [{"id": "bian", "label": "便", "definition": "连接用法",
                            "forms": [{"kind": "literal", "value": "便"}],
                            "thresholds": {"chapter_at_least": 2}}],
        }

    def unit(self, text, uid="u1", complete=True):
        path = self.root / (uid + ".md")
        path.write_bytes(text.encode("utf-8"))
        self.manifest["units"].append({"unit_id": uid, "path": path.name, "complete_chapter": complete})
        return path

    def scan(self, protected=None):
        return language.scan(self.root, self.manifest, self.profile, protected)

    def decisions(self, report):
        result = copy.deepcopy(report["review_template"])
        for item in result["classifications"]:
            item.update(applies=True, reason="连接前后动作", action="retain")
        for item in result["unit_reviews"]:
            item.update(density_reviewed=True, punctuation_reviewed=True,
                        reason="已通读，除列出的类别外未发现新的集中表达")
        for item in result["density_reviews"]:
            item.update(decision="retain", reason="两次对应不同人物的有效条件回应，整章密度仍有作用")
        return result

    def recount(self, report, decisions, protected=None):
        return language.recount(self.root, report, decisions, self.profile, protected)

    def test_chinese_adjacent_decimal_version_and_model_protection(self):
        text = "镜头调到2.5倍，查看T-8型号。版本v2.1尚未升级。停...继续--走。"
        self.unit(text)
        report = self.scan()
        issues = report["punctuation"][0]["issues"]
        # Technical spans survive without needing a whole-sentence exemption;
        # malformed prose punctuation immediately afterwards is still reported.
        self.assertEqual([(item["text"], item["code"]) for item in issues],
                         [("...", "ellipsis_form"), ("--", "dash_form")])
        self.assertTrue(all(text[item["start"]:item["end"]] == item["text"] for item in issues))

    def test_raw_and_semantic_counts_are_separate_and_retention_does_not_subtract(self):
        self.unit("方便、随便、便宜、顺便。雨停便走，他答应便开门。")
        report = self.scan()
        self.assertEqual(report["raw_counts"][0]["raw_form_matches"], 6)
        decisions = self.decisions(report)
        for item in decisions["classifications"][:4]:
            item.update(applies=False, action="not_applicable", reason="属于词内成分，不是连接用法")
        true_ids = [item["id"] for item in decisions["classifications"] if item["applies"]]
        for item in decisions["density_reviews"]:
            item["occurrence_ids"] = true_ids
        result = self.recount(report, decisions)
        chapter = next(row for row in result["semantic_statistics"] if row["scope_kind"] == "unit")
        self.assertEqual(chapter["count"], 2)
        self.assertEqual(result["raw_counts"][0]["raw_form_matches"], 6)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["frequency_outcome"], "有据保留")

    def test_overlapping_forms_are_one_occurrence_but_raw_matches_survive(self):
        self.unit("方便。方便。")
        self.profile["categories"][0]["forms"] += [{"kind": "literal", "value": "方便"}]
        report = self.scan()
        self.assertEqual(report["raw_counts"][0]["raw_form_matches"], 4)
        self.assertEqual(report["raw_counts"][0]["deduplicated_occurrences"], 2)
        self.assertEqual([item["text"] for item in report["occurrences"]], ["方便", "方便"])

    def test_categories_not_merged_and_source_offsets_are_exact(self):
        text = "甲\r\n\r\n便。便。"
        self.unit(text)
        second = copy.deepcopy(self.profile["categories"][0])
        second["id"] = "separate"
        self.profile["categories"].append(second)
        report = self.scan()
        self.assertEqual(len(report["occurrences"]), 4)
        self.assertEqual(report["units"][0]["source_sha256"], language.digest(text.encode("utf-8")))
        for item in report["occurrences"]:
            self.assertEqual(text[item["start"]:item["end"]], "便")
        self.assertEqual(report["units"][0]["nonwhite_characters"], 5)
        paragraph_rows = [row for row in report["statistics"] if row["scope_kind"] == "paragraph"]
        self.assertEqual(len(paragraph_rows), 2)
        self.assertTrue(all(row["scope"] == ["u1", 2] and row["count"] == 2 for row in paragraph_rows))

    def test_fragment_has_no_chapter_threshold_and_rolling_window_is_three(self):
        for number in range(4):
            self.unit("便。便。", "u" + str(number), complete=False)
        report = self.scan()
        self.assertFalse(any(row["triggers"] for row in report["statistics"]))
        windows = [row for row in report["statistics"] if row["scope_kind"] == "rolling3"]
        self.assertEqual(windows[-1]["scope"], ["u1", "u2", "u3"])
        self.assertEqual(windows[-1]["count"], 6)
        self.assertEqual(windows[-1]["nonwhite_characters"], 12)
        self.assertEqual(windows[-1]["per_10000"], 5000)

    def test_density_trigger_requires_specific_aggregate_review(self):
        self.unit("便。便。")
        report = self.scan()
        decisions = self.decisions(report)
        decisions["density_reviews"] = []
        result = self.recount(report, decisions)
        self.assertEqual(result["status"], "NEEDS_VERIFICATION")
        self.assertTrue(any(item["kind"] == "density" for item in result["unresolved"]))
        decisions = self.decisions(report)
        decisions["density_reviews"][0]["occurrence_ids"].pop()
        self.assertEqual(self.recount(report, decisions)["status"], "NEEDS_VERIFICATION")

    def test_new_pattern_or_incomplete_unit_review_prevents_pass(self):
        self.unit("先开门，再点灯。先铺纸，再落笔。")
        report = self.scan()
        decisions = self.decisions(report)
        decisions["unit_reviews"][0]["new_patterns"] = [{"expression": "先……再", "reason": "连续相同句式"}]
        self.assertEqual(self.recount(report, decisions)["status"], "NEEDS_VERIFICATION")
        decisions["unit_reviews"][0]["new_patterns"] = []
        decisions["unit_reviews"][0]["density_reviewed"] = False
        self.assertEqual(self.recount(report, decisions)["status"], "NEEDS_VERIFICATION")

    def test_classification_must_be_complete_unique_and_known(self):
        self.unit("便。便。")
        report = self.scan()
        for mutation in ("missing", "duplicate", "unknown", "null"):
            with self.subTest(mutation=mutation):
                decisions = self.decisions(report)
                if mutation == "missing":
                    decisions["classifications"].pop()
                elif mutation == "duplicate":
                    decisions["classifications"].append(copy.deepcopy(decisions["classifications"][0]))
                elif mutation == "unknown":
                    decisions["classifications"][0]["id"] = "invented"
                else:
                    decisions["classifications"][0]["applies"] = None
                with self.assertRaises(language.ValidationError):
                    self.recount(report, decisions)

    def test_stale_source_and_raised_threshold_are_rejected(self):
        path = self.unit("便。便。")
        report = self.scan()
        decisions = self.decisions(report)
        self.profile["categories"][0]["thresholds"]["chapter_at_least"] = 100
        with self.assertRaisesRegex(language.ValidationError, "stale or modified"):
            self.recount(report, decisions)
        self.profile["categories"][0]["thresholds"]["chapter_at_least"] = 2
        path.write_text("便。", encoding="utf-8")
        with self.assertRaisesRegex(language.ValidationError, "stale or modified"):
            self.recount(report, decisions)

    def test_modified_scan_and_other_scan_decisions_are_rejected(self):
        self.unit("便。")
        report = self.scan()
        decisions = self.decisions(report)
        report["raw_counts"][0]["raw_form_matches"] = 0
        with self.assertRaisesRegex(language.ValidationError, "stale or modified"):
            self.recount(report, decisions)
        report = self.scan()
        decisions["scan_id"] = "other"
        with self.assertRaisesRegex(language.ValidationError, "different scan"):
            self.recount(report, decisions)

    def test_valid_punctuation_and_technical_syntax_are_preserved(self):
        text = ('他说：“看‘说明’（第二版）和《册中〈小节〉》——好了……”。\n\n'
                '型号 F/A-18，版本 2.1，数值 0.25；链接 https://example.test/a?q=2&x=3 。\n'
                '{"level": 2, "name": "ship"}\n\n```yaml\nname: "ship"\nvalue: 2.1\n```\n')
        path = self.unit(text)
        report = self.scan()
        self.assertEqual(report["punctuation"][0]["issues"], [])
        self.assertEqual(path.read_text(encoding="utf-8"), text)
        self.assertEqual(self.recount(report, self.decisions(report))["status"], "PASS")

    def test_wrong_glyphs_cannot_be_excused_by_structure_review(self):
        self.unit('他说:「走...」--真的?')
        report = self.scan()
        codes = {item["code"] for item in report["punctuation"][0]["issues"]}
        self.assertTrue({"ascii_punctuation", "quote_form", "ellipsis_form", "dash_form"} <= codes)
        decisions = self.decisions(report)
        for item in decisions["punctuation_reviews"]:
            item.update(decision="valid_structure", reason="声称看过了")
        self.assertEqual(self.recount(report, decisions)["status"], "NEEDS_VERIFICATION")

    def test_multi_paragraph_quote_requires_llm_structure_review(self):
        self.unit("她说：“第一段。\n\n第二段。”")
        report = self.scan()
        self.assertIn("cross_paragraph_quote", {item["code"] for item in report["punctuation"][0]["issues"]})
        decisions = self.decisions(report)
        self.assertEqual(self.recount(report, decisions)["status"], "NEEDS_VERIFICATION")
        for item in decisions["punctuation_reviews"]:
            item.update(decision="valid_structure", reason="两个自然段属于同一人物的完整引语，末段结束闭合")
        self.assertEqual(self.recount(report, decisions)["status"], "PASS")

    def test_equal_quote_counts_do_not_prove_order_and_nesting(self):
        self.unit("她说：”“甲。‘乙’。")
        report = self.scan()
        self.assertIn("pair_order", {item["code"] for item in report["punctuation"][0]["issues"]})

    def test_explicit_protection_is_exact_and_hash_bound(self):
        text = '引用原样写作「old...」，随后解释。'
        self.unit(text)
        start, end = text.index("「"), text.index("」") + 1
        protected = {"schema_version": 1, "units": [{"unit_id": "u1", "source_sha256": language.digest(text),
                     "spans": [{"start": start, "end": end, "text": text[start:end], "reason": "作者明确要求原样保留的引文"}]}]}
        report = self.scan(protected)
        self.assertEqual(report["punctuation"][0]["issues"], [])
        self.assertEqual(self.recount(report, self.decisions(report), protected)["status"], "PASS")
        protected["units"][0]["source_sha256"] = "stale"
        with self.assertRaisesRegex(language.ValidationError, "stale protected"):
            self.scan(protected)

    def test_partial_protection_cannot_hide_adjacent_punctuation_errors(self):
        for text, end, expected, code in [("甲---乙。", 2, "--", "dash_form"),
                                          ("甲...乙。", 2, "..", "ellipsis_form")]:
            with self.subTest(text=text):
                self.manifest["units"] = []
                self.unit(text)
                protected = {"schema_version": 1, "units": [
                    {"unit_id": "u1", "source_sha256": language.digest(text), "spans": [
                        {"start": 1, "end": end, "text": text[1:end],
                         "reason": "精确保留一个技术字符，后面的符号不在此范围"}]}]}
                report = self.scan(protected)
                issues = report["punctuation"][0]["issues"]
                self.assertEqual([(item["start"], item["end"], item["text"], item["code"]) for item in issues],
                                 [(end, 4, expected, code)])
                self.assertEqual(self.recount(report, self.decisions(report), protected)["status"],
                                 "NEEDS_VERIFICATION")

    def test_fully_protected_runs_and_valid_unprotected_suffix_remain_valid(self):
        text = "甲---——乙。示例 `---...`，版本 1.2……。"
        self.unit(text)
        protected = {"schema_version": 1, "units": [
            {"unit_id": "u1", "source_sha256": language.digest(text), "spans": [
                {"start": 1, "end": 4, "text": "---", "reason": "原样保留的技术符号"}]}]}
        report = self.scan(protected)
        self.assertEqual(report["punctuation"][0]["issues"], [])
        self.assertEqual(self.recount(report, self.decisions(report), protected)["status"], "PASS")

    def test_whole_unit_exemption_is_rejected(self):
        text = "整章..."
        self.unit(text)
        protected = {"schema_version": 1, "units": [{"unit_id": "u1", "source_sha256": language.digest(text),
                     "spans": [{"start": 0, "end": len(text), "text": text, "reason": "全章豁免"}]}]}
        with self.assertRaisesRegex(language.ValidationError, "whole-unit"):
            self.scan(protected)

    def test_combined_blanket_exemption_is_rejected(self):
        text = "引文... 叙述..."
        self.unit(text)
        protected = {"schema_version": 1, "units": [{"unit_id": "u1", "source_sha256": language.digest(text),
                     "spans": [{"start": 0, "end": 5, "text": text[:5], "reason": "引文"},
                               {"start": 6, "end": len(text), "text": text[6:], "reason": "另一引文"}]}]}
        with self.assertRaisesRegex(language.ValidationError, "combined whole-unit"):
            self.scan(protected)

    def test_inherited_default_threshold_boundaries(self):
        path = self.unit("或许晴。或许雨。" + "不是风，是雨。" * 3 + "来了——又走。" * 15)
        profile = language.default_profile()
        first = language.scan(self.root, self.manifest, profile)
        by_category = {row["category_id"]: row for row in first["statistics"] if row["scope_kind"] == "unit"}
        maybe = next(category["id"] for category in profile["categories"] if category.get("label") == "或许")
        self.assertEqual(by_category[maybe]["triggers"], ["chapter_at_least"])
        self.assertEqual(by_category["contrast"]["count"], 3)
        self.assertEqual(by_category["contrast"]["triggers"], [])
        self.assertEqual(by_category["dash"]["count"], 15)
        self.assertEqual(by_category["dash"]["triggers"], [])
        path.write_text(path.read_text(encoding="utf-8") + "不是风，是雨。来了——又走。", encoding="utf-8")
        second = language.scan(self.root, self.manifest, profile)
        by_category = {row["category_id"]: row for row in second["statistics"] if row["scope_kind"] == "unit"}
        self.assertEqual(by_category["contrast"]["triggers"], ["chapter_more_than"])
        self.assertEqual(by_category["dash"]["triggers"], ["chapter_more_than"])

    def test_paths_duplicate_units_and_sliced_manifests_fail_safely(self):
        self.unit("正文。")
        original = copy.deepcopy(self.manifest)
        for name in ("duplicate", "escape", "sliced"):
            with self.subTest(name=name):
                self.manifest = copy.deepcopy(original)
                if name == "duplicate":
                    self.manifest["units"].append({"unit_id": "u2", "path": "u1.md", "complete_chapter": True})
                elif name == "escape":
                    self.manifest["units"][0]["path"] = "../outside.md"
                else:
                    self.manifest["units"][0]["reading"] = [{"path": "u1.md", "start": 0, "end": 2}]
                with self.assertRaises(language.ValidationError):
                    self.scan()

    def test_profile_validation_and_zero_length_regex(self):
        self.unit("正文。")
        for bad in (-1, float("nan"), True):
            self.profile["categories"][0]["thresholds"]["chapter_at_least"] = bad
            with self.assertRaises(language.ValidationError):
                self.scan()
        self.profile["categories"][0]["thresholds"] = {}
        self.profile["categories"][0]["forms"] = [{"kind": "regex", "value": "(?=正)"}]
        with self.assertRaisesRegex(language.ValidationError, "empty match"):
            self.scan()

    def test_repeat_mapping_watch_and_no_entity_heuristic(self):
        self.unit("航船编号甲乙丙丁戊己，今天驶向港口。", "u1")
        self.unit("航船编号甲乙丙丁戊己；今天驶向港口。", "u2")
        result = repeats.scan_repeats(self.root, self.manifest, watch=["甲乙丙丁戊己"])
        self.assertTrue(result["matches"])
        self.assertEqual(result["watch_terms"][0]["count"], 2)
        for match in result["matches"]:
            self.assertGreaterEqual(match["normalized_length"], 10)
            for side in ("left", "right"):
                item = match[side]
                text = (self.root / item["path"]).read_text(encoding="utf-8")
                self.assertEqual(text[item["start"]:item["end"]], item["text"])
                self.assertEqual(repeats.normalize(item["text"])[0], match["normalized_text"])

    def test_repeat_limit_reports_incomplete_not_clear(self):
        self.unit("甲" * 40)
        result = repeats.scan_repeats(self.root, self.manifest, min_length=10, max_results=1)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["status"], "NEEDS_VERIFICATION")
        self.assertEqual(len(result["matches"]), 1)

    def test_cli_can_scan_recount_and_will_not_overwrite_input(self):
        self.unit("夜色安静。")
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        command = [sys.executable, str(SCRIPTS / "language_scan.py"), "scan", "--project-root", str(self.root),
                   "--manifest", str(manifest_path)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        report_path, decisions_path = self.root / "scan.json", self.root / "decisions.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        decisions_path.write_text(json.dumps(self.decisions(report)), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(SCRIPTS / "language_scan.py"), "recount", "--project-root", str(self.root),
                                    "--scan", str(report_path), "--classifications", str(decisions_path)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "PASS")
        before = manifest_path.read_bytes()
        completed = subprocess.run(command + ["--output", str(manifest_path)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(manifest_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
