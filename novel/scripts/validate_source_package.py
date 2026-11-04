#!/usr/bin/env python3
"""Validate package shape, skill metadata, generality, and shared contracts."""

from __future__ import annotations

import argparse
import hashlib
import re
import stat
import sys
import zipfile
from pathlib import Path

import yaml

from build_source_package import PREFIX, is_macos_artifact, source_archives, source_files


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SUBSKILLS = [
    "file-tagging",
    "novel-auditor",
    "novel-ci",
    "novel-conversation",
    "novel-dialogue",
    "novel-discuss",
    "novel-expander",
    "vault-organizer",
]

FORBIDDEN_SUBSKILLS = {
    "conversational-register",
    "project-file-tagging",
}

PATH_CONTRACT_FILES = [
    "SKILL.md",
    "user/novel-discuss/SKILL.md",
    "user/novel-discuss/references/conventions.md",
    "user/novel-discuss/references/state-layout.md",
    "user/novel-discuss/references/workflow-session.md",
    "user/novel-discuss/references/register-discussion.md",
    "user/novel-expander/SKILL.md",
    "design/novel-discuss/README.md",
    "design/novel-discuss/blueprint.md",
    "design/novel-discuss/contracts.md",
    "design/novel-discuss/register-material.md",
    "design/novel-discuss/goals/wp1-skill-entry.md",
    "design/novel-discuss/goals/wp2-conventions-state.md",
]

FORBIDDEN_PATTERNS = [
    (re.compile(r"<project>/discuss/"), "use <project>/agent/discuss/"),
    (re.compile(r"(?<!agent/)discuss/sessions/"), "use agent/discuss/sessions/"),
    (re.compile(r"(?<!agent/)discuss/harness/"), "use agent/discuss/harness/"),
    (re.compile(r"(?<!agent/)discuss/harness/\*\.md"), "use agent/discuss/harness/*.md"),
    (re.compile(r"output_dir:\s+discuss/"), "use output_dir: agent/discuss/"),
    (re.compile(r"Default write target is `discuss/`"), "use agent/discuss/"),
    (re.compile(r"默认只写 `discuss/`"), "use agent/discuss/"),
    (re.compile(r"默认态(?:(?!agent/discuss/).)*discuss/"), "use agent/discuss/"),
    (re.compile(r"`discuss/` 全目录"), "use `agent/discuss/` 全目录"),
    (re.compile(r"create `discuss/`"), "use create `agent/discuss/`"),
    (re.compile(r"initialize\s+`discuss/`"), "use initialize `agent/discuss/`"),
    (re.compile(r"创建\s+`?discuss/`?"), "use 创建 agent/discuss/"),
]

ALLOWED_SKILL_KEYS = {"name", "description", "metadata", "license", "allowed-tools"}

GENERICITY_PATTERNS = [
    (re.compile(r"\bconversational-register\b"), "personal register dependency"),
    (re.compile(r"\bproject-file-tagging\b"), "archived project skill dependency"),
    (re.compile(r"\b(?:Claude|ChatGPT|OpenAI|GPT)\b"), "provider-specific model or product name"),
    (re.compile(r"/(?:Users|home)/[^/\s`]+/"), "absolute user-home path"),
    (re.compile(r"参考副本"), "legacy reference-copy route"),
    (re.compile(r"backup[-_/]?\d{8}", re.IGNORECASE), "dated backup path"),
]


NARRATIVE_REQUIRED_MARKERS = {
    "user/novel-ci/references/workflow-planning.md": [
        "stakes:",
        "change_chain:",
        "time_handling:",
        "dialogue_dynamics:",
        "attention_filter:",
        "embodied_by:",
        "emergent_patterns:",
    ],
    "user/novel-ci/references/workflow-draft.md": [
        "references/narrative-craft.md",
        "`change_chain`",
        "`dialogue_dynamics`",
        "`time_handling`",
        "`turn.embodied_by`",
    ],
    "user/novel-ci/references/checks-structure.md": [
        "Module 6: narrative_delivery_tests",
        "不得按感官数",
    ],
    "user/novel-ci/references/workflow-review.md": [
        "narrative_delivery: PASS",
        "External feedback translation",
    ],
    "user/novel-ci/references/workflow-chapter.md": [
        "emergent_patterns discipline",
        "does not decide",
    ],
}

