# Novel CI — Workflow: Review

> Loaded during: review phase (after draft, before Gate B).
> Depends on: `conventions.md` §2, §3, §5 Gate B.
> Owner of: `review_report` schema (contracts §8.7).
> Delegates prose_lint to: `novel-auditor` (contracts §10.2).

---

## 1. Execution order

The normal CI review is an established workflow, including a `skills_review` auditor task;
do not insert an audit-choice question into every scene. If the user selected additional
audit methods, the coordinator follows
[audit planning](../../novel-auditor/references/audit-planning.md) and
[audit execution](../../novel-auditor/references/audit-execution.md), preserving the independent
reader's inputs even when CI findings already exist. Reuse completed checks only when scope,
source hashes and evidence match. Optional methods do not replace the mandatory clusters below.

Load checks files **one cluster at a time** — never load all four at once. Execute in order:

1. `checks-canon.md` → canon + continuity + information results
2. `checks-character.md` → general character + character-specific results
3. `checks-structure.md` → scene_function + causality + conflict + emotion_curve + consequence + narrative_delivery results
4. `checks-genre.md` → genre results
5. Prose lint: delegate to `novel-auditor`

Each module outputs its own result block independently (`conventions.md` §3).

---

## 2. review_report schema

```yaml
review_report:
  scene_id: ""
  verification: {}                # project-context.md verification_record contract
  goal_completed: true           # against scene_card.target.success_condition
  test_results:                  # keys frozen; values = PASS|FAIL|RISK|SKIPPED
    canon: PASS
    continuity: PASS
    information: PASS
    character: PASS
    scene_function: PASS
    causality: PASS
    conflict: PASS
    emotion_curve: PASS
    consequence: PASS
    narrative_delivery: PASS
    genre: PASS
    prose_lint: PASS             # shared methods; SKIPPED only if check could not be performed
  failures: []                   # aggregated from all modules; entry format per conventions.md §3
  risks: []
  rewrite_permission:
    full_rewrite: false          # true ONLY when P0 exists AND local patch cannot fix
    max_patches: 3
  acceptability:
    status: ACCEPTED | NEEDS_PATCH | BLOCKED | NEEDS_VERIFICATION
    reason: ""
```

---

## 3. Acceptability determination

| Condition | status | rewrite_permission.full_rewrite | rewrite_permission.max_patches |
|-----------|--------|-------------------------------|-------------------------------|
| Mandatory evidence/classification missing or stale | NEEDS_VERIFICATION | false | 0 |
| Any P0, cannot be fixed locally | BLOCKED | true (with reason) | — |
| Any P0, can be fixed locally | BLOCKED | false | — |
| Any P1 (no P0) | NEEDS_PATCH | false | 3 |
| P2 only (no P0/P1) | NEEDS_PATCH | false | (per P2 scope) |
| Required checks complete; P3 only or all PASS | ACCEPTED | false | 0 |

`rewrite_permission.full_rewrite: true` requires a written reason explaining why local patches cannot fix the P0 failure(s).

---

## 4. Prose lint delegation

Delegate to `novel-auditor` per `contracts.md` §10.2:

- **Input:** `draft`, shared project context, applicable decisions, language profile and relevant reader disclosures; final source hashes accompany results.
- **Assignment:** an existing-choice, read-only `skills_review` worker task. Execute that scope
  without asking for a new plan or spawning more auditors. The coordinator owns any selected
  extra methods; independent readers receive separate minimal packets, never this full input.
- **Optional reference input:** pinned language reference and its scope from shared project context.
  Auditor owns the comparison contract. Pure statistical deviations are evidence, suspected language
  issues enter risks, and only contextual language defects enter P2. No new check key or structural
  gate is added. An explicitly required comparison reports completion or gaps; insufficient data
  cannot be described as style acceptance. Existing mandatory checks remain in force.
- **Output mapping:**
  - Confirmed language finding → P2/prose_lint. Reader redundancy → reader_redundancy. Factual, causal, knowledge and voice failures return to their owning checks and severity; do not downcast them to P2.
  - Auditor "疑似" (suspected) finding → `review_report.risks` entry. **Do NOT auto-fix.** Respect auditor's Principle 1 (author's intent first).
