# Novel CI — Workflow: Patch

> Loaded during: patch phase (after review_report, Gate B → P1/P2 branch).
> Depends on: `conventions.md` §2, §4, §5 Gate B/C, §6.
> Owner of: `patch_note` format, `patch_plan` schema (contracts §4).

---

## 1. Input

- `review_report.failures`, grouped by severity (P0 / P1 / P2 / P3).
- Current `draft` (the file to be patched).
- Current `scene_card`, `lockfile`, and relevant `character_profile` files (read-only — patches must not silently alter canon).

---

## 2. patch_plan schema

```yaml
patch_plan:
  scene_id: ""
  round: 1                        # which patch round for this scene
  patches:
    - patch_id: ""                # <scene_id>-p<N>
      severity: ""
      failure_type: ""
      target: {anchor: "", para: 0}
      fix_strategy: ""
      estimated_scope: ""         # punctuation | word | sentence | short-paragraph | segment-restructure
      risks: []
  full_rewrite_required: false
  reason_if_full_rewrite: ""
```

**Plan first, then execute.** The patch_plan must be produced for the interaction point:
- Interactive mode: stop and wait for user confirmation on patch_plan.
- Auto mode: P1 patches auto-execute (patch_note archived); **P0 always waits for human** even in auto mode (`conventions.md` §6).

---

## 3. patch_note format

Each executed patch writes a note appended to `*.patches.md`:

```markdown
## Patch <scene_id>-p<N>
- Level: P1
- Type: scene_function_failure
- Original location: > verbatim quote 1–3 sentences
- Problem: <the failure from review_report>
- Fix intent: what to fix, what NOT to touch
- Replacement: > new fragment
- Self-check: changed confirmed facts? No / changed character motivation? No / changed information access? No / fixed original problem? Yes / needs lockfile update? Yes|No
```

**Discipline:** Append-only to `*.patches.md`. Never overwrite. Full history matters for regression scope checking.

---

## 4. Branch execution by severity

### P0 line — Full rewrite with justification

1. **First: argue why local patch is insufficient.** Reference specific failures. If a local patch COULD fix it, don't jump to rewrite.
2. **User confirmation is mandatory** (even in auto mode).
3. Execute full scene rewrite against the SAME `scene_card`.
4. Run **full retest** — return to `workflow-review` from scratch (all modules).
5. **Limit:** 1 full rewrite per scene. If P0 occurs again after rewrite → scene `blocked`, return to `workflow-planning`.

### P1 line — Local patch, limited scope

1. Max 3 patches per round.
2. Only touch failure-named locations from `review_report`.
3. Choose the smallest evidence-supported intervention: add missing material, clarify an unclear relationship, or compress/delete work already completed. Do not prefer addition or deletion categorically; preserve required facts, reactions, voice and deliberate repetition.
4. Each patch is a fragment replacement, not a full redraft.
5. After patches applied → proceed to `workflow-regression`.

### P2 line — Minimal polish, delegated to auditor

1. Request auditor suggestions for each P2 failure as an assigned read-only worker with the
   established method, current evidence and exact scope. Do not reopen audit-plan selection or
   recursively delegate. The patch executor remains the single writer; any already selected
   revision challenge follows the auditor's [execution protocol](../../novel-auditor/references/audit-execution.md).
2. Execute at **minimum modification level**: punctuation < word < sentence < short-paragraph.
3. **Hard boundary:** P2 polish MUST NOT alter plot facts, character motivation, information access, event outcomes, or world rules.
4. After patches applied → proceed to `workflow-regression`.

### P3 line — Default: don't touch

1. P3 issues are NOT addressed unless user explicitly requests.
2. If user requests, minimal optional adjustment.
3. Any executed P3 edit triggers proportional verification under workflow-regression.md. Optional edits do not consume P1 repair rounds, but cannot bypass final-version checks.

### Example: P1 patch execution

```
Input failure:
  severity: P1
  type: conflict_deficit
  location: {anchor: "谢谢你告诉我这些", para: 27}
  issue: "整场以角色 A 和角色 B 友好交换信息为主，双方目标一致、态度友善、无阻力。"
  required_fix: "让角色 B 至少在一个信息点上回避或要求代价。"

Patch plan:
  patch_id: ch003-s02-p1
  severity: P1
  failure_type: conflict_deficit
  target: {anchor: "谢谢你告诉我这些", para: 27}
  fix_strategy: "在角色 B 回答前插入一个短段：角色 B 犹豫、反问角色 A 为什么要知道这个——制造信息不对称张力，然后有条件地透露部分信息。"
  estimated_scope: short-paragraph
  risks: ["角色 B 的反问可能显得过于敌对——控制分寸，保留角色 B 的基本友善底色"]

Patch note (after execution):
  ## Patch ch003-s02-p1
  - Level: P1
  - Type: conflict_deficit
  - Original location: > "谢谢你告诉我这些。"角色 B 点点头，把事情的来龙去脉说了一遍。
  - Problem: 角色 B 无阻力地全盘托出信息，card 指定的"角色 B 不愿透露"未实现。
  - Fix intent: 在角色 B 回答前插入犹豫和条件，保持角色 B 友善底色但让信息交换有张力。
  - Replacement: > "谢谢你告诉我这些。"角色 B 看了角色 A 一眼，没立刻开口。手指在茶杯沿上转了一圈。"你先告诉我，你为什么要打听这件事？"语气不算冷，但也没松口。
  - Self-check: changed confirmed facts? No / changed character motivation? No / changed information access? No / fixed original problem? Yes / needs lockfile update? No
```

---

## 5. Anti-scope-creep discipline

**顺手修改未点名问题 = 违规，即使"显然更好"。**

- The review_report is the contract. Fix ONLY what it names.
- If you notice a new problem while patching: write it into the review_report's `risks` array. Do NOT fix it inline.
- The test: "Does review_report.failures contain an entry matching this exact location and issue?" If no → don't touch.

---

## 6. Loop cap enforcement (D8)

| Round | Action |
|-------|--------|
| Round 1 | Normal patch execution → regression |
| Round 2 | Last chance — patch → regression |
| Round 2 + NEEDS_MORE_PATCH | Scene → `blocked`, return to `workflow-planning` for new card |

P0 rewrite does NOT count as a patch round, but is limited to 1 per scene. A second P0 also → `blocked` + planning.

## 7. Safe batch protocol

Before any mutation follow revision-tools.md: freeze full original and latest accepted scope,
record source hashes and protected meaning, preflight the entire batch for unique exact anchors,
scope and overlap, stage candidates and inspect actual differences. Recheck versions at write
and track each atomic file replacement. No multi-file atomicity is promised. Recovery must not
overwrite concurrent external changes; verify current output hashes before rollback.

Existing explicit authorization to revise the stated scope satisfies that interaction point;
do not repeatedly request permission for the same edit. New canon, major reconstruction or a
scope expansion still needs its own concrete decision. P2 may use a batch of identified local
changes; do not apply the P1 three-patch cap to every language occurrence. Neither P2 nor P3 may
silently change certainty, action completion, facts or information access. Run actual regression,
not only the patch author's self-check.
