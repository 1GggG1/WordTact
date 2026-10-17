# Novel CI — Workflow: Planning

> Loaded during: planning phase.
> Depends on: `conventions.md`, `state-layout.md` §3.4.
> Related: `test-catalog.md` §C4 (turn templates), §E (chapter integration).
> Owner of: `scene_card` schema (contracts §8.5), `chapter_arc` schema (contracts §8.6).

---

## 1. Input

- Current `canon_lockfile` (read `current_time`, `current_location`, `character_states`, `open_threads`, `unresolved_consequences`, `watchlist`).
- `project_brief` (especially `structural_preference`, `genre`, `tone`).
- Relevant `character_profile` files for characters expected to appear.

---

## 2. Chapter planning → `chapter_arc`

### Derive chapter goal

From lockfile current state + `open_threads` + `unresolved_consequences`, determine:

- What must advance this chapter?
- Which threads can be pulled?
- Which consequences demand follow-up?

### chapter_arc schema

```yaml
chapter_arc:
  chapter_id: ""               # ch<NNN>
  opening_state: ""
  scene_sequence:
    - {scene_id: "", function: "", change_created: "", status: planned|card_confirmed|drafted|under_review|patching|accepted|blocked}
  midpoint_turn: ""
  escalation: ""
  ending_state: ""
  unresolved_consequences: []
  integration_result:          # filled by workflow-chapter at chapter end
    status: PASS | FAIL | NEEDS_VERIFICATION | 未运行
    verification: {}           # project-context.md verification_record
    failures: []
    emergent_patterns:         # non-gating observation; filled at chapter end
      repeated_choices_and_costs: []
      recurring_or_changing_objects: []
      relationship_patterns: []
      implied_theme_questions: []
      counterevidence_to_thematic_pressure: []
```

### Constraints

- Every scene in `scene_sequence` must have a **non-duplicate** `function` — no two scenes serve the same purpose.
- `opening_state` + `escalation` + `ending_state` must form a coherent arc with a discernible turn at `midpoint_turn`.
- Write `arc.yaml` to the chapter manuscript directory.

---

## 3. Scene planning → `scene_card`

### scene_card schema

```yaml
scene_card:
  scene_id: ""                 # ch<NNN>-s<SS>
  title: ""
  function:
    primary_purpose: ""
    secondary_purpose: []
    why_this_scene_must_exist: ""     # KEY FIELD
  target: {one_sentence_goal: "", success_condition: ""}   # KEY FIELD
  pov:
    character_id: ""
    narrative_distance: ""
    information_limit: ""
    narrator: ""                 # fill only when non-default
    narratee: ""                 # fill only when non-default
    form: ""                     # letter/report/diary/transcript/etc.; non-default only
    attention_filter: ""         # what this POV notices, ignores, or misreads
  entry_state:
    time: ""
    location: ""
    previous_scene_result: ""
    active_constraints: []
    character_states:
      - {character_id: "", state: "", belief: "", goal: ""}
  conflict: {external: "", internal: "", interpersonal: "", systemic_or_environmental: ""}
  stakes:
    if_goal_fails: ""
    cost_of_success: ""          # focus for major wins; may be empty
  change_chain:
    initiating_action: ""
    resistance_or_revelation: ""
    response_kind: decision | refusal | strategy_shift | deliberate_inaction
    response: ""
  dynamics:
    power_shift: ""
    connection_shift: ""
  time_handling:
    foreground: ""
    compress: []
    omit: []
  dialogue_dynamics:              # dialogue-led scenes only
    - character_id: ""
      language_goal: ""
      opening_strategy: ""
      refusal_received: ""
      strategy_shift: ""
  misunderstanding_or_information_gap: []
  required_beats:
    - {beat: "", function: ""}
  turn:
    midpoint_shift: ""
    emotional_shift: ""
    embodied_by: ""              # visible action, object, or consequence
  memory_hook: []
  consequence: {immediate: [], delayed: []}                # KEY FIELD
  exit_state:                                              # KEY FIELD
    changed_facts: []
    changed_beliefs: []
    changed_relationships: []
    new_constraints: []
    open_threads: []
  forbidden: []                                            # KEY FIELD
  prose_constraints: {must_include: [], must_avoid: []}
```