- **Fallback** (auditor unavailable): the current executor reads the shared rules and performs the checks. If they cannot be completed, record SKIPPED and NEEDS_VERIFICATION; do not claim acceptance.

This file contains NO language rule entries. The canonical source for language rules is `novel-expander/references/anti-ai-patterns.md`.

---

## 5. Watchlist enforcement

Before running any check module:

1. Read `lockfile.watchlist` for items with `status: open`.
2. For each open watchlist item, verify against the current draft.
3. Result goes into the relevant module output:
   - Resolved → no action (state_update will `clear` it).
   - Still present → `RISK` entry noting the watch item persists.
   - Worsened → `FAIL` entry if the watch item's concern materialized.

---

## 6. Anti-vagueness discipline

**Every FAIL must have an `anchor` (verbatim quote ≤30 characters) AND `evidence` (citing specific lockfile/bible/card fields, prior-scene facts, actual source passages or distribution evidence).**

A finding needs inspectable evidence: an applicable decision, passage, distribution or confirmed state. Without it, record RISK rather than fabricate a diagnosis. Incomplete required evidence still prevents an acceptance claim.

Write failures into `*.review.yaml` (overwrite — keep only latest review).

---

## 7. External feedback translation

读者反馈是症状，不是现成 patch。把外部反馈按以下顺序处理：

```text
读者原话
→ 可观察症状（在哪里失去理解、兴趣、信任或情绪连接）
→ 2—3 个底层原因假设
→ 分派到现有 checks 模块验证
→ 有 anchor + evidence 才成为 failure；证据不足进入 RISK
```

不要直接执行读者给出的解决方案：

- “改第一人称”先检查 POV 形式、心理距离与注意力过滤。
- “多写这个人物”先检查动机是否可见、关键行动是否被概述吞掉。
- “这里节奏慢”先检查场景是否缺少变化，或惯例是否应压缩/省略。
- “多加冲突”先检查既定目标是否已被拒绝、发现或关系微移阻碍。

翻译结果写入相应模块的 failure/risk，沿既有 Gate B 进入 patch；不得创建“reader says”类型
并绕过证据义务，也不得在 review 阶段直接重写正文。

---

## 8. Review execution protocol

For each checks file loaded:

1. **Load the checks file** — read its test items and severity guide.
2. **Load required context** — per blueprint §5.1 table, load only what that cluster needs (lockfile for canon; character profiles for character; scene_card+draft for structure; project_brief for genre).
3. **Run every test item** — each item produces PASS, FAIL (with anchor+evidence), or RISK (with watch).
4. **Output the result block** — write the `<module>_tests_result` block.
5. **Aggregate into review_report** — add failures to `review_report.failures`, risks to `review_report.risks`.
6. **Unload the checks file** before loading the next one.

Do not pre-read failures from one module when running another. Each module is a fresh read of the draft against a specific lens. Cross-contamination (e.g. a canon failure making you look harder for character failures) creates bias.

---

## 9. SKIPPED handling

A test module may produce SKIPPED status when:

| Module | SKIPPED condition |
|--------|------------------|
| prose_lint | Check could not be completed, including direct execution of shared methods |
| genre | `project_brief.genre.primary` is empty or undefined |
| character (specific) | No `character_profile` files exist for appearing characters |

SKIPPED on a required check prevents acceptance: NEEDS_VERIFICATION. Optional out-of-scope modules may remain SKIPPED with a reason. A report can validly record incomplete verification without certifying the draft.

## 10. Completion gate before severity branching

Load project-context.md before review. Read actual chapter/window prose and original anchors;
reader-index.md supplies only prior disclosures and coverage. Use frequency and punctuation
results from the same final source hashes, not an earlier draft. The generic profile is required
when no project profile exists; newly observed habits still require LLM assessment.

First check required verification: absent evidence, stale hashes, unfinished classifications or
requested reader/mapping coverage gaps produce NEEDS_VERIFICATION. This is not a repair round;
complete the missing check, then branch by confirmed severity. A known failure stays recorded
while other checks are incomplete. Non-mandatory risks still follow watchlist policy.

Use actual passages, context and distribution evidence as failure evidence; not every language
problem needs a pre-existing canon entry. Successful frequency review means every excess is
resolved or specifically retained, not simply that each occurrence is grammatical.
