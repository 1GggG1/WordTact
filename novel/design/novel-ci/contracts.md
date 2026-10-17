# Novel CI — 规范契约(单一事实源)

> 本文件是全部 WP 的接口冻结基准。WP 产出文件与本文冲突 = 验收失败。
> WP 作者把本文相应节**转写**进自己负责的 skill 文件时,可调整表述与详略,但不得改变语义。
> 发现契约缺陷:反馈包维护者修订本文,不得就地修正。

---

## §1 术语与场景生命周期

```text
scene 生命周期:
planned → card_confirmed → drafted → under_review → patching → accepted
                                          │
                                          └→ blocked(P0 未解 / 循环超限)
```

| 术语 | 定义 |
|------|------|
| canon | 已确认发生、后文必须遵守的事实集合(lockfile + bibles) |
| spec | 某一场景的写作规格 = scene_card |
| draft | 场景正文,唯一可编辑正文文件 |
| patch | 对 draft 的一次局部替换,含元信息 |
| regression | patch 后核查"原问题修复且未引入新问题" |
| watchlist | 由 RISK 沉淀、下一场 review 必查的关注项 |

## §2 严重度系统 P0—P3

| 级别 | 定义 | 动作 | 修改权限 |
|------|------|------|---------|
| **P0** | 破坏正典、角色、因果或世界规则 | 必须修复,阻断进入下一场景 | 允许整场重写,但必须书面说明为什么局部 patch 不足;重写后全量重测 |
| **P1** | 场景功能、冲突、节奏、后果、情绪转向或关键叙事呈现不足 | 必须修复 | 局部重构,单轮最多 3 个 patch;patch 后跑相关 tests + regression |
| **P2** | 句式、段落、语言、动作承载、AI 味 | 需要打磨 | 仅标点级 / 词级 / 句级 / 短段级;不得改变剧情事实、角色动机、信息权限、事件结果、世界规则 |
| **P3** | 风味、密度、审美偏好 | **默认不改**,用户点名才处理 | 极小范围可选调整 |

判级铁则:
1. 判级看**破坏对象**,不看文字量:一个词泄露信息权限是 P0;整段平淡只是 P1。
2. P3 是防过度修文的防线。把 P3 当 P1 处理是违规——文本越修越假多源于此。
3. 语言问题默认 P2;仅当语言错误造成事实/信息权限错误时升级(归入 P0,type 仍标注来源)。

## §3 测试输出协议

每个逻辑测试模块独立输出一个结果块:

```yaml
<module>_tests_result:
  status: PASS | FAIL | RISK        # FAIL=有确诊 failure;RISK=仅有风险项;PASS=两者皆无
  failures: []                       # FAIL 时必填,条目格式见下
  risks: []                          # 疑似/需观察项
```

**禁止输出**:"基本符合""整体不错""可以再加强"等一切不可定位、不可执行的评价。

### failure 条目格式(全系统统一)

```yaml
- severity: P0 | P1 | P2 | P3
  type: ""            # 见 §3.1 类型枚举
  location:           # 定位格式(全系统统一,LLM 无行号,以原文锚点定位)
    anchor: ""        # 逐字引用 draft 原文 ≤30 字
    para: 0           # 从 1 计数的段落序号
  issue: ""           # 为什么失败,一句话,具体
  evidence: ""        # 证据:引用 lockfile/bible/card 的具体字段或前文事实
  required_fix: ""    # 修复方向(不是替换文本;替换文本属于 patch 阶段)
```

### risk 条目格式

```yaml
- type: ""
  location: {anchor: "", para: 0}
  issue: ""
  watch: ""           # 下一场需要观察什么。ACCEPTED 后由 state_update 写入 lockfile.watchlist
```

### §3.1 failure type 枚举

`canon_conflict` `continuity_break` `unauthorized_knowledge` `character_ooc` `voice_drift` `scene_function_failure` `causality_break` `conflict_deficit` `flat_emotion` `missing_consequence` `genre_breach` `prose_lint` `reader_redundancy` `unauthorized_canon`(擅自新增设定)

## §4 Patch 协议

### patch_note 格式(markdown,追加写入 `*.patches.md`)

```markdown
## Patch <scene_id>-p<N>
- 等级:P1
- 类型:scene_function_failure
- 原位置:> 引用原文 1—3 句
- 问题:<对应 review_report 中的 failure>
- 修改意图:修什么,不修什么
- 替换为:> 新片段
- 自查:改变已确认设定?否 / 改变角色动机?否 / 改变信息权限?否 / 修复原问题?是 / 需更新 lockfile?是|否
```