FORBIDDEN_CRAFT_QUOTAS = [
    "一个场景最多调动两个感官",
    "一页之内最多一个比喻",
    "砍到 2 个",
    "砍到 1 个或 0 个",
]

SCRIPT_STATE_PATTERNS = [
    (re.compile(r"^ROOT\s*=\s*Path\(__file__\).*parents\[3\]", re.MULTILINE), "inferred project root"),
    (re.compile(r"^PROJECT\s*=", re.MULTILINE), "hard-coded project identifier"),
    (
        re.compile(
            r"^(?:CHARACTERS|ORGS|EVENTS|CONCEPTS|LOCATIONS|TITLE_OVERRIDES|PREFERRED_SETTING_ORDER)\s*=",
            re.MULTILINE,
        ),
        "hard-coded project vocabulary or path map",
    ),
]


def frontmatter(markdown: str) -> dict[str, object]:
    if not markdown.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    try:
        _, raw, _ = markdown.split("---", 2)
    except ValueError as exc:
        raise ValueError("unterminated YAML frontmatter") from exc
    values = yaml.safe_load(raw) or {}
    if not isinstance(values, dict):
        raise ValueError("frontmatter must be a mapping")
    return values




def check_root_skill(errors: list[str]) -> None:
    skill_path = ROOT / "SKILL.md"
    if not skill_path.exists():
        errors.append("missing root SKILL.md")
        return

    text = skill_path.read_text(encoding="utf-8")
    try:
        metadata = frontmatter(text)
    except ValueError as exc:
        errors.append(f"SKILL.md: {exc}")
        metadata = {}

    if metadata.get("name") != "novel-superpower":
        errors.append("SKILL.md frontmatter name must be novel-superpower")
    if not metadata.get("description"):
        errors.append("SKILL.md frontmatter description is required")

    for skill in REQUIRED_SUBSKILLS:
        rel = f"user/{skill}/SKILL.md"
        if not (ROOT / rel).exists():
            errors.append(f"missing subskill path {rel}")
        if rel not in text:
            errors.append(f"SKILL.md dispatcher must reference {rel}")

    user_dir = ROOT / "user"
    published = sorted(
        path.name for path in user_dir.iterdir() if path.is_dir() and not path.name.startswith(".")
    )
    if published != sorted(REQUIRED_SUBSKILLS):
        errors.append(
            "published subskills must exactly match allow-list: "
            f"expected={sorted(REQUIRED_SUBSKILLS)} actual={published}"
        )
    for skill in FORBIDDEN_SUBSKILLS:
        rel = f"user/{skill}/SKILL.md"
        if rel in text or (ROOT / "user" / skill).exists():
            errors.append(f"non-publishable subskill remains: {skill}")

    if "agent/discuss/sessions/<session_id>/" not in text:
        errors.append("SKILL.md must document agent/discuss/sessions/<session_id>/")


def check_skill_metadata(errors: list[str]) -> None:
    skill_paths = [ROOT / "SKILL.md", *(ROOT / "user" / name / "SKILL.md" for name in REQUIRED_SUBSKILLS)]
    for path in skill_paths:
        rel = path.relative_to(ROOT).as_posix()
        try:
            metadata = frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{rel}: invalid frontmatter: {exc}")
            continue
        extras = sorted(set(metadata) - ALLOWED_SKILL_KEYS)
        if extras:
            errors.append(f"{rel}: unexpected frontmatter keys: {extras}")
        expected_name = "novel-superpower" if path == ROOT / "SKILL.md" else path.parent.name
        if metadata.get("name") != expected_name:
            errors.append(f"{rel}: name must match folder ({expected_name})")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{rel}: description is required")
        elif len(description) > 1024:
            errors.append(f"{rel}: description exceeds 1024 characters")


