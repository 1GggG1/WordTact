"""Check that the prose skill works as a standalone resource bundle, not model quality."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
import zipfile


SKILL = Path(__file__).resolve().parents[1] / "wordtact"


class StandaloneTests(unittest.TestCase):
    def assert_bundle(self, root):
        root = root.resolve()
        self.assertTrue((root / "SKILL.md").is_file())
        self.assertTrue((root / "LICENSE").is_file())
        self.assertTrue((root / "THIRD_PARTY_NOTICES.md").is_file())
        pending = [root / "SKILL.md"]
        visited = set()
        while pending:
            document = pending.pop()
            if document in visited:
                continue
            visited.add(document)
            for link in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", document.read_text()):
                parsed = urlsplit(link)
                if parsed.scheme or not parsed.path:
                    continue
                target = (document.parent / unquote(parsed.path)).resolve()
                self.assertTrue(target.is_relative_to(root.resolve()), link)
                self.assertTrue(target.is_file(), link)
                pending.append(target)
        resources = set(root.rglob("*.md"))
        self.assertEqual(visited, resources, "Every shipped Markdown resource must be reachable")

    def test_source_graph_is_self_contained(self):
        self.assert_bundle(SKILL)

    def test_conversation_reference_does_not_register_a_duplicate_skill(self):
        reference = SKILL / "references/conversation.md"
        self.assertTrue(reference.is_file())
        self.assertEqual(list(SKILL.rglob("SKILL.md")), [SKILL / "SKILL.md"])
        self.assertFalse(reference.read_text().startswith("---\n"))
        self.assertNotRegex(reference.read_text(), r"\bCG\b|/(?:Users|home)/[^/]+/")

    def test_missing_conversation_reference_breaks_standalone_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "wordtact"
            shutil.copytree(SKILL, copied)
            (copied / "references/conversation.md").unlink()
            with self.assertRaises(AssertionError):
                self.assert_bundle(copied)

    def test_copy_outside_repository_needs_no_sibling_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "wordtact"
            shutil.copytree(SKILL, copied)
            self.assert_bundle(copied)

    def test_archive_roundtrip_preserves_all_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "wordtact.zip"
            with zipfile.ZipFile(archive, "w") as package:
                for path in SKILL.rglob("*"):
                    if path.is_file():
                        package.write(path, "wordtact/" + path.relative_to(SKILL).as_posix())
            with zipfile.ZipFile(archive) as package:
                self.assertIsNone(package.testzip())
                package.extractall(base / "extracted")
            extracted = base / "extracted/wordtact"
            self.assert_bundle(extracted)
            for path in SKILL.rglob("*"):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (extracted / path.relative_to(SKILL)).read_bytes())

    def test_missing_or_external_reference_is_rejected(self):
        for link in ("references/missing.md", "../another-skill/SKILL.md"):
            with self.subTest(link=link), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary) / "wordtact"
                shutil.copytree(SKILL, copied)
                with (copied / "SKILL.md").open("a") as stream:
                    stream.write(f"\n[required reference]({link})\n")
                with self.assertRaises(AssertionError):
                    self.assert_bundle(copied)


if __name__ == "__main__":
    unittest.main()
