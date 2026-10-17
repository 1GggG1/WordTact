# Novel CI — Checks: Structure

> Loaded by: `workflow-review.md` (third cluster).
> Required context: `scene_card` + `draft`; Module 6 additionally reads earlier prose and reader context for reader_redundancy. Other structural modules do not invent external canon.
> Modules: scene_function, causality, conflict, emotion_curve, consequence, narrative_delivery.
> Test content source: `test-catalog.md` §C1–C6.

---

## Module 1: scene_function_tests（场景功能）

### Purpose

检查本场景是否完成了 `scene_card.target` 设定的功能目标，以及场景本身是否具有不可替代性。

### Test items

1. 本场景目标（target.one_sentence_goal）是否完成？
2. success_condition 是否达成？
3. 场景结束后局面是否变化？
4. 是否产生新信息？
5. 是否制造或解决误解？
6. 是否改变角色关系？
7. 是否改变风险等级？
8. 是否改变资源状态？
9. 是否留下后果？
10. 是否推进主线、支线或人物弧线？
11. 是否能从 `initiating_action` 追踪到 `resistance_or_revelation` 与 `response`？
12. 开头到结尾的力量或联系是否移动，或由 `exit_state` 明确记录其他变化？
13. 重大胜利是否检查 `cost_of_success`，重大失败是否检查 `if_goal_fails`？
14. 如果删掉本场景，故事是否明显缺失？

### 末项处置（可删性测试）

如果第 14 项答"不会缺失"→ 四种建议（按优先级排列）：
1. **删除** ——该场景无独立功能，信息可并入相邻场景。
2. **合并** ——该场景的部分信息有价值，合并到前一或后一场景。
3. **改写** ——赋予明确的场景功能（改变局面/关系/信息/风险之一）。
4. **转短过场** ——如果只需交代"角色 A 从地点 X 到了地点 Y"，压缩为 1-2 句过场而非完整场景。

### Severity guide

- **P1**: 目标明显未完成；局面、关系、风险、资源、误解全无变化；交代大量背景但无功能推进。
- **RISK**: 部分目标完成但非核心目标未达成；场景功能性偏弱但通过相邻场景可补足。

### Example FAIL output

```yaml
scene_function_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: scene_function_failure
      location: {anchor: "两人在茶馆中寒暄了一阵", para: 3}
      issue: "本场景交代大量背景信息，但关系、局面、风险、误解、资源全无变化——场景退化为信息说明书。"
      evidence: "scene_card.target.success_condition: '角色 A 说服角色 B 加入行动'；draft 中角色 B 从头到尾未表态。success_condition 未达成。"
      required_fix: "让角色 B 在场景末尾做出选择（加入/拒绝/拖延但暗示可能加入），使场景产生关系或局面的具体变化。"
  risks: []
```

---

## Module 2: causality_tests（因果链）

### Purpose

检查场景内的事件是否由前文因果驱动，而非"因为剧情需要所以发生"。

### Test items

1. 本场事件是否由前文触发？
2. 角色行动是否有动机？
3. 外部事件是否有来源？
4. 冲突升级是否有原因？
5. 转折是否有铺垫？
6. 结果是否由行动导致，而非作者强行安排？
7. 新信息或阻力是否真正引发决定、拒绝、策略变化或有代价的不行动？
8. 是否存在"因为剧情需要所以发生"的桥段？

### High-frequency failure patterns（check these first）

- 角色突然出现。
- 组织突然介入。
- 敌人突然犯蠢。
- 盟友突然帮忙。
- 线索突然送到。
- 冲突突然解除。

### Severity guide

- **P1**: "剧情需要"感明显——事件发生了但缺乏前因；角色行动缺乏可追溯的动机。
- **RISK**: 动机存在但铺垫过薄；读者需要自己脑补因果连接。

正典矛盾与信息越权由 `checks-canon.md` 判级；本模块只凭 card + draft 判断结构因果，
不得为了升到 P0 越界读取外部状态。

### Example FAIL output

