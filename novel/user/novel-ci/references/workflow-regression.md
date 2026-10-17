# Novel CI — Workflow: Regression

> Loaded during: regression phase (after patch applied, before Gate C).
> Depends on: `conventions.md` §4 (loop cap), §5 Gate C.
> Owner of: `regression_report` schema (contracts §8.8).

---

## 1. Input

- Frozen complete original, latest accepted version, candidate, actual diff, protected items and relevant context (revision-tools.md).
- Patch IDs from the current patch round.
- Patched `draft` (after applying all patches from this round).
- Original `review_report` (the failures these patches were meant to fix).
- `*.patches.md` (for scope verification).
- Relevant `character_profile` files (for voice check).

---

## 2. regression_report schema

```yaml
regression_report:
  scene_id: ""
  verification: {}                # project-context.md verification_record contract
  round: 1
  patch_ids: []
  checks:
    original_failure_fixed: {status: PASS, note: ""}
    no_new_failure: {status: PASS, note: ""}
    canon_intact: {status: PASS, note: ""}
    character_motivation_intact: {status: PASS, note: ""}
    information_control_intact: {status: PASS, note: ""}
    voice_intact: {status: PASS, note: ""}
    scope_not_exceeded: {status: PASS, note: ""}
  lockfile_update_needed: true
  result: {status: ACCEPTED | NEEDS_MORE_PATCH | BLOCKED | NEEDS_VERIFICATION, reason: ""}
```

---

## 3. Seven checks — execution guide

### 3.1 original_failure_fixed
**Check:** For each failure the patches targeted, is the problem resolved in the patched draft?

**Method:** Compare patch targets against the review_report failures. For each named failure, locate the patched area in the draft and verify the issue is gone.

### 3.2 no_new_failure
**Check:** Did the patches introduce any NEW problems?

**Method:** Scan the changed areas and their immediate context for new issues: new continuity breaks, new information leaks, new character inconsistencies. The scope is wider than just the patched lines — check how the new text connects to surrounding paragraphs.

### 3.3 canon_intact
**Check:** Did the patches alter any confirmed lockfile facts?

**Method:** Compare lockfile `confirmed_events`, `character_states`, and `world_state` against the patched draft. An unsupported change to a confirmed fact = FAIL. Correcting an original error requires current author/canon evidence and a recorded supersession.

### 3.4 character_motivation_intact
**Check:** Did the patches change what any character wants or why they act?

**Method:** Compare `character_profile` fields (`external_goal`, `internal_need`, `default_strategy`, `moral_boundary`) against character behavior in patched areas. Patch should fix the failure type without altering motivation. Example: fixing `conflict_deficit` should not accidentally make a character more aggressive than their profile allows.

### 3.5 information_control_intact
**Check:** Did the patches grant or remove information access for any character?

**Method:** Compare `character_profile.information_access` against each character's knowledge in patched areas. A patch adding dialogue may inadvertently leak information.

