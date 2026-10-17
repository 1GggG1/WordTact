---
name: novel-superpower
description: "Use when the user asks for Chinese novel-writing help across the bundled workflow: project setup, planning, scene cards, drafting, expanding outlines, brainstorming, reviewing and revising prose for language habits, style consistency, reader continuity and meaning, organizing a writing vault, or project file tagging. Trigger on 写小说、小说项目、讨论大纲、聊聊怎么写、扩写、写正文、审稿、检查 AI 感、统一中文小说文风、检查跨章措辞、更新正典、章节收口, or equivalent requests in English about Chinese fiction."
---

# 章回（Zhanghui）

Single entry dispatcher for the novel-writing skill suite. Use this file to choose the
right sub-skill, then load that sub-skill's `SKILL.md` and any references it requests.

## Dispatch Table

| User intent | Route |
|-------------|-------|
| Initialize or maintain a spec-driven novel project; produce scene cards, drafts, reviews, patches, regression checks, canon updates, or lockfile updates | `user/novel-ci/SKILL.md` |
| Brainstorm, discuss story direction, stress-test an outline, preserve disagreements, or prepare planning handoff minutes without producing manuscript prose | `user/novel-discuss/SKILL.md` |
| Expand outlines, notes, fragments, or scene cards into narrative prose | `user/novel-expander/SKILL.md` |
| Review Chinese prose for language, meaning, repetition or voice; unify novel style or check wording across chapters while preserving character and scene differences; perform authorized minimal edits; build language reference profiles or compare wording distributions | `user/novel-auditor/SKILL.md` |
| Add or maintain project frontmatter and tags in the local writing vault | `user/file-tagging/SKILL.md` |
| Organize an Obsidian writing vault's directory structure, frontmatter, and tag system | `user/vault-organizer/SKILL.md` |

## Routing Notes

- If the user wants to talk through how to write something, use `novel-discuss`, not
  `novel-ci` or `novel-expander`.
- If `novel-discuss` reaches a production decision, hand off through its minutes and
  handoff brief; `novel-ci` consumes that planning input later.
- If `novel-discuss` needs prose feel during discussion, delegate exploratory sketches
  to `novel-expander` and store them only under
  `agent/discuss/sessions/<session_id>/sketches/`.
- If the user supplies finished prose and asks what is wrong with it, use
  `novel-auditor`; if they supply notes and ask for prose, use `novel-expander`.
- Auditor first resolves the audit arrangement: a lightweight survey and a user-selected
  combination of methods, or an already established/delegated choice. Start with the project
  entry and file metadata; load auditor's planning route before other project evidence. Do not preload its
  full review rules before this routing step. Assigned audit workers execute their task;
  they do not reopen selection or recursively dispatch the suite.
- Reference-only language analysis routes to auditor without starting novel planning or requiring
  a scene card. Reference distributions support wording review, not narrative design or word quotas.
- This full suite targets Chinese fiction. Style consistency uses scoped author rules and approved
  samples; it preserves narrator, character and scene differences. English and academic prose need
  a separate workflow and are not capabilities promised by this suite.
- Resolve intent from supplied material and existing authorization first. Ask one concise question
  only if an unresolved choice changes the work substantially.

## Source Layout Note

This bundle keeps sub-skills under `user/<skill>/`. Installed project copies may use a
flatter `agent/skills/user/novel-superpower/<skill>/` layout, but this source package's
canonical references are the `user/<skill>/SKILL.md` paths above.

## Installed layouts and shared verification

Resolve each child under `user/<skill>/SKILL.md` in this source layout; when `user/` is absent,
resolve `<skill>/SKILL.md` in a flat installation. Relative sibling references inside child skills
work in either layout. Do not infer the novel project path from either installation location.

Ordinary expansion and the selected skills-based audit read novel-ci's
`references/project-context.md` without entering its scene-card pipeline. Audit reconnaissance
loads only task-resolution information; independent readers receive a separate minimal packet,
not the suite entrypoints or shared review rules. Language rules have one canonical owner in novel-expander. Actual edits
use frozen originals and proportional regression; unfinished mandatory checks remain
NEEDS_VERIFICATION. Reading, discussion and exploratory sketches do not claim manuscript acceptance.