```yaml
causality_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: causality_break
      location: {anchor: "正在这时，组织 B 的人突然破门而入", para: 18}
      issue: "组织 B 的出现无前因——读者不知道他们如何追踪到该地点、为何选择此时介入。"
      evidence: "scene_card.required_beats 与 entry_state 均未给出组织 B 的追踪来源；draft 前 17 段也无监视、线人或暴露位置的证据。"
      required_fix: "在 card 允许范围内补入可追溯的追踪证据；若需要新增组织行动，退回 planning 确认，不在 review 中擅改正典。"
  risks: []
```

---

## Module 3: conflict_tests（阻力与策略变化）

### Purpose

检查人物行动是否遇到真正的阻力并产生回应。冲突不等于打斗；安静场景也可由拒绝、
发现、关系微移或有代价的不行动成立。

### Test items

1. 本场是否存在明确阻力？
2. 阻力是否来自角色、制度、环境、误解、资源或时间压力？
3. 冲突是否在场景中升级？
4. 角色是否需要付出代价？
5. 是否有人想要不同的东西？
6. 是否有人隐瞒、误解、拖延、抗拒或反制？
7. 对话主导场景中，各方是否有语言目标、收到某种拒绝并出现策略变化？
8. 是否只是角色友好交换信息，且没有发现、决定、关系变化或其他功能？（是 → `conflict_deficit`）

### 冲突的九种形态（不仅是打斗）

信息不对称 / 目标不一致 / 权限不够 / 时间不够 / 资源不足 / 情绪压抑 / 误会扩大 / 代价变高 / 旁观变牵连。

### Severity guide

- **P1**: 场景完全是友好信息交换，无阻力、发现、决定或关系变化；card 指定的关键拒绝/策略变化没有落地。
- **RISK**: 阻力存在但其回应过弱，读者需要脑补策略如何改变。

若场景不是以对话争夺为核心，不因缺少语言策略变化而失败；不要为了通过本模块硬造争吵、
升级或代价。

### Example FAIL output

```yaml
conflict_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: conflict_deficit
      location: {anchor: "谢谢你告诉我这些", para: 27}
      issue: "整场以角色 A 和角色 B 友好交换信息为主，双方目标一致、态度友善、无阻力、无代价。"
      evidence: "scene_card.conflict.interpersonal: '角色 A 需要从角色 B 处获取信息，但角色 B 不愿透露'——card 指定的冲突在正文中未实现。"
      required_fix: "让角色 B 至少在一个信息点上回避、误导、或要求角色 A 付出代价才肯透露，使 card 指定的冲突落地。"
  risks: []
```

---

## Module 4: emotion_curve_tests（情绪曲线）

### Purpose

检查场景是否具有情绪变化——从开头到结尾情绪是否不同，变化是否由事件触发。

### Test items

1. 开头情绪是否明确？
2. 中段是否出现转向？
3. 结尾情绪是否不同于开头？
4. 转向是否由事件触发？
5. 情绪变化是否通过动作、对话、场景承载？
6. 持续同一情绪是否破坏本场约定的体验？稳定、克制或有意延宕不能仅因缺少转向判错。

### 转向模板（供对照参考）

> 平静→不对劲 | 安全→安全是假象 | 好笑→不舒服 | 流程→失控
> 误会→后果 | 试探→暴露 | 旁观→卷入 | 胜利→代价
> 救援→新麻烦 | 亲密→误伤 | 解释→更大的误解 | 控制→失控

约定的情绪变化没有实现且损害场景功能时属于 P1；不能把情绪变化本身设为所有场景的配额。

### Severity guide

- **P1**: 约定的情绪推进未实现且损害场景功能；情绪变化缺乏可推断触发；前后情绪无因果连接。
- **RISK**: 触发或承载证据不足；内心独白不是自动缺陷，先对照 POV 与场景目的。

### Example FAIL output

```yaml
emotion_curve_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: flat_emotion
      location: {anchor: "角色 A 从头到尾都保持着冷静的分析态度", para: 1}
      issue: "场景全程维持同一情绪温度（冷静分析），无转向。card.turn.emotional_shift 要求'自信→不安'，正文未体现。"
      evidence: "scene_card.turn.emotional_shift: '自信→不安'；draft 中角色 A 始终冷静，未出现不安的任何行为表征。"
      required_fix: "在中段设置一个触发事件（如角色 A 发现某个细节与预期不符），让角色 A 的情绪从自信滑向不安。"
  risks: []
```

---

## Module 5: consequence_tests（后果）

