# Project-local tagging schema

## Contents

1. Ownership and invariants
2. Configuration schema
3. Managed frontmatter
4. Semantic tags
5. Attachment sidecars
6. Graph and archive behavior
7. Synthetic example

## 1. Ownership and invariants

Store project-specific values only at `<project>/agent/tagging/config.yaml`. The reusable skill
owns field semantics and scripts; the project owns its title, directory layout, entities, aliases,
status mapping, graph entry points, and archive policy.

Required invariants:

- `schema_version` is `1`.
- `project.id` is a stable slug used in metadata.
- `project.root_name` exactly matches the target directory name.
- Every configured path is relative to the project root and contains no `..` component.
- Entity IDs are stable slugs. Display labels and aliases may change.
- Configuration proposals and inferred entities require user confirmation before write use.

## 2. Configuration schema

```yaml
schema_version: 1
project:
  id: <project-id>
  root_name: <project-directory-name>
  title: <display-title>

layout:
  active_dirs: [<manuscript-dir>, <outline-dir>, <canon-dir>]
  archive_dirs: [<archive-dir>]
  skill_dirs: [<project-skill-dir>]
  ignored_dirs: [.git, .obsidian, <backup-dir>]
  graph_dir: <graph-dir>
  directory_types:
    <manuscript-dir>: manuscript
    <outline-dir>: outline
    <canon-dir>: canon
  status_by_directory:
    <manuscript-dir>: active
    <archive-dir>: archived
  scope_by_directory:
    <manuscript-dir>: main

files:
  text_extensions: [.md, .txt]
  sidecar_extensions: [.pdf, .docx, .doc, .zip]

entities:
  character:
    - id: <character-id>
      label: <display-name>
      aliases: [<alias>]
  org: []
  event: []
  concept: []
  location: []

graph:
  category_labels:
    character: Characters
    org: Organizations
    event: Events
    concept: Concepts
    location: Locations
  main_documents: [<relative-note-path>]

archive:
  title_overrides: {}
  preferred_paths: []
```

`active_dirs`, `archive_dirs`, and `skill_dirs` may be empty. An empty `active_dirs` selects no
active files; it never falls back to scanning the whole project. Add explicit relative directories
after review. Do not put absolute paths, machine usernames, project data from another work, or
source-skill paths into this configuration.

## 3. Managed frontmatter

The tagging script may maintain these keys while preserving all other keys:

| Field | Meaning |
|---|---|
| `title` | First heading or filename-derived title |
| `project` | Stable `project.id`, not a hard-coded title |
| `doc_type` | Value derived from `layout.directory_types` or a conservative fallback |
| `story_scope` | Optional value from `layout.scope_by_directory` |
| `status` | Value from `layout.status_by_directory` or `needs-review` |
| `source_path` | Project-relative path |
| `file_ext` | Original file extension |
| `note_role` | `primary` or `attachment-index` |
| `version` / `version_source` | Filename/header evidence or `unversioned` / `none` |
| `version_family` | Filename with date/version suffixes removed |
| `date` / `date_source` | Filename/header evidence; filesystem date only when configured |
| `chapters` | Explicit chapter tokens found in title/heading |
| `mentioned_*` | Configured entity IDs evidenced in title/body |
| `tags` | Semantic tags and review markers owned by this workflow |

Do not overwrite unrelated fields such as skill `name`/`description`, author notes, publishing
metadata, or project-defined custom keys.

## 4. Semantic tags

Use stable IDs from the project configuration:

- `character/<character-id>`
- `org/<org-id>`
- `event/<event-id>`
- `concept/<concept-id>`
- `location/<location-id>`
- `chapter/<chapter-id>` when explicitly detected
- `meta/needs-review` for unresolved classification or attachment-only inference

Store document state in properties rather than duplicating it into `project/`, `status/`, `ext/`,
or date tags. Existing non-owned tags must be preserved.

## 5. Attachment sidecars

For a configured non-Markdown attachment, create `original-name.ext.asset.md` beside it. Keep the
body minimal: a link to the original, a statement that metadata lives in the sidecar, and the
inference mode. Never modify the attachment itself.

## 6. Graph and archive behavior

Graph hubs derive only from existing semantic tags. Project configuration supplies graph labels,
the graph destination, and optional main documents. Generated content must live between stable
markers so reruns preserve hand-written text.

Archive links are proposals based on `version_family`, chapter, document type, and semantic-tag
overlap. A weak filename resemblance is insufficient. Do not delete stale archive or graph files;
report them for user review.

## 7. Synthetic example

```yaml
---
title: <scene-title>
project: <project-id>
doc_type: manuscript
status: active
source_path: <manuscript-dir>/<scene-file>.md
version: unversioned
version_source: none
version_family: <scene-file>
chapters: [<chapter-id>]
mentioned_characters: [<character-id>]
tags:
  - chapter/<chapter-id>
  - character/<character-id>
---
```

Placeholders describe shape only. They are not defaults and must never appear in applied output.
