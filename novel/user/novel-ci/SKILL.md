---
name: novel-ci
description: "Spec-driven novel writing pipeline: scene_card → draft → review → patch → regression → lockfile. Trigger on 新建小说项目、初始化设定库、规划章节、设计场景、scene card、写下一场、跑 review、自审、修补、打 patch、回归检查、更新正典、更新 lockfile、连续写、章节收口, or English equivalents. Routing: freeform outline to prose with no CI state routes to novel-expander. Discussing, brainstorming, or deciding an outline/writing approach rather than producing prose routes to novel-discuss; novel-discuss handoff minutes are valid planning input. Finished prose diagnosis routes to novel-auditor. Project state, scene specs, tests, patches, or lockfile maintenance routes here."
---

# Novel CI

## Core principles

1. 先规格后正文。Every scene must have a confirmed `scene_card` before drafting.
2. 先 card 后 draft。Without a confirmed card, do not enter draft generation.
3. 正文后必测。Every draft must pass through `workflow-review` before a scene is considered complete.
4. 已执行测试输出 PASS / FAIL / RISK；未执行写 SKIPPED，必验项缺失写 NEEDS_VERIFICATION。No scores, no vague evaluations, no "整体不错".
5. Failure 必标 P0—P3。Every failure entry carries a severity level per the severity system.
6. 默认局部 patch。Default repair strategy is local patch; full rewrite only when P0 and local cannot fix.
7. 语言打磨不破坏角色声音。P2 language polish must not alter character voice, facts, motivation, or information access.
8. 修改后必回归。Every patch must pass regression check before the scene is accepted.
9. 通过后才更新 lockfile。Only ACCEPTED scenes write to the lockfile (Gate D).
10. P0/P1 未清不进下一场景。P0 or P1 unresolved through Gate B/C = do not proceed to next scene.

---

## Pipeline overview

```text
Read canon state → scene_card → [Gate A: user confirm] → draft
  → run tests → review_report → [Gate B: verify completeness, then severity]
    → NEEDS_VERIFICATION: finish checks on current hashes, then re-enter Gate B
    → P0: rewrite plan → user confirm → full rewrite → retest
    → P1: patch_plan → patch (≤3) → regression → [Gate C]
    → P2: delegate auditor → minimal polish → regression → [Gate C]
    → P3 / PASS → ACCEPTED
  → [Gate D] → state_update → write lockfile
  → [Gate E: chapter end?] → chapter integration tests → next chapter
```

Blocked scenes (P0 unresolved after 1 rewrite, or patch loop > 2 rounds) return to planning for a new `scene_card`.

---

## Gate table

| Gate | Location | Pass condition | On failure |
|------|----------|---------------|------------|
| **A** Card Gate | After scene_card | User confirms (auto: self-check passes) | Revise card |
| **B** Review Gate | After review_report | Required checks complete on final hashes, then branch by highest severity: P0→rewrite, P1→patch, P2-only→lint, P3/PASS→ACCEPTED | Enter branch |
| **C** Regression Gate | After regression_check | `result.status: ACCEPTED` | NEEDS_VERIFICATION → finish checks without a repair round; NEEDS_MORE_PATCH (≤2 rounds)→patch; exceeded/BLOCKED→planning |
| **D** State Gate | Before lockfile write | Scene accepted; state_update contains only draft-confirmed facts | Reject write |
| **E** Chapter Gate | Chapter end | integration tests complete on final hashes, no FAIL | Locate problem scene→review/patch or planning |

---

## Interaction points & auto mode

| Interaction point | Default (interactive) | Auto mode |
|-------------------|----------------------|-----------|
| Gate A card confirm | Stop, wait | Auto-pass if self-check passes |
| P0 rewrite plan | Stop, wait | **Still stop** (P0 always needs human) |
| P1 patch_plan | Stop, wait | Auto-execute; patch_note archived |
| Gate E chapter report | Stop, present | Stop, present |

Auto mode is detected from user utterance (e.g. "连续写两场" or "write the next two scenes without stopping"). Declare active mode at the start of each phase.

---

## Module loading route

Load reference files lazily by phase. Load only relevant reference sections and their required contracts:

| Phase | Files loaded |
|-------|-------------|
| Initialize | `conventions.md` + `state-layout.md` + `workflow-setup.md` |
| Plan | `conventions.md` + `workflow-planning.md` |
| Draft | `workflow-draft.md` (+ sibling expander rules) |
| Review | `workflow-review.md` + one `checks-*.md` at a time (sequential) |
| Patch | `workflow-patch.md` (+ sibling auditor for P2) |
| Regression | `workflow-regression.md` |
| State update | `workflow-state-update.md` + `state-layout.md` |
| Chapter wrap | `workflow-chapter.md` |

---

## Reference files

| File | When to load |
|------|-------------|
| `references/conventions.md` | **Always loaded first.** Severity system, test output protocol, patch rules, gates, interaction points. |
| `references/state-layout.md` | Initialization, state update. Project directory contract + state schemas. |
| `references/workflow-setup.md` | Project initialization (full / lite / cold-start). |
| `references/workflow-state-update.md` | After scene ACCEPTED. Lockfile update + watchlist maintenance. |
| `references/workflow-planning.md` | Chapter/scene planning. Produces `chapter_arc` + `scene_card`. |
| `references/workflow-chapter.md` | Chapter end. Integration tests + three questions + non-gating pattern observation. |
| `references/workflow-draft.md` | Draft generation. Structural rules + narrative-craft/language delegation. |
| `references/workflow-review.md` | Review orchestration. Produces `review_report`. |
| `references/checks-canon.md` | Review: canon + continuity + information checks (cluster 1). |
| `references/checks-character.md` | Review: general + character-specific checks (cluster 2). |
| `references/checks-structure.md` | Review: scene_function + causality + conflict + emotion_curve + consequence + narrative_delivery (cluster 3). |
| `references/checks-genre.md` | Review: genre contract + type extension packs (cluster 4). |
| `references/workflow-patch.md` | Patch phase. Patch plan + execution + anti-scope-creep rules. |
| `references/workflow-regression.md` | Regression phase. Seven checks + verification/repair exits. |

---

## Maintainer notes

**Language allocation is intentional.** Meta-layer content (workflow structure, routing, loading rules, this maintainer section) is in English to activate instruction-following clusters. Content-layer material (test items, writing rules, case examples, all Chinese creative-writing content) is in Chinese because the rules describe surface forms that must match what the model generates during Chinese creative writing. Don't translate content-layer material to English.

**Schema single-ownership.** Every schema has exactly one owner file (see `blueprint.md` §5.2). Consumer files reference the owner by filename + section number — they never replicate the schema. The owner table: project_brief/world_bible/character_profile/canon_lockfile → `state-layout.md`; scene_card/chapter_arc → `workflow-planning.md`; review_report → `workflow-review.md`; patch_note/patch_plan → `workflow-patch.md`; regression_report → `workflow-regression.md`; state_update → `workflow-state-update.md`.

**Sibling dependencies.** Narrative-craft and language generation are delegated to `novel-expander`; P2 prose_lint is delegated to `novel-auditor`. Fallback rules when siblings are unavailable are in `conventions.md` §7 and the review contract respectively. Never replicate expander or auditor rule entries in this skill; only map scene_card fields to their owners.

**Separate problem severity from verification completeness.** P3 taste is optional; confirmed language defects are P2. Frequency excess needs review and a resolution, not automatic deletion. Unperformed mandatory checks prevent a completion claim independently of severity.

## Shared editorial services

`references/project-context.md` resolves project evidence for all siblings without requiring a
scene card outside CI. `reader-index.md` owns the accepted disclosure index and mapping;
`revision-tools.md` owns frozen baselines, guarded batches and bound receipts. Ordinary audits
can use these services directly. Read references progressively as needed, not all into one prompt.

NEEDS_VERIFICATION means a mandatory check is unfinished or stale; gather evidence before
continuing to acceptance, without consuming a patch round. A density threshold is not an
automatic textual error, but every excess must have a checked outcome. State writes require the
accepted final hashes. Do not turn RISK/SKIPPED into PASS or silently accept an unchecked draft.

Existing explicit authorization satisfies the corresponding interaction point within its scope; do not ask again merely because a skill names a confirmation step. New creative decisions outside that scope still require author input.