### Purpose

检查场景结束后世界是否因此改变。这是 state_update 阶段的反向清单——本模块的 FAIL 项指出了 lockfile 必须记录但可能被遗漏的变化。

### Test items

1. 谁知道了这件事？
2. 谁误解了这件事？
3. 谁被迫行动？
4. 哪个组织、家庭、团体、敌人或盟友需要记录此事？
5. 什么资源被消耗？
6. 什么关系被改变？
7. 什么边界被越过？
8. 什么风险被提高？
9. 什么伏笔被打开？
10. `turn.embodied_by` 的动作、物件或后果是否让转向可见？
11. 下一场为什么不能回到原状？

### 核心病灶

不是"没事发生"，而是**发生了很多事，但世界没有记住**。

本模块的 FAIL 清单与 `workflow-state-update.md` 的后果提取形成反向对照：凡是 consequence_tests 确诊的 FAIL，state_update 必须能定位到对应的后果记录项。如果 state_update 中找不到对应后果 → lockfile 遗漏。

### Severity guide

- **P1**: 场景有事件但无后果——检查项全否或几乎全否；后果有但不在 scene_card.consequence 范围内。
- **RISK**: 后果存在但未被显式确认；仅以暗示形式存在。

### Example FAIL output

```yaml
consequence_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: missing_consequence
      location: {anchor: "角色 A 转身离开了房间", para: 42}
      issue: "角色 A 当众揭露了角色 B 的秘密，但场景结束后无人记录、无人反应、无人被迫行动——大事件无后果。"
      evidence: "scene_card.consequence.immediate 要求'角色 B 的名誉受损，至少一人改变对角色 B 的态度'；draft 中现场角色的反应完全缺失。"
      required_fix: "在离开后添加至少一个旁观者的具体反应（震惊/议论/悄悄离开去报信），使后果可视化。"
  risks: []
```

---

## Module 6: narrative_delivery_tests（叙事呈现）

### Purpose

检查结构规格是否被读者实际经历：关键时刻是否获得前景篇幅，POV 契约是否自洽，背景与
细节是否提供可推断的证据。本模块不做句式密度审计。

### Test items

1. `time_handling.foreground` 是否保留发现、决定、拒绝、关系变化等关键时刻？
2. 惯例、重复劳动和无功能连接是否被 `compress` 或 `omit`，而非扩成空转场景？
3. 关键发现或决定是否被一句概述吞掉，导致 scene_card 目标无法体验？
4. POV 的 `narrator` / `narratee` / `form` / `narrative_distance` / `information_limit` 是否互相一致？
5. `attention_filter` 是否让背景和细节来自 POV 的专业、偏见、社会位置或物理限制？
6. 重点细节是否给读者提供推断、行动、压力、时代/阶层定位或物件追踪证据？
7. 反复物件是否先完成现实功能，而不是由叙述者直接宣布象征意义？
8. 相关前文已完成的解释、确认、决定和笑点，当前是否带来新的反应、误解、代价或读者提醒功能？无增量重复标 reader_redundancy。
9. 新听众被说服的过程有戏时是否被误压缩？人物听过、读者读过与角色此刻需要听见是不同条件。

### Severity guide

- **P1**: 关键发现/决定被错误概述，导致 card 的目标或转向无法体验；非默认叙述形式、对象或心理距离契约被正文破坏。
- **RISK**: 背景略泛、细节略多、物件意义略显直白，但未破坏结构目标。

信息泄漏仍归 `checks-canon.md` 的 information 模块，按其规则可判 P0。本模块不得按感官数、
比喻数、对话比例或场景冲突强度设置硬阈值；表层密度交给 prose_lint。

### Example FAIL output

```yaml
narrative_delivery_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: foreground_misallocation
      location: {anchor: "几天后，角色甲终于同意了", para: 12}
      issue: "决定只在跨时段概述中给出，读者没有经历触发、拒绝与回应，scene_card 的关键转向被吞掉。"
      evidence: "scene_card.time_handling.foreground 指定'角色甲听见条件后拒绝，再因新证据改变决定'；draft 只用一句结果概述跨过该过程。"
      required_fix: "把触发证据、拒绝和最终回应恢复为前景场景；其余数日的重复交涉继续压缩。"
  risks: []
```