### patch_plan(先出计划,经交互点确认后才执行)

```yaml
patch_plan:
  scene_id: ""
  round: 1                        # 本场景第几轮 patch(见循环上限)
  patches:
    - patch_id: ""                # <scene_id>-p<N>
      severity: ""
      failure_type: ""
      target: {anchor: "", para: 0}
      fix_strategy: ""
      estimated_scope: ""         # 标点级|词级|句级|短段级|片段重构
      risks: []
  full_rewrite_required: false
  reason_if_full_rewrite: ""
```

### 执行规则

1. 只修 review_report 点名的 failure;顺手修改未点名问题 = 违规。
2. 单轮 P1 patch ≤ 3 个;P2 采用能解决问题的**最小层级**(标点 < 词 < 句 < 短段)。
3. patch 输出片段替换,不输出全文。
4. **循环上限**:同一场景 patch→regression 循环最多 2 轮;第 2 轮后仍 NEEDS_MORE_PATCH → 判定场景规划缺陷,场景标记 `blocked`,回到 planning 重出 scene_card。
5. P0 整场重写不占用 patch 轮次,但一个场景最多整场重写 1 次;再次 P0 → `blocked` + 回 planning。

## §5 门禁总表

| Gate | 位置 | 通过条件 | 不通过时 |
|------|------|---------|---------|
| **A** Card Gate | scene_card 生成后 | 用户确认(auto 模式:对照 workflow-planning 自查清单通过) | 修改 card 重提 |
| **B** Review Gate | review_report 生成后 | 必验完整且绑定最终哈希后按最高严重度分流:P0→重写线;P1→patch 线;仅 P2→lint 线;仅 P3 或全 PASS→ACCEPTED | 进入对应处理线 |
| **C** Regression Gate | regression_check 后 | `result.status: ACCEPTED` | NEEDS_VERIFICATION 补验不计轮次;NEEDS_MORE_PATCH(≤2 轮)回 patch;超限或 BLOCKED 回 planning |
| **D** State Gate | 写 lockfile 前 | 场景状态 = accepted;state_update 只含正文已确认事实 | 拒绝写入 |
| **E** Chapter Gate | 章末 | chapter integration tests 完整且无 FAIL | 定位问题场景,回到该场景的 review/patch 或 planning |

硬规则:**未过 Gate B/C 的 P0、P1,不进入下一场景;未过 Gate D,不更新 canon。**

Gate A 的 auto 自查还必须确认:关键变化可沿 action→resistance/revelation→response 追踪;
转向有可见承载;前景/压缩/省略分配保留关键发现与决定;对话主导场景填写语言目标与策略
变化;POV 的信息边界、形式和注意力过滤一致。条件项不适用时写明原因,不得编造冲突。

## §6 交互点与 auto 模式

| 交互点 | 默认(interactive) | auto 模式(用户要求"连续写"时) |
|--------|-------------------|------------------------------|
| Gate A card 确认 | 停,等用户 | 自查通过即继续 |
| P0 重写方案 | 停,等用户 | **仍然停**(P0 永远需要人确认) |
| P1 patch_plan | 停,等用户 | 自动执行,patch_note 留档 |
| Gate E 章节报告 | 停,呈报 | 停,呈报 |

模式由用户话语触发(如"接下来两场连着写完再给我看"→ auto);SKILL.md 负责识别与声明当前模式。

## §7 项目状态目录契约

skill 只含方法论;以下全部位于**小说项目目录**(用户指定,记为 `<project>/`):

```text
<project>/
  canon/
    project-brief.yaml
    world-bible.yaml
    characters/<character_id>.yaml     # 一角色一文件
    lockfile.yaml                       # 含 timeline_position/open_threads/watchlist
    style/                              # 可选
      style-guide.md                    # 项目文风约定
      prose-benchmark.md                # 文风基准样本
      voice-samples.md                  # 角色声音样本
  manuscript/
    ch<NNN>/
      arc.yaml                          # chapter_arc:规划 + 进度 + 集成结果
      <NNN>-<SS>.card.yaml
      <NNN>-<SS>.draft.md               # 唯一正文文件,patch 直接应用于此
      <NNN>-<SS>.review.yaml            # 最近一次 review_report(覆盖写)
      <NNN>-<SS>.patches.md             # patch 历史(追加写)
```

### 必需性分级(lite 模式契约,D9)

