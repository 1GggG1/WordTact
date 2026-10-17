from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "user" / "file-tagging" / "scripts"


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run_script(name: str, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), "--project-root", str(root), *extra],
        text=True,
        capture_output=True,
        check=False,
    )


def write_project(root: Path, project_id: str, entity_id: str, label: str, alias: str) -> Path:
    (root / "manuscript").mkdir(parents=True)
    (root / "archive").mkdir()
    config = {
        "schema_version": 1,
        "project": {"id": project_id, "root_name": root.name, "title": f"Synthetic {project_id}"},
        "layout": {
            "active_dirs": ["manuscript"],
            "archive_dirs": ["archive"],
            "skill_dirs": [],
            "ignored_dirs": [".git", ".obsidian"],
            "graph_dir": "graph",
            "directory_types": {"manuscript": "manuscript", "archive": "manuscript"},
            "status_by_directory": {"manuscript": "active", "archive": "archived"},
            "scope_by_directory": {"manuscript": "main", "archive": "main"},
        },
        "files": {
            "text_extensions": [".md", ".txt"],
            "sidecar_extensions": [".pdf"],
        },
        "entities": {
            "character": [{"id": entity_id, "label": label, "aliases": [alias]}],
            "org": [],
            "event": [],
            "concept": [],
            "location": [],
        },
        "graph": {
            "category_labels": {
                "character": "Characters",
                "org": "Organizations",
                "event": "Events",
                "concept": "Concepts",
                "location": "Locations",
            },
            "main_documents": ["manuscript/opening.md"],
        },
        "archive": {"title_overrides": {}, "preferred_paths": []},
    }
    config_path = root / "agent" / "tagging" / "config.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return config_path


class FileTaggingIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="novel-tagging-")
        base = Path(self.temp.name)
        self.alpha = base / "synthetic-alpha"
        self.beta = base / "synthetic-beta"
        self.alpha.mkdir()
        self.beta.mkdir()
        self.alpha_config = write_project(self.alpha, "synthetic-alpha", "lead-a", "Aster", "Ari")
        self.beta_config = write_project(self.beta, "synthetic-beta", "lead-b", "贝塔", "小贝")
        (self.alpha / "manuscript" / "opening.md").write_text(
            "# Opening\n\nAri enters the observatory.\n",
            encoding="utf-8",
        )
        (self.beta / "manuscript" / "opening.md").write_text(
            "# 开场\n\n小贝走进温室。\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_missing_config_refuses_apply_and_dry_run_only_proposes(self) -> None:
        root = Path(self.temp.name) / "unconfigured"
        root.mkdir()
        before = tree_digest(root)
        preview = run_script("apply_project_tags.py", root, "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("configuration_proposal", preview.stdout)
        self.assertEqual(tree_digest(root), before)

        applied = run_script("apply_project_tags.py", root, "--apply")
        self.assertEqual(applied.returncode, 2)
        self.assertIn("refusing apply without confirmed config", applied.stderr)
        self.assertEqual(tree_digest(root), before)

    def test_dry_run_apply_isolation_and_idempotence(self) -> None:
        alpha_before = tree_digest(self.alpha)
        beta_before = tree_digest(self.beta)
        source_before = tree_digest(SCRIPTS)

        preview = run_script("apply_project_tags.py", self.alpha, "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        payload = json.loads(preview.stdout)
        self.assertGreater(payload["change_count"], 0)
        self.assertEqual(tree_digest(self.alpha), alpha_before)
        self.assertEqual(tree_digest(self.beta), beta_before)

        applied = run_script("apply_project_tags.py", self.alpha, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        alpha_text = (self.alpha / "manuscript" / "opening.md").read_text(encoding="utf-8")
        self.assertIn("project: synthetic-alpha", alpha_text)
        self.assertIn("character/lead-a", alpha_text)
        self.assertNotIn("lead-b", alpha_text)
        self.assertEqual(tree_digest(self.beta), beta_before)
        self.assertEqual(tree_digest(SCRIPTS), source_before)

        clean = run_script("apply_project_tags.py", self.alpha, "--dry-run")
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertEqual(json.loads(clean.stdout)["change_count"], 0)

        swapped = run_script(
            "apply_project_tags.py",
            self.alpha,
            "--config",
            str(self.beta_config),
            "--dry-run",
        )
        self.assertEqual(swapped.returncode, 2)
        self.assertIn("config must live inside the target project", swapped.stderr)

    def test_empty_active_dirs_do_not_fall_back_to_project_root(self) -> None:
        config = yaml.safe_load(self.alpha_config.read_text(encoding="utf-8"))
        config["layout"]["active_dirs"] = []
        self.alpha_config.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        unconfigured_note = self.alpha / "outside-configured-layout.md"
        original = "# Outside configured layout\n\nAster is mentioned here.\n"
        unconfigured_note.write_text(original, encoding="utf-8")

        result = run_script("apply_project_tags.py", self.alpha, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["changes"], [])
        self.assertEqual(unconfigured_note.read_text(encoding="utf-8"), original)

    def test_attachment_graph_and_archive_are_previewable(self) -> None:
        attachment = self.alpha / "manuscript" / "reference.pdf"
        attachment.write_bytes(b"synthetic-pdf-bytes")
        original_bytes = attachment.read_bytes()
        old = self.alpha / "archive" / "opening_v1.md"
        old.write_text(
            "---\n"
            "title: Opening old\n"
            "project: synthetic-alpha\n"
            "doc_type: manuscript\n"
            "status: archived\n"
            "version_family: opening\n"
            "tags:\n  - character/lead-a\n"
            "---\n\n# Opening old\n",
            encoding="utf-8",
        )

        applied = run_script("apply_project_tags.py", self.alpha, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        sidecar = self.alpha / "manuscript" / "reference.pdf.asset.md"
        self.assertTrue(sidecar.exists())
        self.assertEqual(attachment.read_bytes(), original_bytes)

        graph_before = tree_digest(self.alpha)
        graph_preview = run_script("build_graph_hubs.py", self.alpha, "--dry-run")
        self.assertEqual(graph_preview.returncode, 0, graph_preview.stderr)
        self.assertFalse((self.alpha / "graph").exists())
        self.assertEqual(tree_digest(self.alpha), graph_before)
        graph_apply = run_script("build_graph_hubs.py", self.alpha, "--apply")
        self.assertEqual(graph_apply.returncode, 0, graph_apply.stderr)
        self.assertTrue((self.alpha / "graph" / "overview.md").exists())
        graph_clean = run_script("build_graph_hubs.py", self.alpha, "--dry-run")
        self.assertEqual(json.loads(graph_clean.stdout)["changes"], [])

        archive_before = tree_digest(self.alpha)
        archive_preview = run_script("refresh_archive_graph.py", self.alpha, "--dry-run")
        self.assertEqual(archive_preview.returncode, 0, archive_preview.stderr)
        self.assertEqual(tree_digest(self.alpha), archive_before)
        archive_apply = run_script("refresh_archive_graph.py", self.alpha, "--apply")
        self.assertEqual(archive_apply.returncode, 0, archive_apply.stderr)
        self.assertIn("AUTO-ARCHIVE-LINKS", old.read_text(encoding="utf-8"))
        archive_clean = run_script("refresh_archive_graph.py", self.alpha, "--dry-run")
        self.assertEqual(json.loads(archive_clean.stdout)["changes"], [])


if __name__ == "__main__":
    unittest.main()