---

字段纪律：`entry_state.character_states[].goal` 是即时欲望的唯一来源，不复制 desire。
`power_shift` / `connection_shift` 至少说明一项，或明确“不适用”并由 `exit_state` 记录事实、
信念、资源或约束变化。`dialogue_dynamics`、`narratee`、`form` 是条件字段。
`deliberate_inaction` 是合法回应，不能把安静或拒绝自动判为空转。

## 4. Field guidelines

### 4.1 `why_this_scene_must_exist`

场景存在的不可替代理由。如果可以用一句"交代了背景"概括，说明理由不够——背景可以通过其他更有功能的场景传达。

- **好**: "角色 A 发现角色 B 隐瞒了事件 X，这是两人决裂的唯一触发点"——该场景是因果链上不可跳过的环节。
- **坏**: "展示世界观中的某个设定"——展示设定不是场景功能，设定可以附在任何有功能的场景中。

### 4.2 `target.success_condition`

必须可判定。完成后读者能回答"是/否"。

- **好**: "角色 A 从角色 B 处获得信息 X，且角色 B 不知道自己已被套话"
- **坏**: "让读者感受到世界观的神秘"——感受不可判定。

### 4.3 `turn.midpoint_shift`

场景中段的转向。从一种状态进入另一种状态。参考 `test-catalog.md` §C4 转向模板：

> 平静→不对劲 | 安全→安全是假象 | 好笑→不舒服 | 流程→失控
> 误会→后果 | 试探→暴露 | 旁观→卷入 | 胜利→代价
> 救援→新麻烦 | 亲密→误伤 | 解释→更大的误解 | 控制→失控

`emotional_shift` 也必须非空，且与 `midpoint_shift` 呼应。

- **好**: midpoint_shift "角色 A 以为在帮角色 B，却发现角色 B 在利用自己" + emotional_shift "感激→被背叛的寒意"
- **坏**: midpoint_shift "角色 A 想了想" + emotional_shift "有点困惑"——没有真正的转向。

### 4.4 `consequence`

`immediate` 是本场景直接结果；`delayed` 是会在后续场景生效的结果。两者必须非空。

- **好**: immediate "角色 A 当众驳了角色 B 的面子" + delayed "角色 B 将在下一场中暗中阻挠角色 A 的计划"
- **坏**: immediate "角色 A 离开了房间"——这不是后果，只是位移；无 delayed。

### 4.5 `exit_state`

必须与 `consequence` 互相呼应：exit_state 的 changed_facts 应该等于 consequence.immediate 的具体化。

- **好**: changed_facts "角色 A 与角色 B 的公开矛盾已形成" + changed_beliefs "角色 A 认为角色 B 不可信任" + changed_relationships "角色 A→角色 B:敌意"
- **坏**: changed_facts 为空或写"暂无"。

### 4.6 `forbidden`

防御性字段。列出本场景绝对不能出现的内容——来自 lockfile 敏感项、角色信息权限边界、以及容易踩的坑。

- **好**: "角色 A 不得知道事件 X（lockfile 记录其 does_not_know）；不得出现角色 C（尚未登场）；不得让角色 B 主动道歉（违背其 voice.must_not）"
- **坏**: "注意不要写差"——太泛，不可检查。

### 4.7 `stakes` 与 `change_chain`

`if_goal_fails` 写失败将失去什么；重大胜利再填写 `cost_of_success`，不要给每次小成功硬造代价。
`change_chain` 必须能沿“人物先做什么 → 遇到什么阻力或新信息 → 怎样回应”追踪。

- **好**: initiating_action "角色甲要求改期" → resistance_or_revelation "角色乙已替所有人付款" → response_kind `refusal` → response "角色甲拒绝接受退款并退出安排"。
- **坏**: initiating_action "大家聊天" → resistance_or_revelation "气氛微妙" → response "各自想了很多"——动作、刺激和回应都不可判定。

### 4.8 `dynamics`

比较场景首尾谁能决定、谁要回应，以及人物是靠近、疏远还是中断联系。若变化发生在事实、
信念、资源或约束上，可明确写“不适用”，由 `exit_state` 承担，不要伪造权力变化。

### 4.9 `time_handling`