| 文件 | full | lite 最小集 |
|------|------|------------|
| project-brief.yaml | 全字段 | 仅 genre.primary / narrative_mode.pov / tone.primary / core_premise |
| world-bible.yaml | 全字段 | 可缺省;首次出现世界规则时增量创建 |
| characters/*.yaml | 出场者全档 | 出场者仅 external_goal / voice.diction / must_not 三项 |
| lockfile.yaml | 完整 | 空骨架(字段齐全、内容为空),随写作增量填充 |
| style/ | 可选 | 可缺省 |

lite 模式下，未使用的可选字段记入覆盖说明；只有当前检查必需的证据缺失才产生 RISK 与 NEEDS_VERIFICATION。不能因档案较短伪造失败，也不能将实际未核对项算作通过。

## §8 Schema 全集

英文键、中文值;未用字段可省略;列表可为空。以下为**修正版**,以此为准。

### 8.1 project_brief(owner: state-layout.md)

```yaml
project_brief:
  title: ""
  genre: {primary: "", secondary: []}
  tone: {primary: "", avoid: []}
  target_reader_experience: []
  narrative_mode: {pov: "", tense: "", narrator_distance: ""}
  core_premise: ""
  central_conflict: ""
  thematic_pressure: []
  structural_preference: {chapter_length: "", scene_length: "", pacing: ""}
```

### 8.2 world_bible(owner: state-layout.md)

```yaml
world_bible:
  hard_rules:
    - {rule: "", consequence_if_broken: ""}
  soft_rules:
    - {rule: "", allowed_variation: ""}
  power_limits:
    - {entity: "", capability: "", limitation: ""}
  institutions:
    - {name: "", function: "", authority_limit: "", usual_behavior: ""}
  forbidden_world_moves: []
```

### 8.3 character_profile(owner: state-layout.md;一角色一文件)

```yaml
character_profile:
  character_id: ""            # ASCII slug(拼音),稳定不变;显示名另存 display_name
  display_name: ""
  role_in_story: ""
  external_goal: ""
  internal_need: ""
  default_strategy: ""
  fear_or_avoidance: ""
  moral_boundary: ""
  information_access: {knows: [], does_not_know: [], may_infer: []}
  voice: {diction: "", rhythm: "", typical_subtext: "", forbidden_lines: []}
  behavior_rules: {must: [], should: [], must_not: []}
  stress_response: {under_pressure: "", when_confused: "", when_cornered: ""}
  relationship_dynamics:
    - {with: "", default_pattern: "", tension: ""}
```

### 8.4 canon_lockfile(owner: state-layout.md;timeline/open-threads 已并入)

```yaml
canon_lockfile:
  current_time: ""
  current_location: ""
  timeline_position: ""        # 当前叙事时间点;confirmed_events 保持时间序即隐含时间线
  confirmed_events:
    - {event_id: "", summary: "", participants: [], public_knowledge: "", private_knowledge: ""}
  character_states:
    - character_id: ""
      location: ""
      physical_state: ""
      emotional_state: ""
      legal_or_social_status: ""
      resources: []
      constraints: []
      current_beliefs: []
      false_beliefs: []
  world_state:
    institutions:
      - {name: "", current_awareness: "", current_action: ""}
    public_pressure: ""
    resource_changes: []
  open_threads:
    - {thread_id: "", description: "", introduced_in: "", current_status: "", owner: "", urgency: ""}
  unresolved_consequences:
    - {source_event: "", expected_followup: "", deadline_or_trigger: ""}
  watchlist:                   # D7:RISK 的去向;下一场 review 必查后销项或续期
    - {watch_id: "", from_scene: "", issue: "", watch: "", status: open|cleared}
```

### 8.5 scene_card(owner: workflow-planning.md)

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

字段纪律:`entry_state.character_states[].goal` 仍是即时欲望的唯一来源;不复制 desire。
`power_shift` / `connection_shift` 至少说明一项,或明确“不适用”并由 `exit_state` 指出事实、
信念、资源或约束变化。`dialogue_dynamics`、`narratee`、`form` 是条件字段。
`deliberate_inaction` 是合法回应,不能把安静或拒绝自动判为空转。

### 8.6 chapter_arc(owner: workflow-planning.md;规划+进度+集成三段合一)

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

### 8.7 review_report(owner: workflow-review.md;修正版:无 scores)

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

### 8.8 regression_report(owner: workflow-regression.md)

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

### 8.9 state_update(owner: workflow-state-update.md;Gate D 后写入 lockfile)

```yaml
state_update:
  scene_id: ""
  confirmed_events: []
  character_state_changes:
    - {character_id: "", before: "", after: "", reason: ""}
  relationship_changes:
    - {characters: [], change: "", evidence: ""}
  world_state_changes:
    - {entity: "", new_awareness: "", new_action: ""}
  resource_changes:
    - {character_id: "", gained: [], lost: [], consumed: []}
  new_constraints: []
  open_threads_added: []
  open_threads_updated:
    - {thread_id: "", new_status: ""}
  consequences_to_track:
    - {source_event: "", expected_followup: "", urgency: ""}
  watchlist_changes:
    - {watch_id: "", action: add|clear|renew, issue: "", watch: ""}
```

铁则:**只记录正文中已确认发生的内容;作者计划、猜测、可能性不入 canon。**

## §9 命名与格式约定

- `scene_id`: `ch<NNN>-s<SS>`(零填充);`event_id`: `ev-<自增>`;`thread_id`: `th-<自增>`;`watch_id`: `w-<自增>`;`patch_id`: `<scene_id>-p<N>`。
- `character_id`:ASCII 拼音 slug,创建后永不改;中文名放 `display_name`。
- YAML:英文键中文值;引用原文的 anchor 必须逐字。
- review 文件覆盖写(只留最近);patches 文件追加写(留全史)。

## §10 Shared context, verification and sibling contracts

`user/novel-ci/references/project-context.md` owns task context and verification_record. It is a
shared service, not a requirement to start CI for ordinary expansion or auditing. Load current
author decisions with explicit scope and supersession; support agent/context and canon/style
without migrating historical files. Language rules have exactly one body in expander; auditor's
old filename forwards to it. Canonical sibling paths resolve in source and flat installations.

### 10.1 → novel-expander

Draft consumes the confirmed card and applicable context. Narrative craft remains expander's
responsibility. Standalone expansion performs two-pass self-check; CI generation returns draft
for separate review. When invocation fails, read the same shared references directly, without
substituting a copied abbreviated rule list. Missing required verification is explicit.

### 10.2 → novel-auditor

Ordinary standalone audits compose methods through
[audit planning](../../user/novel-auditor/references/audit-planning.md) before loading the full
review context. A fixed CI review/patch handoff is already selected: pass a bounded worker
assignment, not a request to plan another audit. Additional selected methods follow
[audit execution](../../user/novel-auditor/references/audit-execution.md); the coordinator owns
their dispatch and synthesis. Independent readers never receive CI diagnoses or the shared
review bundle. Reuse same-version evidence without changing mandatory CI checks or gate schemas.

Input includes prose and current hashes, author decisions, language profile, previous disclosures,
reader condition and edit scope. Language/punctuation → prose_lint; functionally redundant reading
→ reader_redundancy; factual/knowledge/voice failures retain their proper category and severity.
Missing invocation permits the current executor to run shared methods; missing checks themselves
produce SKIPPED and NEEDS_VERIFICATION. No unchecked acceptance.

An optional pinned `style_reference` from project context supplies language-distribution evidence
under auditor's `references/style-reference.md`. It carries source_group and applicability scope.
Pure deviations do not become automatic P2 failures; confirmed contextual language problems use
the existing routing. Explicit comparison requests report completion or evidence gaps. This adds
no scene-card field, test-results key, narrative-design responsibility or acceptance gate.

### 10.3 Verification completeness precedes acceptance

Keep P0–P3 severity and two repair rounds. P1 alone has the three-patch cap; P2 may apply a verified
batch. Unimplemented P3 suggestions need no regression; actual edits always need proportional
verification. RISK/SKIPPED on a required check, incomplete classification or stale evidence yields
NEEDS_VERIFICATION, which does not consume repair rounds. Known failures remain recorded.

Freeze original and latest accepted versions separately; compare real diffs and protected meaning.
Hash validation is provenance verification, not automatic semantic judgment. Follow final order:
punctuation → frequency recount → semantics → mapping → project acceptance → index commit.
Author decisions may correct an original error with evidence; reverting a bad candidate does not
resolve the baseline problem. Index only accepted prose; prior-only queries must reveal coverage
gaps and invalidate changed suffixes. See reader-index.md and revision-tools.md for schemas.

### 10.4 Scope and authorization

Existing explicit authorization satisfies its corresponding confirmation step; new choices
outside its scope still go to the author. Runtime schema owners above and the design mirror must
be changed together. Historical goal briefs describe the original build and cannot override this
updated contract.
