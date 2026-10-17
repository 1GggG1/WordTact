#!/usr/bin/env python3
"""Preview or apply project-local frontmatter and attachment sidecars."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from tagging_common import (
    ConfigError,
    Context,
    SEMANTIC_CATEGORIES,
    SIDE_SUFFIX,
    add_common_arguments,
    diagnostic_proposal,
    dump_markdown,
    first_heading,
    iter_files,
    load_context,
    print_summary,
    read_markdown,
    relative,
    version_family,
    write_if_apply,
)


MANAGED_FIELDS = (
    "title",
    "project",
    "doc_type",
    "story_scope",
    "status",
    "source_path",
    "file_ext",
    "note_role",
    "version",
    "version_source",
    "version_family",
    "date",
    "date_source",
    "chapters",
    "mentioned_characters",
    "mentioned_orgs",
    "mentioned_events",
    "mentioned_concepts",
    "mentioned_locations",
    "tags",
)
VERSION_RE = re.compile(r"(?P<version>v\d+(?:[._]\d+)?)", re.IGNORECASE)
DATE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
CHAPTER_PATTERNS = (
    re.compile(r"第[一二三四五六七八九十百零〇两\d]+章"),
    re.compile(r"\bchapter[\s_-]*(\d+)\b", re.IGNORECASE),
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(result)
    return result


def mapping_value(mapping: dict[str, str], rel: str, fallback: str) -> str:
    for prefix in sorted(mapping, key=len, reverse=True):
        if rel == prefix or rel.startswith(f"{prefix}/"):
            return mapping[prefix]
    return fallback


def extract_version(path: Path, body: str) -> tuple[str, str]:
    match = VERSION_RE.search(path.stem)
    if match:
        return match.group("version").lower().replace("_", "."), "filename"
    match = VERSION_RE.search("\n".join(body.splitlines()[:40]))
    if match:
        return match.group("version").lower().replace("_", "."), "header"
    return "unversioned", "none"


def extract_date(context: Context, path: Path, body: str) -> tuple[str | None, str]:
    match = DATE_RE.search(path.name)
    if match:
        return match.group("date"), "filename"
    match = DATE_RE.search("\n".join(body.splitlines()[:60]))
    if match:
        return match.group("date"), "header"
    metadata = context.config.get("metadata") or {}
    if metadata.get("use_filesystem_date"):
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"), "filesystem"
    return None, "none"


def extract_chapters(path: Path, body: str) -> list[str]:
    sample = f"{path.stem}\n{first_heading(body) or ''}"
    found: list[str] = []
    for pattern in CHAPTER_PATTERNS:
        for match in pattern.finditer(sample):
            value = match.group(0) if pattern.groups == 0 else f"chapter-{match.group(1)}"
            if value not in found:
                found.append(value)
    return found


def detect_entities(context: Context, text: str) -> dict[str, list[str]]:
    found = {category: [] for category in SEMANTIC_CATEGORIES}
    for category in SEMANTIC_CATEGORIES:
        for entry in context.config["entities"].get(category, []):
            terms = [str(entry["label"]), *[str(item) for item in entry.get("aliases", [])]]
            if any(term and term in text for term in terms):
                found[category].append(str(entry["id"]))
    return found


def owned_tags(metadata: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for chapter in metadata["chapters"]:
        result.append(f"chapter/{chapter}")
    field_by_category = {
        "character": "mentioned_characters",
        "org": "mentioned_orgs",
        "event": "mentioned_events",
        "concept": "mentioned_concepts",
        "location": "mentioned_locations",
    }
    for category, field in field_by_category.items():
        result.extend(f"{category}/{item}" for item in metadata[field])
    if metadata["status"] == "needs-review" or metadata["note_role"] == "attachment-index":
        result.append("meta/needs-review")
    return list(dict.fromkeys(result))


def merge_tags(existing: Any, generated: list[str]) -> list[str]:
    values = [existing] if isinstance(existing, str) else list(existing or [])
    owned_prefixes = tuple(f"{item}/" for item in (*SEMANTIC_CATEGORIES, "chapter", "meta"))
    preserved = [item for item in values if isinstance(item, str) and not item.startswith(owned_prefixes)]
    return list(dict.fromkeys([*preserved, *generated]))


def metadata_for(
    context: Context,
    path: Path,
    body: str,
    existing: dict[str, Any],
    *,
    original: Path | None = None,
) -> dict[str, Any]:
    source = original or path
    rel = relative(source, context.root)
    layout = context.config["layout"]
    doc_type = mapping_value(layout["directory_types"], rel, "note")
    status = mapping_value(layout["status_by_directory"], rel, "needs-review")
    story_scope = mapping_value(layout["scope_by_directory"], rel, "unspecified")
    evidence = f"{source.name}\n{first_heading(body) or ''}\n{body if original is None else ''}"
    entities = detect_entities(context, evidence)
    version, version_source = extract_version(source, body)
    date, date_source = extract_date(context, source, body)
    chapters = extract_chapters(source, body)
    result: dict[str, Any] = {
        "title": first_heading(body) or source.stem,
        "project": context.project_id,
        "doc_type": doc_type,
        "story_scope": story_scope,
        "status": status,
        "source_path": rel,
        "file_ext": source.suffix.lower().lstrip(".") or "md",
        "note_role": "attachment-index" if original is not None else "primary",
        "version": version,
        "version_source": version_source,
        "version_family": version_family(source),
        "date_source": date_source,
        "chapters": chapters,
        "mentioned_characters": entities["character"],
        "mentioned_orgs": entities["org"],
        "mentioned_events": entities["event"],
        "mentioned_concepts": entities["concept"],
        "mentioned_locations": entities["location"],
    }
    if date:
        result["date"] = date
    elif "date" in existing:
        result["date"] = existing["date"]
    result["tags"] = merge_tags(existing.get("tags"), owned_tags(result))
    return result


def merge_frontmatter(existing: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    result = dict(existing)
    for field in MANAGED_FIELDS:
        if field in metadata:
            result[field] = metadata[field]
        elif field == "date" and field in result:
            continue
    return result


def sidecar_body(original: Path, context: Context) -> str:
    rel = relative(original, context.root)
    return (
        f"# {original.name} attachment index\n\n"
        f"- Original: [[{rel}|{original.name}]]\n"
        "- Metadata and semantic tags are maintained in this sidecar.\n"
        "- inference_mode: filename-only; review required\n"
    )


def plan_markdown(context: Context, path: Path, changes: list[dict[str, Any]]) -> None:
    existing, body = read_markdown(path)
    metadata = metadata_for(context, path, body, existing)
    content = dump_markdown(merge_frontmatter(existing, metadata), body)
    old = path.read_text(encoding="utf-8", errors="ignore")
    if content != old:
        changes.append({"action": "update", "path": relative(path, context.root)})
        write_if_apply(context, path, content)


def plan_sidecar(context: Context, original: Path, changes: list[dict[str, Any]]) -> None:
    sidecar = original.with_name(f"{original.name}{SIDE_SUFFIX}")
    existing: dict[str, Any] = {}
    body = sidecar_body(original, context)
    if sidecar.exists():
        existing, existing_body = read_markdown(sidecar)
        body = existing_body or body
    metadata = metadata_for(context, sidecar, body, existing, original=original)
    content = dump_markdown(merge_frontmatter(existing, metadata), body)
    old = sidecar.read_text(encoding="utf-8", errors="ignore") if sidecar.exists() else ""
    if content != old:
        changes.append(
            {"action": "update" if sidecar.exists() else "create", "path": relative(sidecar, context.root)}
        )
        write_if_apply(context, sidecar, content)


def run(context: Context) -> None:
    files = context.config["files"]
    text_extensions = set(files["text_extensions"])
    attachment_extensions = set(files["sidecar_extensions"]) | (text_extensions - {".md"})
    extensions = text_extensions | attachment_extensions
    changes: list[dict[str, Any]] = []
    for path in iter_files(context, ("active_dirs",), extensions):
        if path.name.endswith(SIDE_SUFFIX):
            plan_markdown(context, path, changes)
        elif path.suffix.lower() == ".md":
            plan_markdown(context, path, changes)
        elif path.suffix.lower() in attachment_extensions:
            plan_sidecar(context, path, changes)
    print_summary("apply-project-tags", context, changes, change_count=len(changes))


def main() -> int:
    args = parser().parse_args()
    try:
        context, config_path = load_context(args)
        if context is None:
            root = Path(args.project_root).expanduser().resolve()
            if args.apply:
                raise ConfigError(f"refusing apply without confirmed config: {config_path}")
            print(f"project_root={root}")
            print(f"config_missing={config_path}")
            print("configuration_proposal:")
            print(diagnostic_proposal(root), end="")
            return 0
        run(context)
        return 0
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