- `foreground`: 必须让读者亲历的发现、决定、拒绝、策略变化或关系移动。
- `compress`: 惯例、重复劳动、旅行过程、次要交流和已建立模式。
- `omit`: 只连接两个清楚状态且没有新功能的过程。

关键发现或决定不得被一句概述吞掉；惯例也不要为了“完整”扩成空转场景。

### 4.10 `dialogue_dynamics`（条件字段）

仅当语言争夺是场景主要机制时填写。每个参与者写清语言目标、开局策略、收到的拒绝以及
策略变化。答非所问、附加条件、沉默和错误答案都可以构成拒绝。非对话主导场景留空，
不能为填 schema 强行制造争论。

### 4.11 `pov` 与 `turn.embodied_by`

`narrator`、`narratee`、`form` 只在非默认文体填写；它们必须与 `narrative_distance`、
`information_limit` 一致。`attention_filter` 说明 POV 因专业、偏见、社会位置、身体条件或
欲望会注意、忽略、误判什么。

`turn.embodied_by` 把转向落实为读者可见的动作、物件或后果，不能重复抽象情绪标签。

---

## 5. Card self-check checklist (Gate A auto-mode pass criteria)

Every item must be answerable with YES:

1. `target.one_sentence_goal` can be judged as achieved/failed after reading the scene?
2. `target.success_condition` is falsifiable (can tell whether it was met)?
3. At least one conflict dimension (`external` / `internal` / `interpersonal` / `systemic_or_environmental`) is non-empty?
4. Either `misunderstanding_or_information_gap` is non-empty, or conflict creates genuine information asymmetry?
5. `turn.midpoint_shift` AND `turn.emotional_shift` are both non-empty?
6. `consequence.immediate` is non-empty AND `consequence.delayed` is non-empty?
7. `exit_state` has at least one non-empty field among `changed_facts` / `changed_beliefs` / `changed_relationships`?
8. `forbidden` contains specific, checkable entries (not vague "写好点")?
9. `entry_state` data is copied from lockfile (not from memory recall)?
10. `pov.information_limit` is consistent with that character's `information_access`?
11. The key change can be traced through `initiating_action → resistance_or_revelation → response`?
12. `turn.embodied_by` makes the turn visible through an action, object, or consequence?
13. `time_handling` keeps discovery/decision in foreground and compresses or omits routine connective material?
14. If dialogue-led, each relevant character has a language goal, receives refusal, and changes or deliberately retains strategy?
15. POV narrator/narratee/form/distance/information/attention fields are mutually consistent?

Items 13–15 are conditional where their source fields are conditional. Mark `not_applicable` with a concrete
reason; do not invent dialogue conflict, special form, or dramatic escalation merely to pass Gate A.

---

## 6. Information discipline during planning

- **Entry state MUST be copied from lockfile**, not recalled from memory. Lockfile is the source of truth; human/LLM memory drifts.
- **pov.information_limit** MUST match the POV character's `information_access` in their profile. If the character `does_not_know` something, `information_limit` must exclude it.
- If lockfile data contradicts the planner's intuition, lockfile wins. Flag the discrepancy for the user but do not silently override.

---

## 7. Blocked scene reflow (D8)

When a scene reaches `blocked` (P0 unresolved after 1 rewrite, or patch loop > 2 rounds), return here:

1. **Diagnose** the scene_card defect. Root causes are typically:
   - `success_condition` is not actually decidable.
   - `conflict` is hollow — the card names a conflict but no real opposition exists.
   - `exit_state` has no teeth — scene "ends" but nothing changed.
   - `change_chain` has activity but no resistance/revelation or response.
   - `time_handling` foregrounds routine while summarizing the irreversible moment.
2. **Produce a new card**, not a tweak of the old one. The old card's structural assumptions failed.
3. **Re-plan affected scenes** in the chapter arc if the new card changes the scene_sequence.

## Shared project and reader context

Before planning or drafting, read project-context.md and retrieve relevant disclosures through
reader-index.md using only the prefix before the target. Verify source anchors when relying on
an indexed summary. Load project language habits before generation; the later review performs
mandatory scans and semantic judgments. Existing author decisions and local exceptions retain
their scope; no second canon or new mandatory project-state migration is required.
