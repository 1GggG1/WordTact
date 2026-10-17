"""Check the composed audit's resource graph in both supported skill layouts.

These are packaging/link checks, not evidence of model behavior. Independent execution
scenarios and evaluation boundaries are documented under fixtures/audit_composition/.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
try:
    from build_source_package import source_files
finally:
    sys.path.pop(0)


AUDIT_CONSUMERS = (
    "novel-auditor/SKILL.md",
    "novel-auditor/references/audit-planning.md",
    "novel-auditor/references/audit-execution.md",
    "novel-auditor/references/audit-workflow.md",
    "novel-auditor/references/style-consistency.md",
    "novel-auditor/references/reading-load-zh.md",
    "novel-auditor/references/style-reference.md",
    "novel-ci/references/project-context.md",
    "novel-ci/references/workflow-review.md",
    "novel-ci/references/workflow-patch.md",
    "novel-ci/references/checks-canon.md",
    "novel-ci/references/workflow-regression.md",
    "novel-ci/references/workflow-draft.md",
    "novel-expander/SKILL.md",
    "novel-expander/references/anti-ai-patterns.md",
    "novel-expander/references/humanizer-fiction.md",
    "novel-expander/THIRD_PARTY_NOTICES.md",
    "novel-expander/references/expansion-workflow.md",
    "novel-expander/references/style-guide.md",
)


class AuditResourceTests(unittest.TestCase):
    def assert_local_links_resolve(self, document: Path, root: Path) -> None:
        links = re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", document.read_text(encoding="utf-8"))
        self.assertTrue(links, f"No resource links found in {document}")
        for link in links:
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            with self.subTest(document=document.relative_to(root), link=link):
                target = (document.parent / unquote(parsed.path)).resolve()
                self.assertTrue(target.is_relative_to(root.resolve()), str(target))
                self.assertTrue(target.is_file(), f"Missing resource: {target}")

    def test_audit_resources_resolve_in_source_layout(self) -> None:
        for relative in AUDIT_CONSUMERS:
            self.assert_local_links_resolve(REPO / "user" / relative, REPO)
        self.assert_local_links_resolve(REPO / "design/novel-ci/contracts.md", REPO)

    def test_audit_resources_resolve_in_flat_layout(self) -> None:
        with tempfile.TemporaryDirectory(prefix="audit-flat-") as temporary:
            flat = Path(temporary) / "skills"
            shutil.copytree(REPO / "user", flat, ignore=shutil.ignore_patterns("__pycache__"))
            for relative in AUDIT_CONSUMERS:
                self.assert_local_links_resolve(flat / relative, flat)

    def test_audit_resources_are_in_source_package(self) -> None:
        packaged = {path.relative_to(REPO).as_posix() for path in source_files(REPO)}
        self.assertTrue({f"user/{path}" for path in AUDIT_CONSUMERS}.issubset(packaged))


if __name__ == "__main__":
    unittest.main()