def text_files_for_generality() -> list[Path]:
    paths = [ROOT / "SKILL.md"]
    for base in (ROOT / "user", ROOT / "design" / "novel-ci", ROOT / "design" / "novel-discuss"):
        if base.exists():
            paths.extend(path for path in base.rglob("*") if path.is_file() and path.suffix in {".md", ".py", ".yaml", ".yml"})
    return sorted(set(paths))


def check_generality(errors: list[str]) -> None:
    for path in text_files_for_generality():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, label in GENERICITY_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line}: {label}")

    for path in sorted((ROOT / "user").glob("*/scripts/*.py")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, label in SCRIPT_STATE_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(ROOT)}:{line}: {label}")
        if path.parent.parent.name == "file-tagging" and path.name != "tagging_common.py":
            for required in ("add_common_arguments", "load_context"):
                if required not in text:
                    errors.append(f"{path.relative_to(ROOT)}: missing safe interface {required}")


def check_shared_files(errors: list[str], skill_root: Path | None = None) -> None:
    """Check a single rule owner and executable references in either install layout."""
    base = skill_root if skill_root is not None else ROOT / "user"
    expander = base / "novel-expander" / "references" / "anti-ai-patterns.md"
    auditor = base / "novel-auditor" / "references" / "anti-ai-patterns.md"
    if not expander.exists() or not auditor.exists():
        errors.append("canonical language rules and auditor compatibility entry must exist")
        return
    owner_text = expander.read_text(encoding="utf-8")
    forward_text = auditor.read_text(encoding="utf-8")
    expected_link = "../../novel-expander/references/anti-ai-patterns.md"
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", forward_text)
    if links.count(expected_link) != 1 or (auditor.parent / expected_link).resolve() != expander.resolve():
        errors.append("auditor compatibility entry must link to the sole expander rule owner")
    if forward_text == owner_text or len(forward_text.splitlines()) > 30:
        errors.append("auditor compatibility entry must forward, not duplicate language rules")
    for skill in ("novel-auditor", "novel-expander"):
        entry = base / skill / "SKILL.md"
        if not entry.exists():
            errors.append(f"missing language rule consumer: {skill}/SKILL.md")
            continue
        text = entry.read_text(encoding="utf-8")
        if not re.search(r"(?:Read|读取|阅读)[^\n]*references/anti-ai-patterns\.md", text):
            errors.append(f"{skill}/SKILL.md must instruct loading references/anti-ai-patterns.md")
        if not (entry.parent / "references/anti-ai-patterns.md").is_file():
            errors.append(f"{skill}/SKILL.md language rule reference does not resolve")

    for relative in ("references/style-reference.md", "references/style-consistency.md",
                     "references/reading-load-zh.md", "scripts/style_reference.py", "scripts/language_scan.py"):
        if not (base / "novel-auditor" / relative).is_file():
            errors.append(f"missing language reference resource: novel-auditor/{relative}")
    for relative in ("references/humanizer-fiction.md", "THIRD_PARTY_NOTICES.md"):
        if not (base / "novel-expander" / relative).is_file():
            errors.append(f"missing language reference resource: novel-expander/{relative}")
    if "humanizer-fiction.md" not in owner_text:
        errors.append("canonical language rules must route Humanizer fiction checks")
    for skill in ("novel-auditor", "novel-expander"):
        entry = base / skill / "SKILL.md"
        if entry.is_file() and "references/style-reference.md" not in entry.read_text(encoding="utf-8"):
            errors.append(f"{skill}/SKILL.md must route applicable reference comparison")


