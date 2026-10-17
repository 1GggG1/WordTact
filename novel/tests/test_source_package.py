from __future__ import annotations

import copy
import hashlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ARCHIVE_NAME_RE = re.compile(r"^novel-superpower-full-\d{8}\.zip$")
sys.path.insert(0, str(REPO / "scripts"))
try:
    import build_source_package as builder
    import validate_source_package as validator
finally:
    sys.path.pop(0)


def run_script(script, *args, repo=REPO):
    return subprocess.run([sys.executable, str(repo / "scripts" / script), *map(str, args)],
                          cwd=repo, text=True, capture_output=True, check=False)


def rewrite_member(source, output, mutate):
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, "w") as changed:
        for info in original.infolist():
            data = original.read(info)
            metadata, content = mutate(copy.copy(info), data)
            changed.writestr(metadata, content)



class SourcePackageTests(unittest.TestCase):
    def test_full_product_does_not_package_sibling_general_product(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            root = repository / "novel"
            root.mkdir()
            (repository / "general/wordtact").mkdir(parents=True)
            (repository / "general/wordtact/SKILL.md").write_text("standalone")
            (root / "SKILL.md").write_text("full product")
            archive = repository / "novel.zip"
            builder.build(archive, root)
            with zipfile.ZipFile(archive) as package:
                self.assertEqual(package.namelist(), ["novel-superpower/SKILL.md"])

    def test_missing_humanizer_resource_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for skill in ("novel-auditor", "novel-expander"):
                shutil.copytree(REPO / "user" / skill, base / skill)
            for relative in ("references/humanizer-fiction.md", "THIRD_PARTY_NOTICES.md"):
                with self.subTest(resource=relative):
                    path = base / "novel-expander" / relative
                    content = path.read_bytes()
                    path.unlink()
                    errors = []
                    validator.check_shared_files(errors, base)
                    self.assertTrue(any(relative in error for error in errors))
                    path.write_bytes(content)

    def test_builder_rejects_invalid_release_date(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts" / "build_source_package.py"),
                "--date",
                "20260230",
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid YYYYMMDD date", result.stderr)

    def test_repository_validator_passes(self) -> None:
        # A previous release cannot establish that today's changed source is sound.
        result = run_script("validate_source_package.py", "--skip-archive")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Source package validation passed", result.stdout)

    def test_publish_surface_contains_only_generic_skills(self) -> None:
        expected = {
            "file-tagging",
            "novel-auditor",
            "novel-ci",
            "novel-discuss",
            "novel-expander",
            "vault-organizer",
        }
        actual = {
            path.name
            for path in (REPO / "user").iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        self.assertEqual(actual, expected)

    def test_language_rules_have_one_owner_and_loading_consumers(self) -> None:
        errors = []
        validator.check_shared_files(errors)
        self.assertEqual(errors, [])

    def test_broken_forwarder_or_unloaded_consumer_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for skill in ("novel-auditor", "novel-expander"):
                shutil.copytree(REPO / "user" / skill, base / skill)
            forwarder = base / "novel-auditor/references/anti-ai-patterns.md"
            good = forwarder.read_text(encoding="utf-8")
            forwarder.write_text(good.replace("../../novel-expander/", "../../missing/"), encoding="utf-8")
            errors = []
            validator.check_shared_files(errors, base)
            self.assertTrue(any("sole expander" in error for error in errors))
            forwarder.write_text(good, encoding="utf-8")
            entry = base / "novel-auditor/SKILL.md"
            entry.write_text(entry.read_text(encoding="utf-8").replace("Read `references/anti-ai-patterns.md`",
                                                                      "Optional rule reference"),
                             encoding="utf-8")
            errors = []
            validator.check_shared_files(errors, base)
            self.assertTrue(any("must instruct loading" in error for error in errors))

    def test_fresh_archive_matches_source_and_extracted_tools_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="novel-package-") as temporary:
            base = Path(temporary)
            archive = base / "release.zip"
            built = run_script("build_source_package.py", "--date", "20261013", "--output", archive)
            self.assertEqual(built.returncode, 0, built.stderr)
            checked = run_script("validate_source_package.py", "--archive", archive)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            with zipfile.ZipFile(archive) as package:
                self.assertEqual(package.read("novel-superpower/LICENSE"),
                                 (REPO / "LICENSE").read_bytes())
                package.extractall(base / "extract")
            extracted = base / "extract" / builder.PREFIX
            checked = run_script("validate_source_package.py", "--skip-archive", repo=extracted)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            # Source and flat sibling layouts must resolve the same rule owner.
            flat = base / "flat"
            shutil.copytree(extracted / "user", flat)
            errors = []
            validator.check_shared_files(errors, flat)
            self.assertEqual(errors, [])
            for relative in ("novel-ci/scripts/reader_index.py", "novel-ci/scripts/revision_guard.py",
                             "novel-auditor/scripts/language_scan.py", "novel-auditor/scripts/repeat_scan.py",
                             "novel-auditor/scripts/style_reference.py"):
                for layout in (extracted / "user", flat):
                    result = subprocess.run([sys.executable, str(layout / relative), "--help"],
                                            cwd=base, text=True, capture_output=True, check=False)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_reference_resource_is_detected_in_flat_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for skill in ("novel-auditor", "novel-expander"):
                shutil.copytree(REPO / "user" / skill, base / skill)
            for relative in ("scripts/style_reference.py", "references/style-consistency.md",
                             "references/reading-load-zh.md"):
                with self.subTest(resource=relative):
                    path = base / "novel-auditor" / relative
                    content = path.read_bytes()
                    path.unlink()
                    errors = []
                    validator.check_shared_files(errors, base)
                    self.assertTrue(any(relative in error for error in errors))
                    path.write_bytes(content)

    def test_builder_explicit_output_does_not_touch_legacy_archives(self) -> None:
        before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in builder.source_archives(REPO)}
        with tempfile.TemporaryDirectory() as temporary:
            result = run_script("build_source_package.py", "--output", Path(temporary) / "new.zip")
            self.assertEqual(result.returncode, 0, result.stderr)
        after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in builder.source_archives(REPO)}
        self.assertEqual(before, after)

    def test_conflicting_archive_cli_options_are_rejected(self) -> None:
        result = run_script("validate_source_package.py", "--skip-archive", "--archive", "unused.zip")
        self.assertNotEqual(result.returncode, 0)
        result = run_script("build_source_package.py", "--output", "unused.zip", "--replace-existing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be combined", result.stderr)


class ArchiveIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="package-integrity-")
        self.base = Path(self.temporary.name)
        self.root = self.base / "source"
        self.root.mkdir()
        (self.root / "SKILL.md").write_text("Synthetic package fixture.\n", encoding="utf-8")
        (self.root / "tool.py").write_text("print('sample')\n", encoding="utf-8")
        (self.root / "tool.py").chmod(0o755)
        self.archive = self.base / "original.zip"
        builder.build(self.archive, self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def errors(self, archive):
        result = []
        with mock.patch.object(validator, "ROOT", self.root):
            validator.check_archive(result, archive)
        return result

    def test_fresh_build_is_deterministic_and_permissions_match(self):
        second = self.base / "second.zip"
        count, checksum = builder.build(second, self.root)
        self.assertEqual(count, 2)
        self.assertEqual(self.archive.read_bytes(), second.read_bytes())
        self.assertEqual(checksum, hashlib.sha256(second.read_bytes()).hexdigest())
        self.assertEqual(self.errors(second), [])
        with zipfile.ZipFile(second) as package:
            mode = package.getinfo("novel-superpower/tool.py").external_attr >> 16
            self.assertTrue(stat.S_ISREG(mode))
            self.assertEqual(stat.S_IMODE(mode), 0o755)

    def test_macos_metadata_is_excluded_and_injected_members_are_rejected(self):
        junk = (
            ".DS_Store", "nested/.DS_Store", "nested/._README.md",
            "__MACOSX/nested/README.md", ".AppleDouble/README.md", ".LSOverride",
            ".Spotlight-V100/index", ".Trashes/item", ".fseventsd/log",
            ".TemporaryItems/item", ".DocumentRevisions-V100/item",
            ".VolumeIcon.icns", ".com.apple.timemachine.donotpresent",
            "nested/preferences.plist",
        )
        for name in junk:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("local metadata")
        (self.root / "preferences.json").write_text('{"source": true}')
        clean = self.base / "clean.zip"
        builder.build(clean, self.root)
        with zipfile.ZipFile(clean) as package:
            self.assertEqual(set(package.namelist()), {
                "novel-superpower/SKILL.md", "novel-superpower/tool.py",
                "novel-superpower/preferences.json",
            })
        self.assertEqual(self.errors(clean), [])
        for index, name in enumerate(junk):
            with self.subTest(name=name):
                tampered = self.base / f"metadata-{index}.zip"
                shutil.copy2(clean, tampered)
                with zipfile.ZipFile(tampered, "a") as package:
                    package.writestr("novel-superpower/" + name, "local metadata")
                self.assertTrue(any("macOS metadata" in error for error in self.errors(tampered)))

    def test_valid_crc_does_not_hide_tampered_content(self):
        tampered = self.base / "tampered.zip"
        def mutate(info, content):
            return info, content.replace(b"sample", b"tamper")
        rewrite_member(self.archive, tampered, mutate)
        with zipfile.ZipFile(tampered) as package, zipfile.ZipFile(self.archive) as original:
            self.assertIsNone(package.testzip())
            self.assertEqual(package.namelist(), original.namelist())
        self.assertTrue(any("content differs" in error for error in self.errors(tampered)))

    def test_old_archive_cannot_verify_changed_source(self):
        (self.root / "tool.py").write_text("print('updated source')\n", encoding="utf-8")
        self.assertTrue(any("content differs" in error for error in self.errors(self.archive)))

    def test_tampered_permission_and_symlink_type_are_rejected(self):
        for mode in (stat.S_IFREG | 0o777, stat.S_IFLNK | 0o755):
            tampered = self.base / (str(mode) + ".zip")
            def mutate(info, content):
                info.external_attr = mode << 16
                return info, content
            rewrite_member(self.archive, tampered, mutate)
            self.assertTrue(any("permissions differ" in error or "regular Unix file" in error
                                for error in self.errors(tampered)))

    def test_missing_extra_duplicate_and_unsafe_members_are_rejected(self):
        missing = self.base / "missing.zip"
        with zipfile.ZipFile(self.archive) as source, zipfile.ZipFile(missing, "w") as package:
            info = source.infolist()[0]
            package.writestr(info, source.read(info))
        self.assertTrue(any("file list differs" in error for error in self.errors(missing)))
        extra = self.base / "extra.zip"
        shutil.copy2(self.archive, extra)
        with zipfile.ZipFile(extra, "a") as package:
            package.writestr("../escape", "untrusted")
        self.assertTrue(any("unsafe archive" in error for error in self.errors(extra)))
        duplicate = self.base / "duplicate.zip"
        shutil.copy2(self.archive, duplicate)
        with self.assertWarns(UserWarning), zipfile.ZipFile(duplicate, "a") as package:
            package.writestr("novel-superpower/SKILL.md", "duplicate")
        self.assertTrue(any("duplicate file" in error for error in self.errors(duplicate)))

    def test_output_cannot_be_packaged_into_itself(self):
        for output in (self.root / "release.zip", self.root / "dist" / "release.zip"):
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "self-inclusion"):
                builder.build(output, self.root)
            self.assertFalse(output.exists())
        allowed = self.root / "novel-superpower-full-20261013.zip"
        builder.build(allowed, self.root)
        with zipfile.ZipFile(allowed) as package:
            self.assertEqual(len(package.namelist()), 2)

    def test_legacy_archive_defaults_and_symlink_rejection(self):
        self.assertEqual(builder.archive_for_date("20261013", self.root),
                         self.root / "novel-superpower-full-20261013.zip")
        (self.root / "alias.py").symlink_to(self.root / "tool.py")
        with self.assertRaisesRegex(ValueError, "symlink"):
            builder.build(self.base / "symlinks.zip", self.root)

    def test_default_date_and_explicit_replacement_keep_original_semantics(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy2(REPO / "scripts/build_source_package.py", scripts)
        old = self.root / "novel-superpower-full-20261012.zip"
        old.write_bytes(b"previous dated release")
        unrelated = self.root / "notes.zip"
        unrelated.write_bytes(b"unrelated data")
        result = run_script("build_source_package.py", "--date", "20261013", repo=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(old.exists())
        result = run_script("build_source_package.py", "--date", "20261014", "--replace-existing", repo=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([item.name for item in builder.source_archives(self.root)],
                         ["novel-superpower-full-20261014.zip"])
        self.assertEqual(unrelated.read_bytes(), b"unrelated data")


if __name__ == "__main__":
    unittest.main()
