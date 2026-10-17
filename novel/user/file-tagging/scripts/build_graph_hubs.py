#!/usr/bin/env python3
"""Preview or build project-configured semantic graph hubs."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tagging_common import (
    ConfigError,
    Context,
    SEMANTIC_CATEGORIES,
    add_common_arguments,
    diagnostic_proposal,
    dump_markdown,
    first_heading,
    iter_files,
    load_context,
    print_summary,
    read_markdown,
    relative,
    safe_component,
    semantic_tags,
    write_if_apply,
)


BLOCK_START = "<!-- AUTO-GRAPH-HUBS:START -->"
BLOCK_END = "<!-- AUTO-GRAPH-HUBS:END -->"


@dataclass
class Note:
    path: Path
    frontmatter: dict[str, Any]
    body: str
    tags: dict[str, list[str]]

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title") or first_heading(self.body) or self.path.stem)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(result)
    return result


def graph_settings(context: Context) -> tuple[Path, dict[str, str], list[str]]:
    graph = context.config.get("graph") or {}
    labels = graph.get("category_labels") or {}
    category_labels = {category: str(labels.get(category) or category.title()) for category in SEMANTIC_CATEGORIES}
    main_documents = graph.get("main_documents") or []
    if not isinstance(main_documents, list) or not all(isinstance(item, str) for item in main_documents):
        raise ConfigError("graph.main_documents must be a list of relative paths")
    root = (context.root / context.config["layout"]["graph_dir"]).resolve()
    return root, category_labels, main_documents


def wiki_target(path: Path, context: Context) -> str:
    value = relative(path, context.root)
    return value[:-3] if value.endswith(".md") else value


def wiki_link(path: Path, context: Context, label: str | None = None) -> str:
    target = wiki_target(path, context)
    return f"[[{target}|{label}]]" if label else f"[[{target}]]"


def load_notes(context: Context, graph_root: Path) -> list[Note]:
    notes: list[Note] = []
    for path in iter_files(context, ("active_dirs",), {".md"}):
        if path.resolve() == graph_root or graph_root in path.resolve().parents:
            continue
        frontmatter, body = read_markdown(path)
        notes.append(Note(path, frontmatter, body, semantic_tags(frontmatter)))
    return notes


def counts(notes: list[Note]) -> Counter[tuple[str, str]]:
    result: Counter[tuple[str, str]] = Counter()
    for note in notes:
        for category, values in note.tags.items():
            for value in values:
                result[(category, value)] += 1
    return result


def documents_by_entity(notes: list[Note]) -> dict[tuple[str, str], list[Note]]:
    result: dict[tuple[str, str], list[Note]] = defaultdict(list)
    for note in notes:
        for category, values in note.tags.items():
            for value in values:
                result[(category, value)].append(note)
    for related in result.values():
        related.sort(key=lambda note: note.path.as_posix())
    return result


def entity_path(graph_root: Path, labels: dict[str, str], category: str, value: str) -> Path:
    return graph_root / safe_component(labels[category]) / f"{safe_component(value)}.md"


def index_path(graph_root: Path, labels: dict[str, str], category: str) -> Path:
    return graph_root / f"{safe_component(labels[category])}.md"


def generated_frontmatter(context: Context, title: str, category: str) -> dict[str, Any]:
    return {
        "title": title,
        "project": context.project_id,
        "doc_type": "graph",
        "status": "generated",
        "category": category,
    }


def cooccurrence(
    entity: tuple[str, str],
    docs: list[Note],
) -> Counter[tuple[str, str]]:
    result: Counter[tuple[str, str]] = Counter()
    for note in docs:
        for category, values in note.tags.items():
            for value in values:
                other = (category, value)
                if other != entity:
                    result[other] += 1
    return result


def entity_content(
    context: Context,
    graph_root: Path,
    labels: dict[str, str],
    entity: tuple[str, str],
    docs: list[Note],
) -> str:
    category, value = entity
    related = cooccurrence(entity, docs).most_common(8)
    lines = [
        f"# {value}",
        "",
        f"- Category: {labels[category]}",
        f"- Index: {wiki_link(index_path(graph_root, labels, category), context, labels[category])}",
        "",
        "## Related documents",
    ]
    lines.extend(f"- {wiki_link(note.path, context, note.title)}" for note in docs[:12])
    if related:
        lines.extend(["", "## Co-occurring entities"])
        for (other_category, other_value), score in related:
            target = entity_path(graph_root, labels, other_category, other_value)
            lines.append(f"- {wiki_link(target, context, other_value)} ({score})")
    frontmatter = generated_frontmatter(context, value, category)
    frontmatter["tags"] = [f"{category}/{value}"]
    return dump_markdown(frontmatter, "\n".join(lines))


def index_content(
    context: Context,
    graph_root: Path,
    labels: dict[str, str],
    category: str,
    entity_counts: Counter[tuple[str, str]],
) -> str:
    values = sorted(
        (value for item_category, value in entity_counts if item_category == category),
        key=lambda value: (-entity_counts[(category, value)], value),
    )
    lines = [
        f"# {labels[category]}",
        "",
        f"- Overview: {wiki_link(graph_root / 'overview.md', context, 'Graph overview')}",
        "",
        "## Nodes",
    ]
    lines.extend(
        f"- {wiki_link(entity_path(graph_root, labels, category, value), context, value)}: "
        f"{entity_counts[(category, value)]} document(s)"
        for value in values
    )
    return dump_markdown(generated_frontmatter(context, labels[category], "graph-index"), "\n".join(lines))


def overview_content(
    context: Context,
    graph_root: Path,
    labels: dict[str, str],
    main_documents: list[str],
    entity_counts: Counter[tuple[str, str]],
) -> str:
    lines = ["# Graph overview", "", "## Main documents"]
    existing_main = []
    for item in main_documents:
        target = (context.root / item).resolve()
        if target.exists() and target.is_file():
            existing_main.append(f"- {wiki_link(target, context, target.stem)}")
    lines.extend(existing_main or ["- None configured"])
    lines.extend(["", "## Categories"])
    for category in SEMANTIC_CATEGORIES:
        total = sum(count for (item_category, _), count in entity_counts.items() if item_category == category)
        lines.append(f"- {wiki_link(index_path(graph_root, labels, category), context, labels[category])}: {total}")
    lines.extend(["", "## Most connected entities"])
    for (category, value), count in entity_counts.most_common(20):
        lines.append(f"- {wiki_link(entity_path(graph_root, labels, category, value), context, value)}: {count}")
    return dump_markdown(generated_frontmatter(context, "Graph overview", "graph-overview"), "\n".join(lines))


def strip_block(body: str) -> str:
    pattern = re.compile(
        r"\n*## Graph hubs\n" + re.escape(BLOCK_START) + r"\n.*?\n" + re.escape(BLOCK_END) + r"\n*",
        re.DOTALL,
    )
    return pattern.sub("\n\n", body).rstrip()


def attach_block(
    context: Context,
    graph_root: Path,
    labels: dict[str, str],
    note: Note,
) -> str:
    links = [f"- {wiki_link(graph_root / 'overview.md', context, 'Graph overview')}"]
    for category, values in note.tags.items():
        if values:
            links.append(f"- {wiki_link(index_path(graph_root, labels, category), context, labels[category])}")
        links.extend(
            f"- {wiki_link(entity_path(graph_root, labels, category, value), context, value)}"
            for value in values[:2]
        )
    links = list(dict.fromkeys(links))
    block = "\n".join(["## Graph hubs", BLOCK_START, *links, BLOCK_END])
    clean = strip_block(note.body)
    return f"{clean}\n\n{block}\n" if clean else f"{block}\n"


def planned_write(context: Context, path: Path, content: str, changes: list[dict[str, Any]]) -> None:
    old = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    if old == content:
        return
    changes.append({"action": "update" if path.exists() else "create", "path": relative(path, context.root)})
    write_if_apply(context, path, content)


def run(context: Context) -> None:
    graph_root, labels, main_documents = graph_settings(context)
    notes = load_notes(context, graph_root)
    entity_counts = counts(notes)
    docs_map = documents_by_entity(notes)
    changes: list[dict[str, Any]] = []
    desired_graph_paths: set[str] = set()

    overview_path = graph_root / "overview.md"
    desired_graph_paths.add(relative(overview_path, context.root))
    planned_write(
        context,
        overview_path,
        overview_content(context, graph_root, labels, main_documents, entity_counts),
        changes,
    )
    for category in SEMANTIC_CATEGORIES:
        category_path = index_path(graph_root, labels, category)
        desired_graph_paths.add(relative(category_path, context.root))
        planned_write(
            context,
            category_path,
            index_content(context, graph_root, labels, category, entity_counts),
            changes,
        )
    for entity, docs in sorted(docs_map.items()):
        node_path = entity_path(graph_root, labels, *entity)
        desired_graph_paths.add(relative(node_path, context.root))
        planned_write(
            context,
            node_path,
            entity_content(context, graph_root, labels, entity, docs),
            changes,
        )
    for note in notes:
        content = dump_markdown(note.frontmatter, attach_block(context, graph_root, labels, note))
        planned_write(context, note.path, content, changes)

    existing_graph = {
        relative(path, context.root)
        for path in graph_root.rglob("*.md")
        if path.is_file()
    } if graph_root.exists() else set()
    stale = sorted(existing_graph - desired_graph_paths)
    print_summary("build-graph-hubs", context, changes, stale_graph_notes=stale)


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
