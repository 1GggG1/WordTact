---
name: vault-organizer
description: "Plan and safely execute project-agnostic organization of an Obsidian writing vault: inventory files and frontmatter, reconcile versions, propose a directory and metadata layout, preserve links, and produce a migration log. Use when a writing vault is disordered or its tags and properties conflict. Stop for approval after the migration plan; never assume a particular novel title, entity list, language, or directory scheme."
---

# Vault Organizer

Organize a user-specified writing vault while keeping project data in that vault. Do not embed the
project's title, characters, directories, or preferences in this skill.

## Non-negotiable boundary

Treat `<project>/agent/tagging/config.yaml` as the shared owner of project layout, controlled
entities, and metadata mappings. Read `../file-tagging/references/tag-schema.md` when that sibling
skill is available. Do not maintain a second project schema here.

Never move, rename, delete, or rewrite frontmatter before the user approves a concrete migration
plan. Approval of an audit is not approval to migrate.

## Stage 1: inventory without writes

Resolve the exact vault root, then record:

1. Every non-hidden file, its extension, relative path, size, and current frontmatter.
2. Existing directory roles and naming conventions.
3. Candidate version families, with evidence from filenames, headers, timestamps, and links.
4. Duplicate or conflicting frontmatter fields and tags.
5. Internal wiki/Markdown links that a move could affect.
6. Project-local skills, scripts, generated graphs, attachments, sidecars, and archive areas.
7. Existing Git or backup coverage without creating a new backup automatically.

Do not treat the newest filesystem timestamp as proof of the canonical version. Mark uncertain
families for user decision.

## Stage 2: propose a project-specific layout

Derive the smallest useful layout from the inventory. A project may use any language or folder
names. Recommend roles rather than fixed names:

```text
<project>/
  <active-manuscript>/
  <outlines>/
  <canon-or-setting>/
  <characters>/              # only when separate character files are useful
  <references>/
  <archive>/
  agent/
    tagging/config.yaml
    migrations/<migration-id>/
```

Reuse a coherent existing layout instead of renaming it merely to match this example. Put the
confirmed names into the shared tagging configuration.

## Stage 3: write the migration plan, then stop

Create the plan only in a user-approved project-side planning location. If none exists, propose
`<project>/agent/migrations/<migration-id>/plan.md` and ask before creating it.

The plan must contain:

- exact source → destination mappings;
- version-family decisions and unresolved choices;
- frontmatter additions, removals, and value translations;
- tag-to-property migrations;
- link updates required by every move;
- collision handling;
- rollback or recovery method appropriate to the actual environment;
- validation commands and expected counts.

Stop after presenting the plan. Do not interpret silence as approval.

## Stage 4: execute an approved plan

After explicit approval:

1. Re-read the vault and compare it with the inventory; stop if material drift changes the plan.
2. Confirm recovery coverage. Prefer Git or a scoped snapshot; never copy an unbounded vault into
   itself or invent a dated backup directory.
3. Create destination directories from the approved mapping.
4. Move one version family at a time, preserving all uncertain versions.
5. Merge frontmatter without overwriting unrelated keys.
6. Update only links affected by confirmed moves.
7. Run project tagging in dry-run mode and review its report before applying metadata changes.
8. Record each operation and its result in the project-side migration log.

Deletion is a separate authorization. Archive superseded files unless the user explicitly requests
and confirms exact deletion targets.

## Metadata model

Use properties for document identity and state, such as `title`, `project`, `doc_type`, `status`,
`version`, `chapter`, and `story_scope`. Use semantic tags for relationships such as character,
organization, event, concept, and location IDs defined by project configuration.

Do not force one universal field set. Preserve project fields that have a clear consumer. Propose
removal only when a field is redundant, unused, and covered by a confirmed replacement.

## Verification

After execution, prove:

- every planned source has exactly one intended destination;
- no unplanned file was moved, deleted, or rewritten;
- unresolved versions remain recoverable;
- all changed internal links resolve;
- frontmatter parses for every changed Markdown file;
- dry-run tagging is idempotent after any approved apply;
- the project-side configuration contains all project-specific values and the reusable skill source
  contains none;
- the migration log matches actual filesystem changes.