def check_conversation_routes(errors: list[str], skill_root: Path | None = None) -> None:
    """Keep author communication and character speech reachable in either layout."""
    base = skill_root if skill_root is not None else ROOT / "user"
    consumers = {
        "novel-conversation": [
            "novel-ci/SKILL.md",
            "novel-discuss/SKILL.md",
            "novel-expander/SKILL.md",
            "novel-auditor/SKILL.md",
            "novel-discuss/references/register-discussion.md",
        ],
        "novel-dialogue": [
            "novel-expander/SKILL.md",
            "novel-auditor/SKILL.md",
            "novel-ci/references/workflow-draft.md",
            "novel-ci/references/workflow-planning.md",
            "novel-ci/references/checks-character.md",
            "novel-expander/references/narrative-craft.md",
            "novel-discuss/references/workflow-session.md",
        ],
    }
    for skill, paths in consumers.items():
        target = base / skill / "SKILL.md"
        if not target.is_file():
            errors.append(f"missing conversation resource: {skill}/SKILL.md")
        for relative in paths:
            consumer = base / relative
            if not consumer.is_file():
                errors.append(f"missing conversation consumer: {relative}")
                continue
            links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", consumer.read_text(encoding="utf-8"))
            resolved = {(consumer.parent / link.split("#", 1)[0]).resolve() for link in links}
            if target.resolve() not in resolved:
                errors.append(f"{relative} must link to bundled {skill}/SKILL.md")


