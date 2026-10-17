from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]


class NarrativeContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (REPO / relative).read_text(encoding="utf-8")

    def yaml_after(self, text: str, marker: str) -> object:
        marker_at = text.index(marker)
        fence_at = text.index("```yaml", marker_at) + len("```yaml")
        fence_end = text.index("```", fence_at)
        return yaml.safe_load(text[fence_at:fence_end])

    def shape(self, value: object) -> object:
        if isinstance(value, dict):
            return {key: self.shape(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.shape(value[0])] if value else []
        return type(value).__name__

    def test_narrative_craft_has_six_conditional_modules_without_hard_quotas(self) -> None:
        craft = self.read("user/novel-expander/references/narrative-craft.md")
        self.assertGreaterEqual(len(craft.splitlines()), 180)
        self.assertLessEqual(len(craft.splitlines()), 250)
        for number in range(1, 7):
            self.assertRegex(craft, rf"(?m)^## {number}\. ")
        for forbidden in (
            "一个场景最多调动两个感官",
            "一页之内最多一个比喻",
            "固定对话比例",
        ):
            self.assertNotIn(forbidden, craft)

        expander = self.read("user/novel-expander/SKILL.md")
        draft = self.read("user/novel-ci/references/workflow-draft.md")
        self.assertIn("references/narrative-craft.md", expander)
        self.assertIn("references/narrative-craft.md", draft)
        self.assertIn("two-pass self-check", expander)
        self.assertIn("Evaluation separation", expander)

    def test_scene_card_and_review_expose_new_contract_fields(self) -> None:
        planning = self.read("user/novel-ci/references/workflow-planning.md")
        contracts = self.read("design/novel-ci/contracts.md")
        for marker in (
            "stakes:",
            "change_chain:",
            "response_kind:",
            "dynamics:",
            "time_handling:",
            "dialogue_dynamics:",
            "narrator:",
            "narratee:",
            "form:",
            "attention_filter:",
            "embodied_by:",
            "emergent_patterns:",
        ):
            self.assertIn(marker, planning)
            self.assertIn(marker, contracts)

        review = self.read("user/novel-ci/references/workflow-review.md")
        checks = self.read("user/novel-ci/references/checks-structure.md")
        self.assertIn("narrative_delivery: PASS", review)
        self.assertIn("Module 6: narrative_delivery_tests", checks)
        self.assertIn("不得按感官数", checks)

    def test_runtime_schemas_have_single_owners(self) -> None:
        reference_dir = REPO / "user" / "novel-ci" / "references"
        expected = {
            "scene_card": "workflow-planning.md",
            "chapter_arc": "workflow-planning.md",
            "review_report": "workflow-review.md",
            "regression_report": "workflow-regression.md",
            "verification_record": "project-context.md",
        }
        for schema, owner in expected.items():
            pattern = re.compile(rf"^{schema}:\s*$", re.MULTILINE)
            holders = [
                path.name
                for path in sorted(reference_dir.glob("*.md"))
                if pattern.search(path.read_text(encoding="utf-8"))
            ]
            self.assertEqual(holders, [owner])

    def test_runtime_owner_schemas_match_design_contract_shapes(self) -> None:
        contracts = self.read("design/novel-ci/contracts.md")
        planning = self.read("user/novel-ci/references/workflow-planning.md")
        review = self.read("user/novel-ci/references/workflow-review.md")
        regression = self.read("user/novel-ci/references/workflow-regression.md")
        comparisons = (
            (contracts, "### 8.5 scene_card", planning, "### scene_card schema"),
            (contracts, "### 8.6 chapter_arc", planning, "### chapter_arc schema"),
            (contracts, "### 8.7 review_report", review, "## 2. review_report schema"),
            (contracts, "### 8.8 regression_report", regression, "## 2. regression_report schema"),
        )
        for design_text, design_marker, runtime_text, runtime_marker in comparisons:
            with self.subTest(schema=design_marker):
                self.assertEqual(
                    self.shape(self.yaml_after(design_text, design_marker)),
                    self.shape(self.yaml_after(runtime_text, runtime_marker)),
                )

    def test_feedback_and_lens_questions_are_symptom_first(self) -> None:
        review = self.read("user/novel-ci/references/workflow-review.md")
        self.assertIn("读者反馈是症状，不是现成 patch", review)
        self.assertIn("2—3 个底层原因假设", review)
        self.assertIn("证据不足进入 RISK", review)

        runtime_lenses = self.read("user/novel-discuss/references/lens-catalog.md")
        design_lenses = self.read("design/novel-discuss/lens-catalog.md")
        for marker in (
            "哪些内容应成为前景场景,哪些应简述或留作白空间",
            "哪一步是作者需要而非人物需要",
            "谁在说、对谁说、以什么形式、心理距离多近",
            "可观察症状是什么",
        ):
            self.assertIn(marker, runtime_lenses)
            self.assertIn(marker, design_lenses)

    def test_canonical_language_rules_remove_numeric_craft_failures(self) -> None:
        expander = REPO / "user" / "novel-expander" / "references" / "anti-ai-patterns.md"
        auditor = REPO / "user" / "novel-auditor" / "references" / "anti-ai-patterns.md"
        forward = re.search(r"\]\(([^)]+anti-ai-patterns\.md)\)", auditor.read_text(encoding="utf-8"))
        self.assertIsNotNone(forward)
        self.assertEqual((auditor.parent / forward.group(1)).resolve(), expander.resolve())
        self.assertLess(len(auditor.read_text().splitlines()), 20)
        text = expander.read_text(encoding="utf-8")
        for forbidden in (
            "一个场景最多调动两个感官",
            "一页之内最多一个比喻",
            "砍到 2 个",
            "砍到 1 个或 0 个",
        ):
            self.assertNotIn(forbidden, text)
        self.assertIn("感官数量没有固定上限", text)
        self.assertIn("不是“一页一个”的失败阈值", text)

    def test_required_verification_status_is_exposed_in_all_acceptance_schemas(self) -> None:
        for owner, marker, root, result in (
            ("workflow-review.md", "## 2. review_report schema", "review_report", "acceptability"),
            ("workflow-regression.md", "## 2. regression_report schema", "regression_report", "result"),
            ("workflow-planning.md", "### chapter_arc schema", "chapter_arc", "integration_result"),
        ):
            doc = self.read("user/novel-ci/references/" + owner)
            schema = self.yaml_after(doc, marker)[root]
            target = schema if root != "chapter_arc" else schema[result]
            self.assertIn("verification", target)
            self.assertIn("NEEDS_VERIFICATION", schema[result]["status"].split(" | "))
        shared = self.read("user/novel-ci/references/project-context.md")
        blocks = re.findall(r"```yaml\n(.*?)```", shared, re.S)
        record = next(yaml.safe_load(block)["verification_record"] for block in blocks if block.startswith("verification_record:"))
        self.assertEqual(set(record["required"]), {"frequency", "punctuation", "semantics"})
        self.assertTrue(all(record["checks"][key]["status"] == "SKIPPED" for key in record["required"]))

    def test_failure_type_and_fixed_punctuation_contract(self) -> None:
        conventions = self.read("user/novel-ci/references/conventions.md")
        design = self.read("design/novel-ci/contracts.md")
        for text in (conventions, design):
            self.assertIn("`reader_redundancy`", text)
        rules = self.read("user/novel-expander/references/anti-ai-patterns.md")
        for mark in ("，。；：？！、", "——", "……", "U+2014", "U+2026", "NFKC"):
            self.assertIn(mark, rules)


if __name__ == "__main__":
    unittest.main()
