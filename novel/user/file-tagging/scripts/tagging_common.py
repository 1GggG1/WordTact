#!/usr/bin/env python3
"""Shared safe primitives for project-local tagging scripts."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


DEFAULT_CONFIG = Path("agent/tagging/config.yaml")
SIDE_SUFFIX = ".asset.md"
SEMANTIC_CATEGORIES = ("character", "org", "event", "concept", "location")
HIDDEN_OR_TOOL_DIRS = {".git", ".obsidian", ".codex", ".claude"}


class ConfigError(ValueError):
    """Raised when a project tagging configuration is unsafe or invalid."""


@dataclass(frozen=True)
class Context:
    root: Path
    config_path: Path
    config: dict[str, Any]
    apply: bool

    @property
    def project_id(self) -> str:
        return str(self.config["project"]["id"])


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", required=True, help="Explicit target project directory")
    parser.add_argument(
        "--config",
        help="Project-local YAML config; defaults to agent/tagging/config.yaml",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Write the reviewed changes")
    mode.add_argument("--dry-run", action="store_true", help="Preview only (the default)")


def resolve_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise ConfigError(f"project root is not a directory: {root}")
    return root


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def resolve_config_path(root: Path, raw: str | None) -> Path:
    path = Path(raw).expanduser() if raw else root / DEFAULT_CONFIG
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not is_within(path, root):
        raise ConfigError("config must live inside the target project")
    return path


def validate_relative_path(value: str, field: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ConfigError(f"{field} must be project-relative: {value}")
    return path.as_posix().strip("/")


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{field} must be a list of strings")
    return [validate_relative_path(item, field) for item in value if item]


def load_context(args: argparse.Namespace) -> tuple[Context | None, Path]:
    root = resolve_root(args.project_root)
    config_path = resolve_config_path(root, args.config)
    if not config_path.exists():
        return None, config_path
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ConfigError("config root must be a mapping")
    if data.get("schema_version") != 1:
        raise ConfigError("schema_version must be 1")
    project = data.get("project")
    if not isinstance(project, dict) or not project.get("id") or not project.get("root_name"):
        raise ConfigError("project.id and project.root_name are required")
    if str(project["root_name"]) != root.name:
        raise ConfigError(
            f"config root_name={project['root_name']!r} does not match target {root.name!r}"
        )
    layout = data.setdefault("layout", {})
    if not isinstance(layout, dict):
        raise ConfigError("layout must be a mapping")
    for field in ("active_dirs", "archive_dirs", "skill_dirs", "ignored_dirs"):
        layout[field] = _string_list(layout.get(field), f"layout.{field}")
    graph_dir = str(layout.get("graph_dir") or "graph")
    layout["graph_dir"] = validate_relative_path(graph_dir, "layout.graph_dir")
    for field in ("directory_types", "status_by_directory", "scope_by_directory"):
        mapping = layout.get(field) or {}
        if not isinstance(mapping, dict):
            raise ConfigError(f"layout.{field} must be a mapping")
        layout[field] = {
            validate_relative_path(str(key), f"layout.{field}"): str(value)
            for key, value in mapping.items()
        }
    files = data.setdefault("files", {})
    if not isinstance(files, dict):
        raise ConfigError("files must be a mapping")
    files.setdefault("text_extensions", [".md", ".txt"])
    files.setdefault("sidecar_extensions", [".pdf", ".docx", ".doc", ".zip"])
    for key in ("text_extensions", "sidecar_extensions"):
        values = files[key]
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise ConfigError(f"files.{key} must be a list of extensions")
        files[key] = [item.lower() if item.startswith(".") else f".{item.lower()}" for item in values]
    entities = data.setdefault("entities", {})
    if not isinstance(entities, dict):
        raise ConfigError("entities must be a mapping")
    for category in SEMANTIC_CATEGORIES:
        entries = entities.setdefault(category, [])
        if not isinstance(entries, list):
            raise ConfigError(f"entities.{category} must be a list")
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict) or not entry.get("id") or not entry.get("label"):
                raise ConfigError(f"entities.{category} entries require id and label")
            entity_id = str(entry["id"])
            if entity_id in seen:
                raise ConfigError(f"duplicate entities.{category} id: {entity_id}")
            seen.add(entity_id)
            aliases = entry.setdefault("aliases", [])
            if not isinstance(aliases, list) or not all(isinstance(item, str) for item in aliases):
                raise ConfigError(f"aliases for {category}/{entity_id} must be strings")
    return Context(root, config_path, data, bool(args.apply)), config_path


def diagnostic_proposal(root: Path) -> str:
    directories = sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name != "agent"
    )
    proposal = {
        "schema_version": 1,
        "project": {"id": "<confirm-project-id>", "root_name": root.name, "title": "<confirm-title>"},
        "layout": {
            "active_dirs": directories,
            "archive_dirs": [],
            "skill_dirs": [],
            "ignored_dirs": [".git", ".obsidian"],
            "graph_dir": "graph",
            "directory_types": {},
            "status_by_directory": {},
            "scope_by_directory": {},
        },
        "files": {
            "text_extensions": [".md", ".txt"],
            "sidecar_extensions": [".pdf", ".docx", ".doc", ".zip"],
        },
        "entities": {category: [] for category in SEMANTIC_CATEGORIES},
        "graph": {
            "category_labels": {category: category.title() for category in SEMANTIC_CATEGORIES},
            "main_documents": [],
        },
        "archive": {"title_overrides": {}, "preferred_paths": []},
    }
    return yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False, width=1000)


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def configured_roots(context: Context, fields: Iterable[str]) -> list[Path]:
    result: list[Path] = []
    layout = context.config["layout"]
    for field in fields:
        for item in layout.get(field, []):
            candidate = (context.root / item).resolve()
            if is_within(candidate, context.root) and candidate.exists():
                result.append(candidate)
    return result


def ignored(context: Context, path: Path) -> bool:
    rel_parts = path.relative_to(context.root).parts
    ignored_names = HIDDEN_OR_TOOL_DIRS | set(context.config["layout"].get("ignored_dirs", []))
    if any(part.startswith(".") for part in rel_parts):
        return True
    return any(part in ignored_names for part in rel_parts)


def iter_files(context: Context, fields: Iterable[str], extensions: set[str]) -> Iterable[Path]:
    roots = configured_roots(context, fields)
    seen: set[Path] = set()
    for base in roots:
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path in seen or ignored(context, path):
                continue
            if path.resolve() == context.config_path:
                continue
            if path.suffix.lower() in extensions or path.name.endswith(SIDE_SUFFIX):
                seen.add(path)
                yield path


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return {}, text
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, text
    data = yaml.safe_load("\n".join(lines[1:end])) or {}
    if not isinstance(data, dict):
        data = {}
    return data, "\n".join(lines[end + 1 :]).lstrip("\n")


def dump_markdown(frontmatter: dict[str, Any], body: str) -> str:
    rendered = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000).strip()
    return f"---\n{rendered}\n---\n\n{body.rstrip()}\n"


def write_if_apply(context: Context, path: Path, content: str) -> None:
    target = path.resolve()
    if not is_within(target, context.root):
        raise ConfigError(f"refusing write outside target: {target}")
    if context.apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def print_summary(kind: str, context: Context, changes: list[dict[str, Any]], **extra: Any) -> None:
    payload = {
        "operation": kind,
        "mode": "apply" if context.apply else "dry-run",
        "project_root": str(context.root),
        "config": relative(context.config_path, context.root),
        "changes": changes,
        **extra,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def first_heading(body: str) -> str | None:
    match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else None


def version_family(path: Path) -> str:
    name = path.name[: -len(SIDE_SUFFIX)] if path.name.endswith(SIDE_SUFFIX) else path.name
    stem = Path(name).stem
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}[_-]?", "", stem)
    stem = re.sub(r"[_\-\s]?v\d+(?:[._]\d+)?$", "", stem, flags=re.IGNORECASE)
    return stem.rstrip("_- ") or Path(name).stem


def semantic_tags(frontmatter: dict[str, Any]) -> dict[str, list[str]]:
    result = {category: [] for category in SEMANTIC_CATEGORIES}
    tags = frontmatter.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    for tag in tags:
        if not isinstance(tag, str) or "/" not in tag:
            continue
        prefix, value = tag.split("/", 1)
        if prefix in result and value and value not in result[prefix]:
            result[prefix].append(value)
    return result


def safe_component(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", "-", value).strip(". ")
    return cleaned or "unnamed"
