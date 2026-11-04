"""Exercise local installation, conflict handling and independent release use."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile


GENERAL = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, GENERAL / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load("wordtact_install_test", "install.py")
builder = load("wordtact_build_test", "scripts/build_package.py")


class InstallationTests(unittest.TestCase):
    def test_default_installs_two_siblings_and_repeated_install_is_noop(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "skills"
            first = installer.install(destination)
            self.assertEqual([x["action"] for x in first["skills"]], ["create", "create"])
            self.assertEqual({p.name for p in destination.iterdir()}, set(installer.SKILLS))
            for name, content in installer.payloads().items():
                self.assertEqual(installer.files(destination / name), content)
            second = installer.install(destination)
            self.assertEqual([x["action"] for x in second["skills"]], ["unchanged", "unchanged"])
            self.assertIsNone(second["backup"])

    def test_general_edition_can_install_only_the_conversation_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            standalone = base / "general"
            standalone.mkdir()
            for name in installer.SKILLS:
                shutil.copytree(GENERAL / name, standalone / name)
            shutil.copy2(GENERAL / "install.py", standalone / "install.py")
            destination = base / "skills"
            result = subprocess.run(
                [sys.executable, str(standalone / "install.py"), "--dest", str(destination),
                 "--only", "conversational-register"], cwd=base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in destination.iterdir()}, {"conversational-register"})
            self.assertEqual((destination / "conversational-register/SKILL.md").read_bytes(),
                             (standalone / "conversational-register/SKILL.md").read_bytes())

    def test_conflict_is_detected_before_either_skill_is_written(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "skills"
            custom = destination / "conversational-register/SKILL.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("custom conversation rules")
            with self.assertRaisesRegex(ValueError, "different existing skill"):
                installer.install(destination)
            self.assertFalse((destination / "wordtact").exists())
            self.assertEqual(custom.read_text(), "custom conversation rules")

    def test_dry_run_writes_no_destination_or_backups(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            result = installer.install(base / "skills", dry_run=True, backup_dir=base / "backups")
            self.assertTrue(result["dry_run"])
            self.assertEqual(list(base.iterdir()), [])

    def test_replace_backs_up_original_and_preserves_unrelated_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            destination = base / "skills"
            custom = destination / "conversational-register/SKILL.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("user version")
            unrelated = destination / "unrelated/SKILL.md"
            unrelated.parent.mkdir()
            unrelated.write_text("unrelated rules")
            result = installer.install(destination, replace=True, backup_dir=base / "backups")
            self.assertEqual((Path(result["backup"]) / "conversational-register/SKILL.md").read_text(), "user version")
            self.assertEqual(unrelated.read_text(), "unrelated rules")
            self.assertEqual(custom.read_bytes(), installer.payloads()["conversational-register"]["SKILL.md"])

    def test_different_symlink_is_not_followed_or_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            actual = base / "personal"
            actual.mkdir()
            (actual / "SKILL.md").write_text("personal")
            destination = base / "skills"
            destination.mkdir()
            (destination / "conversational-register").symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "different existing symlink"):
                installer.install(destination, replace=True, backup_dir=base / "backups")
            self.assertFalse((destination / "wordtact").exists())
            self.assertTrue((destination / "conversational-register").is_symlink())
            self.assertEqual((actual / "SKILL.md").read_text(), "personal")

    def test_identical_symlink_is_reused(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            actual = base / "managed"
            installer.install(actual)
            destination = base / "skills"
            destination.mkdir()
            for name in installer.SKILLS:
                (destination / name).symlink_to(actual / name, target_is_directory=True)
            result = installer.install(destination)
            self.assertEqual([x["action"] for x in result["skills"]], ["unchanged", "unchanged"])
            self.assertTrue(all((destination / name).is_symlink() for name in installer.SKILLS))

    def test_second_write_failure_restores_both_originals(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            destination = base / "skills"
            for name in installer.SKILLS:
                path = destination / name
                path.mkdir(parents=True)
                (path / "SKILL.md").write_text(name + " original")
            replace = installer.os.replace

            def fail_second(source, target):
                source = Path(source)
                if source.name == "conversational-register" and source.parent.name == "new":
                    raise OSError("simulated write failure")
                return replace(source, target)

            with mock.patch.object(installer.os, "replace", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "simulated write failure"):
                    installer.install(destination, replace=True, backup_dir=base / "backups")
            for name in installer.SKILLS:
                self.assertEqual((destination / name / "SKILL.md").read_text(), name + " original")

    def test_invalid_payload_stops_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "general"
            shutil.copytree(GENERAL, source)
            (source / "conversational-register/SKILL.md").write_text("broken")
            with self.assertRaisesRegex(ValueError, "frontmatter"):
                installer.install(base / "skills", root=source)
            self.assertFalse((base / "skills").exists())

    def test_destination_cannot_be_nested_inside_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "general"
            shutil.copytree(GENERAL, source)
            with self.assertRaisesRegex(ValueError, "overlap"):
                installer.install(source / "nested", root=source)
            self.assertFalse((source / "nested").exists())

    def test_stale_fallback_is_rejected_and_synced_from_the_sibling_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "general"
            shutil.copytree(GENERAL, source)
            fallback = source / "wordtact/references/conversation.md"
            fallback.write_text("stale fallback")
            with self.assertRaisesRegex(ValueError, "fallback is stale"):
                installer.payloads(source)
            builder.sync_conversation(source)
            expected = installer.conversation_body((source / "conversational-register/SKILL.md").read_bytes())
            self.assertEqual(fallback.read_bytes(), expected)
            self.assertIn("conversational-register", installer.payloads(source))


class ReleaseTests(unittest.TestCase):
    def test_macos_metadata_is_excluded_from_installation_and_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "general"
            shutil.copytree(GENERAL, source)
            for name in installer.SKILLS:
                for relative in (".DS_Store", "._SKILL.md", ".AppleDouble/props",
                                 "__MACOSX/resource", "preferences.plist", "cache.PLIST",
                                 "references/.DS_Store", "references/._notes.md",
                                 "__pycache__/cache.pyc"):
                    path = source / name / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"filesystem metadata")
            self.assertEqual(builder.release_files(source), builder.release_files(GENERAL))
            destination = base / "skills"
            installer.install(destination, root=source)
            for name, expected in installer.payloads(GENERAL).items():
                actual = {p.relative_to(destination / name).as_posix()
                          for p in (destination / name).rglob("*") if p.is_file()}
                self.assertEqual(actual, set(expected))

    def test_release_is_deterministic_and_installs_without_the_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = builder.build(base / "first.zip")
            second = builder.build(base / "second.zip")
            self.assertEqual(first["sha256"], second["sha256"])
            with zipfile.ZipFile(base / "first.zip") as archive:
                self.assertIsNone(archive.testzip())
                self.assertFalse(any("__pycache__" in name or "/novel/" in name or "/tests/" in name
                                     for name in archive.namelist()))
                archive.extractall(base / "unpacked")
            release = base / "unpacked/wordtact-general"
            manifest = json.loads((release / "manifest.json").read_text())
            actual = {p.relative_to(release).as_posix() for p in release.rglob("*")
                      if p.is_file() and p.name != "manifest.json"}
            self.assertEqual(set(manifest), actual)
            for relative, expected in manifest.items():
                self.assertEqual(hashlib.sha256((release / relative).read_bytes()).hexdigest(), expected)
            self.assertEqual(installer.conversation_body((release / "conversational-register/SKILL.md").read_bytes()),
                             (release / "wordtact/references/conversation.md").read_bytes())
            destination = base / "client/skills"
            result = subprocess.run([sys.executable, str(release / "install.py"),
                                     "--dest", str(destination)], cwd=base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in installer.SKILLS:
                self.assertEqual(installer.files(destination / name), installer.files(release / name))

    def test_release_output_inside_general_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside general"):
            builder.build(GENERAL / "generated.zip")


if __name__ == "__main__":
    unittest.main()