Also apply the shared [evidence boundaries](project-context.md#evidence-boundaries-in-writing-and-review)
to the before/after prose: preserve how necessary information becomes available, as well as who
knows it. Project facts alone cannot prove that a deleted discovery or transition is redundant.
Keep legitimate narrator access, time shifts and purposeful omissions; repairing one gap must
not reveal a protected secret or turn supported implication into mandatory exposition.

### 3.6 voice_intact
**Check:** Did the patches change any character's voice?

**Method:** Compare `character_profile.voice` against each character's dialogue/narration in patched areas. Key fields: `diction`, `rhythm`, `forbidden_lines`. A patch that changes a character's speaking pattern to be more "correct" is still a regression — voice stability matters more than correctness.

Use applicable author rules and approved samples from the pinned
[style basis](../../novel-auditor/references/style-consistency.md), alongside original and accepted
prose. Compare narrator, speaker, form and scene conditions; preserve the differences between
characters and between public/private, tense/quiet or other purposeful registers. A character's
change of tone is not itself drift. Check stable terms and referents without forcing synonyms.
If a patch claims lower reading load, verify the actual comprehension benefit and retained
rhythm using [Chinese reading load](../../novel-auditor/references/reading-load-zh.md). A shorter
sentence or a closer frequency profile cannot prove this check passed. Record these findings
within the existing seven checks; no additional style gate or baseline refresh is introduced.

### 3.7 scope_not_exceeded
**Check:** Did the patches only touch the failure-named locations from review_report?

**Method:** Compare `*.patches.md` targets against actual changes in the draft. If the draft has changes beyond the patch targets, verify those are strictly necessary for the fix (e.g. a paragraph restructure may naturally shift surrounding text). Unnecessary adjacent changes = FAIL.

---

## 4. Verification and repair exits

| Condition | result.status | Next step |
|-----------|--------------|-----------|
| Required evidence absent/stale or required check RISK/SKIPPED | NEEDS_VERIFICATION | Finish verification; do not increment round |
| All 7 checks PASS and required verification complete on final hashes | ACCEPTED | → `workflow-state-update` |
| Some checks FAIL, round < 2 | NEEDS_MORE_PATCH | → back to `workflow-patch` (increment round) |
| Some checks FAIL, round ≥ 2 | BLOCKED | → scene blocked, back to `workflow-planning` (D8) |
| Any P0-level regression detected | BLOCKED | → scene blocked, back to `workflow-planning` |

Round counting: write `round` into the report. First regression after first patch execution = round 1. After second patch execution = round 2.

---

## 5. Boundary with full retest

Regression checks ONLY the patch impact surface — the 7 checks above. It does NOT re-run all 11 test modules.

**Exception:** P0 full rewrite → the scene goes through full `workflow-review` (all modules from scratch), NOT through this regression workflow. Regression covers actual P1/P2/P3 edits proportionally; an unimplemented suggestion needs no regression.

---

Restoring a rejected candidate does not erase the original unresolved problem. BLOCKED describes the remaining work, not proof that all baseline prose must be rewritten.

## 6. Regression report output

Write `regression_report` to `*.review.yaml` as a sibling block to the original `review_report`. The file then contains both the original review and the regression result, giving a complete audit trail for the scene.

---

## 7. Common regression failures and responses

| Failed check | Common cause | Response |
|-------------|-------------|----------|
| original_failure_fixed: FAIL | Patch was too conservative or missed the root cause | Return to patch with sharper fix strategy |
| no_new_failure: FAIL | Patch introduced a new problem in adjacent text | Shrink or reject the candidate; any supplementary P1 patch counts toward its three-patch limit |
| canon_intact: FAIL | Patch accidentally altered a confirmed fact | This is serious — revert the patch and redesign the fix |
| scope_not_exceeded: FAIL | Patch cleaned up "obvious issues" beyond the named failure | Revert the extra changes; remind: only fix what review named |
| voice_intact: FAIL | Patch made dialogue more "correct" but less character-specific | Revert and rewrite the fix preserving the original voice pattern |

When a check fails, the fix is specific to that check — do not redo the entire patch round.

## 8. Fixed baseline, local semantics and proportional checks

Before the first edit, use revision-tools.md to freeze the complete original scope and a distinct
latest accepted version. Inputs also include original/current SHA-256, real before/after diff,
protected items, relevant decisions, adjacent prose and the declared edit goal. The original is
not overwritten at each round. If an old audit lacks a baseline, mark that limitation; do not
reconstruct a fictitious verified original from current HEAD.

Run the seven checks against both the recent accepted version and the fixed original. Check
local meaning even when it is absent from canon: agents/objects, negation, possibility/certainty,
conditions, quantities and range, planned/started/ongoing/completed action, time/causality, POV,
reader knowledge, implication, voice and rhythm. “不能排除夜间补给” is not automatically “会有夜间补给”;
“已经核对” is not “交给核对”. Context may support a clarification, but quote that evidence.

Regression examples use anonymous equivalents of audit cases:

| Case | Candidate change | Required judgment |
|---|---|---|
| B07 | “不能排除夜间补给” → “夜间一定会有补给” | Reject unless new explicit evidence supports certainty; smoother wording cannot strengthen the claim. |
| E02 | “已经让她核对过” → “交给她核对” | Reject an unsupported completed-to-pending change. |
| B05 | A cautious statement about training is made more explicit | Read the adjacent statement about who actually trained and what they can do; accept only that supported scope. |
| B06 | A cautious statement about remembering a route is made more explicit | Quote contextual evidence of actual recollection; do not invent perfect memory or certainty beyond it. |

For compression, inventory the meaning of the deleted span too: repeated exposition may carry a
new knower, time, condition or completed action. Preserve that increment or justify its removal;
reading a smooth remainder is not a regression check.

All actual manuscript edits, including P3 and punctuation, need proportional verification. A
pure glyph change has a smaller semantic surface; splitting/merging sentences does not. P1 alone
has the three-patch cap; P2 may be a preflighted batch of named local issues. Keep two repair rounds.
Generate one minimal candidate by default. If stronger constraints produce new repetition or
meaning loss, weaken the editing intervention or reject the candidate, not the threshold.

The original is an available outcome; rejecting a candidate does not clear the original failure.
If no accepted version exists, restoring baseline restores text only. Valid original errors may
be corrected with explicit canon/author evidence; baseline preservation does not freeze errors.

## 9. Final-version acceptance

A required check without evidence or with stale hashes, RISK or SKIPPED yields NEEDS_VERIFICATION,
not ACCEPTED; complete verification without incrementing repair rounds. This condition precedes
the seven-check exit table. Confirmed failed checks still require correction or candidate rejection.

Order: punctuation normalization → final frequency recount → semantic/cumulative regression →
required publication mapping verification → project acceptance → reader-index commit. Any further
text change invalidates associated results. Apply the revision-tools receipt contract when
accepting a batch; PASS labels alone are not a literary proof. Only the project's accepted final
version enters state-update. Preserve unresolved issues and coverage gaps in the report.