def check_narrative_contract(errors: list[str]) -> None:
    craft = ROOT / "user" / "novel-expander" / "references" / "narrative-craft.md"
    if not craft.exists():
        errors.append("missing narrative-craft.md")
    else:
        craft_text = craft.read_text(encoding="utf-8")
        for number in range(1, 7):
            if not re.search(rf"^## {number}\. ", craft_text, re.MULTILINE):
                errors.append(f"narrative-craft.md missing module {number}")

    expander_skill = ROOT / "user" / "novel-expander" / "SKILL.md"
    if craft.exists() and "references/narrative-craft.md" not in expander_skill.read_text(encoding="utf-8"):
        errors.append("novel-expander must reference narrative-craft.md")

    for rel, markers in NARRATIVE_REQUIRED_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing narrative contract file {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{rel}: missing narrative contract marker {marker!r}")

    structure_checks = sorted(
        path.name for path in (ROOT / "user" / "novel-ci" / "references").glob("checks-*.md")
    )
    expected_checks = ["checks-canon.md", "checks-character.md", "checks-genre.md", "checks-structure.md"]
    if structure_checks != expected_checks:
        errors.append(
            "novel-ci checks files must remain physically grouped into four files: "
            f"expected={expected_checks} actual={structure_checks}"
        )

    owner_patterns = {
        "scene_card": "workflow-planning.md",
        "chapter_arc": "workflow-planning.md",
        "review_report": "workflow-review.md",
    }
    reference_dir = ROOT / "user" / "novel-ci" / "references"
    for schema, owner in owner_patterns.items():
        holders = []
        pattern = re.compile(rf"^{schema}:\s*$", re.MULTILINE)
        for path in sorted(reference_dir.glob("*.md")):
            if pattern.search(path.read_text(encoding="utf-8")):
                holders.append(path.name)
        if holders != [owner]:
            errors.append(f"schema {schema} must be defined only in {owner}; found={holders}")

    for rel in (
        "user/novel-expander/references/anti-ai-patterns.md",
        "user/novel-auditor/references/anti-ai-patterns.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for quota in FORBIDDEN_CRAFT_QUOTAS:
            if quota in text:
                errors.append(f"{rel}: hard craft quota remains: {quota}")


def check_archive(errors: list[str], archive: Path | None = None) -> None:
    if archive is None:
        archives = source_archives(ROOT)
        if not archives:
            errors.append("missing dated release archive novel-superpower-full-YYYYMMDD.zip")
            return
        if len(archives) != 1:
            names = [path.name for path in archives]
            errors.append(f"expected exactly one dated release archive; found={names}; use --archive")
            return
        archive = archives[0]

    try:
        source_by_name = {
            f"{PREFIX}/{path.relative_to(ROOT).as_posix()}": path for path in source_files(ROOT)
        }
        expected = set(source_by_name)
        with zipfile.ZipFile(archive) as package:
            bad_member = package.testzip()
            if bad_member:
                errors.append(f"archive CRC failure: {bad_member}")

            members = [name for name in package.namelist() if not name.endswith("/")]
            actual = set(members)
            if len(members) != len(actual):
                errors.append("archive contains duplicate file entries")
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                errors.append(f"archive file list differs from source: missing={missing} extra={extra}")

            for info in package.infolist():
                name = info.filename
                path = Path(name)
                if path.is_absolute() or ".." in path.parts or not name.startswith(f"{PREFIX}/"):
                    errors.append(f"unsafe archive member path: {name}")
                if is_macos_artifact(path):
                    errors.append(f"archive contains macOS metadata: {name}")
                if f"{PREFIX}/user/conversational-register/" in name:
                    errors.append(f"archive contains removed personal skill: {name}")
                if f"{PREFIX}/user/project-file-tagging/" in name:
                    errors.append(f"archive contains removed project skill: {name}")
                mode = info.external_attr >> 16
                if info.is_dir() or not stat.S_ISREG(mode) or info.create_system != 3:
                    errors.append(f"archive member must be a regular Unix file: {name}")
                if info.date_time != (1980, 1, 1, 0, 0, 0):
                    errors.append(f"archive timestamp is not deterministic: {name}")
                source = source_by_name.get(name)
                if source is not None:
                    if stat.S_IMODE(mode) != stat.S_IMODE(source.stat().st_mode):
                        errors.append(f"archive permissions differ from source: {name}")
                    if hashlib.sha256(package.read(info)).digest() != hashlib.sha256(source.read_bytes()).digest():
                        errors.append(f"archive content differs from source: {name}")

            scoped_prefixes = (
                f"{PREFIX}/user/",
                f"{PREFIX}/design/novel-ci/",
                f"{PREFIX}/design/novel-discuss/",
            )
            text_suffixes = {".md", ".py", ".yaml", ".yml"}
            for name in members:
                if name != f"{PREFIX}/SKILL.md" and not name.startswith(scoped_prefixes):
                    continue
                if Path(name).suffix not in text_suffixes:
                    continue
                text = package.read(name).decode("utf-8", errors="ignore")
                for pattern, label in GENERICITY_PATTERNS:
                    match = pattern.search(text)
                    if match:
                        line = text.count("\n", 0, match.start()) + 1
                        errors.append(f"archive:{name}:{line}: {label}")
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        errors.append(f"invalid source archive: {exc}")


def check_discuss_contract(errors: list[str]) -> None:
    if (ROOT / "agent" / "discuss").exists():
        errors.append("source package must not contain runtime directory agent/discuss/")

    for rel in PATH_CONTRACT_FILES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing path contract file {rel}")
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern, replacement in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{rel}:{lineno}: stale discuss path; {replacement}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    archive_group = parser.add_mutually_exclusive_group()
    archive_group.add_argument(
        "--skip-archive",
        action="store_true",
        help="validate an extracted install tree that intentionally does not contain its source archive",
    )
    archive_group.add_argument(
        "--archive", type=Path,
        help="validate this fresh archive against current source, preserving legacy archives",
    )
    args = parser.parse_args()

    errors: list[str] = []
    check_root_skill(errors)
    check_skill_metadata(errors)
    check_discuss_contract(errors)
    check_generality(errors)
    check_shared_files(errors)
    check_conversation_routes(errors)
    check_narrative_contract(errors)
    if not args.skip_archive:
        check_archive(errors, args.archive)
    if errors:
        print("Source package validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Source package validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
