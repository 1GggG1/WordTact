---
name: file-tagging
description: "Maintain project-local frontmatter, semantic tags, attachment sidecars, graph hubs, and archive links for a writing vault. Use when a user asks to tag, index, graph, or reconcile files in a specified novel project. Require an explicit project root, keep project vocabulary in that project's agent/tagging/config.yaml, preview by default, and write only after explicit approval."
---

# File Tagging

Maintain metadata for one user-specified writing project without storing that project's title,
entities, paths, or preferences in this skill.

## Load first

Read `references/tag-schema.md` before creating or changing a project tagging configuration.
Treat `<project>/agent/tagging/config.yaml` as the only owner of project-specific tagging data.

## Safety contract

1. Require `--project-root`; never infer the target from the script location.
2. Resolve and echo the target before scanning.
3. Default every script to dry-run. Write only with explicit `--apply`.
4. Require the configuration to live inside the target project and verify its declared
   `root_name` against the actual root directory.
5. Preserve unmanaged frontmatter keys and manuscript body text.
6. Do not scan hidden directories, configured ignored directories, or paths outside the target.
7. Treat entity detection as evidence-based: add only configured aliases that appear in the
   title or readable text. Never infer entities from memory.
8. Do not delete stale graph notes or archived files automatically. Report them for review.

## Configure a project

If `<project>/agent/tagging/config.yaml` does not exist, run a dry diagnostic:

```text
python3 <skill>/scripts/apply_project_tags.py --project-root <project> --dry-run
```

The script prints a configuration proposal based on top-level directories. Review and write that
proposal into the project only after user confirmation. Fill controlled entities, aliases, layout,
and status/type mappings from project evidence or confirmed canon. Never write the proposal back
into this skill.

## Apply metadata

Preview:

```text
python3 <skill>/scripts/apply_project_tags.py \
  --project-root <project> \
  --config <project>/agent/tagging/config.yaml \
  --dry-run
```

After reviewing the reported paths, repeat with `--apply`. Markdown files receive merged
frontmatter. Configured binary/text attachments receive adjacent `.asset.md` sidecars; original
attachments are not modified.

## Build graph hubs

Use `scripts/build_graph_hubs.py` with the same root, config, and dry-run/apply discipline. Graph
categories and destination directories come from project configuration. The script creates or
updates generated hub blocks but does not delete unreferenced graph notes.

## Refresh archive links

Use `scripts/refresh_archive_graph.py` to propose current/archive relationships from confirmed
metadata such as `version_family`, chapter, document type, and semantic tags. Treat uncertain
matches as report-only; only sufficiently supported matches enter generated blocks on `--apply`.

## Completion checks

- Confirm dry-run changed no file hashes.
- Confirm every applied path appeared in the preview.
- Confirm the skill source tree stayed byte-identical.
- Confirm no entity from another project entered the target configuration or output.
- Re-run the relevant script in dry-run mode; it should report zero pending changes.
