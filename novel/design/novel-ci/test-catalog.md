# Novel CI — 测试目录(内容层原料库)

> 供 WP6(checks-*.md、workflow-review.md)与 WP4(workflow-chapter.md)转写使用。
> 本文是测试**内容**的单一来源;输出格式、severity 判级、failure 条目结构一律以 `contracts.md` §2—§3 为准,本文不重复。
> 转写要求:测试条目语义不得删改;可以补充案例;每个模块须在目标文件中保留独立结果块输出。

---

## A. checks-canon.md 的三个模块

### A1. canon_tests(正典一致性)

```yaml
canon_tests:
  - 是否违反 world_bible 的硬规则?
  - 是否违反 canon_lockfile 的已确认事件?
  - 是否错误改变角色状态?
  - 是否错误改变物品、资源、伤势、位置?
  - 是否错误改变组织权限或世界机制?
  - 是否提前触发尚未触发的事件?
  - 是否把未确认内容写成已确认事实?
  - 是否引入未授权的新设定?(type: unauthorized_canon)
```

P0 典型案例(抽象):

- 违反世界观硬规则;能力边界被临时改写;组织权限写错。
- 物品 / 伤势 / 身份 / 关系状态与 lockfile 冲突。
- 时间线冲突;前文明确禁止的情节被写入。

### A2. continuity_tests(连续性)

```yaml
continuity_tests:
  - 当前时间是否接续上一场?
  - 当前地点是否合理接续?
  - 角色身体状态是否连续?
  - 角色情绪状态是否有过渡?
  - 角色资源是否正确继承?
  - 角色关系是否正确继承?
  - 上一场留下的后果是否没有被清空?
  - 本场是否错误跳过必要反应?
  - lockfile.watchlist 中 status=open 的条目是否逐一核查?(D7 强制项)
```

长篇高频翻车点:受伤角色下一场没事;被追捕者随便出门;已曝光身份没人知道;用掉的资源又出现;上一场大事件世界毫无反应。

### A3. information_tests(信息权限)

```yaml
information_tests:
  - 每个角色是否只知道自己有渠道知道的信息?
  - 是否有人说出作者视角才知道的内容?
  - 是否有人过早推理出缺乏证据的真相?
  - 是否有人忘记自己已经知道的信息?
  - 是否有人错误误解或错误地不误解?
  - 信息传播路径是否存在?
  - 秘密是否被不合理泄露?
```

P0 案例(抽象):lockfile 记录角色 A 不知道事件 X,本场景角色 A 直接引用事件 X 细节 → `unauthorized_knowledge`,required_fix: 删除该认知,或补足信息传播路径。

## B. checks-character.md 的两层模块

### B1. general_character_tests(所有出场角色)

```yaml
general_character_tests:
  - 角色是否按照自己的 default_strategy 行动?
  - 角色是否违反自己的 moral_boundary?
  - 角色是否因为剧情需要突然变聪明?
  - 角色是否因为剧情需要突然变蠢?
  - 角色是否说了只有作者才会说的话?
  - 角色是否承担了不属于自己的主题表达?
  - 角色是否掌握了不该掌握的信息?(与 A3 联动,failure 归 A3)
  - 角色声音是否能与其他角色区分?(type: voice_drift)
  - 角色在压力下的反应是否符合 stress_response?
```

### B2. character_specific_tests(逐角色,基于其 profile 生成)

```yaml
character_specific_tests:
  character_id: ""
  tests:
    - 是否保持该角色的默认行动策略?
    - 是否保持该角色的语言节奏(voice.rhythm)?
    - 是否没有越过该角色的道德边界?
    - 是否没有说出 voice.forbidden_lines 类台词?
    - 是否没有让该角色替作者讲道理?
    - 是否没有为推进剧情而失真?
```

判级提示:严重 OOC(违反 must_not / moral_boundary / 信息权限)= P0;声音趋同、strategy 轻微偏移 = P1 或 RISK。角色测试的重点不是"讨喜",而是"稳定"。

## C. checks-structure.md 的六个模块

### C1. scene_function_tests(场景功能)

```yaml
scene_function_tests:
  - 本场景目标(target.one_sentence_goal)是否完成?
  - success_condition 是否达成?
  - 场景结束后局面是否变化?
  - 是否产生新信息?
  - 是否制造或解决误解?
  - 是否改变角色关系?
  - 是否改变风险等级?
  - 是否改变资源状态?
  - 是否留下后果?
  - 是否推进主线、支线或人物弧线?
  - 是否能从 initiating_action 追踪到 resistance_or_revelation 与 response?
  - 开头到结尾的力量或联系是否移动,或由 exit_state 明确记录其他变化?
  - 重大胜利是否检查 cost_of_success,重大失败是否检查 if_goal_fails?
  - 如果删掉本场景,故事是否明显缺失?
```

末项答"不会"→ 建议:删除 / 合并 / 改写为功能明确的场景 / 转短过场。
P1 案例(抽象):本场交代大量背景,但关系、局面、风险、误解、资源全无变化 → `scene_function_failure`。

### C2. causality_tests(因果链)

```yaml
causality_tests:
  - 本场事件是否由前文触发?
  - 角色行动是否有动机?
  - 外部事件是否有来源?
  - 冲突升级是否有原因?
  - 转折是否有铺垫?
  - 结果是否由行动导致,而非作者强行安排?
  - 新信息或阻力是否真正引发决定、拒绝、策略变化或有代价的不行动?
  - 是否存在"因为剧情需要所以发生"的桥段?
```

高频失败形态:角色突然出现 / 组织突然介入 / 敌人突然犯蠢 / 盟友突然帮忙 / 线索突然送到 / 冲突突然解除。通常 P1,破坏正典因果时 P0。

### C3. conflict_tests(冲突密度)

```yaml
conflict_tests:
  - 本场是否存在明确阻力?
  - 阻力是否来自角色、制度、环境、误解、资源或时间压力?
  - 冲突是否在场景中升级?
  - 角色是否需要付出代价?
  - 是否有人想要不同的东西?
  - 是否有人隐瞒、误解、拖延、抗拒或反制?
  - 对话主导场景中,各方是否有语言目标、收到某种拒绝并出现策略变化?
  - 是否只是角色友好交换信息,且没有发现、决定、关系变化或其他功能?(是 → conflict_deficit)
```

冲突不等于打斗:信息不对称 / 目标不一致 / 权限不够 / 时间不够 / 资源不足 / 情绪压抑 / 误会扩大 / 代价变高 / 旁观变牵连。
条件纪律:非对话争夺场景不因没有语言策略变化而失败;安静场景可由拒绝、关系微移、发现或
`deliberate_inaction` 成立,不得硬造激烈冲突。

### C4. emotion_curve_tests(情绪曲线)

```yaml
emotion_curve_tests:
  - 开头情绪是否明确?
  - 中段是否出现转向?
  - 结尾情绪是否不同于开头?
  - 转向是否由事件触发?
  - 情绪变化是否通过动作、对话、场景承载?
  - 持续同一情绪是否破坏本场约定的体验?(不能仅因稳定或克制判错)
```

转向模板(供 review 对照、也供 WP4 规划 turn 字段引用):

```text
平静→不对劲 | 安全→安全是假象 | 好笑→不舒服 | 流程→失控
误会→后果 | 试探→暴露 | 旁观→卷入 | 胜利→代价
救援→新麻烦 | 亲密→误伤 | 解释→更大的误解 | 控制→失控
```

约定的情绪推进未实现并损害功能时属于 P1；不设置适用于所有场景的转向配额。

### C5. consequence_tests(后果)

```yaml
consequence_tests:
  - 谁知道了这件事?
  - 谁误解了这件事?
  - 谁被迫行动?
  - 哪个组织、家庭、团体、敌人或盟友需要记录此事?
  - 什么资源被消耗?
  - 什么关系被改变?
  - 什么边界被越过?
  - 什么风险被提高?
  - 什么伏笔被打开?
  - turn.embodied_by 的动作、物件或后果是否让转向可见?
  - 下一场为什么不能回到原状?
```

核心病灶:不是"没事发生",而是**发生了很多事,但世界没有记住**。本模块 FAIL 项是 state_update 阶段的反向清单——凡确认的后果必须落 lockfile。

### C6. narrative_delivery_tests(叙事呈现)

```yaml
narrative_delivery_tests:
  - time_handling.foreground 是否保留发现、决定、拒绝、关系变化等关键时刻?
  - 惯例、重复劳动和无功能连接是否被 compress 或 omit,而非扩成空转场景?
  - 关键发现或决定是否被一句概述吞掉,导致 scene_card 目标无法体验?
  - POV 的 narrator / narratee / form / narrative_distance / information_limit 是否互相一致?
  - attention_filter 是否让背景和细节来自 POV 的专业、偏见、社会位置或物理限制?
  - 重点细节是否给读者提供推断、行动、压力、时代/阶层定位或物件追踪证据?
  - 反复物件是否先完成现实功能,而不是由叙述者直接宣布象征意义?
  - 当前是否无增量地复述前文已完成的解释、确认、决定或笑点?(reader_redundancy)
  - 是否保留新听众被说服、误解、反应及追更提醒的真实功能?
```

判级:关键发现/决定被错误概述或 POV 形式契约破坏,通常 P1;信息泄漏仍归 A3/P0。
背景略泛、细节略多、象征略明显默认 RISK;不得按感官数量、比喻数量或对话比例设硬阈值。

## D. checks-genre.md

### D1. genre_tests(通用类型契约)

```yaml
genre_tests:
  - 本场是否满足 primary genre 的读者期待?
  - 是否没有破坏题材基调(tone.avoid)?
  - 是否有符合类型的压力来源?
  - 是否避免了不属于该类型的廉价解决方案?
  - 是否保持类型承诺,而不是只借用外壳?
```

### D2. 类型扩展包(按 project_brief.genre 选择性加载)

```yaml
horror_tests:
  - 是否存在不安全感?
  - 是否有未知、污染、侵入、失控或禁忌?
  - 是否避免过早解释恐怖来源?
romance_tests:
  - 是否推动关系动态?
  - 是否存在欲望、误解、靠近或退缩?
  - 是否没有让角色直接说穿所有情绪?
mystery_tests:
  - 是否提供线索?
  - 是否隐藏关键信息但保持公平?
  - 是否避免侦探无根据神推理?
political_tests:
  - 是否有权力结构?
  - 是否有利益冲突?
  - 是否有公开理由和真实理由的差异?
action_tests:
  - 行动是否清楚?
  - 空间关系是否可理解?
  - 代价是否存在?
  - 是否避免无后果爽感?
```

WP6 可按同构模式补充其他类型(如 xianxia / 系统文 / 都市),每包 3—5 条,聚焦该类型的"承诺与廉价解"。

## E. workflow-chapter.md 用(WP4)

### E1. chapter_integration_tests

```yaml
chapter_integration_tests:
  - 各场是否有可说明的作用？
  - 接续和因果是否清楚？
  - 节奏是否服务本章目标？
  - 关键变化是否落实？
  - 后果是否保留？
  - 关系与声音是否可信？
  - 信息状态是否清楚？
  - 资源、风险和动作状态是否一致？
  - 未回收线索是否可追踪？
  - 章尾是否完成适合的停顿？
  - 本章提供什么阅读价值？
  - 是否重复已完成的叙事功能？
  - 词频、标点与实际修改是否完成验证？
```

### E2. 章节三问(章末必答,写入 arc.integration_result 附注)

```text
本章开始时是什么局面?
本章让读者经历、理解或见证了什么?
这些内容怎样接入后文?
```

### E3. emergent_patterns(非门禁观察)

章末另记录:反复出现的选择与代价、反复出现或变化的物件、关系重复模式、文本目前暗示的
主题问题、与 `thematic_pressure` 相冲突的证据。它只负责发现,不自动把主题写成结论,
也不把物件登记为象征;内容不得改变 E Gate 的 PASS/FAIL。

## F. prose_lint 说明(不产出 checks 文件)

P2 语言检查完整委托 `novel-auditor`(contracts §10.2)。其规则清单 canonical 源:`novel-expander/references/anti-ai-patterns.md`。WP6 在 workflow-review.md 中只写:调用时机、输入、输出映射、直接执行共享方法的 fallback；必验缺失时 NEEDS_VERIFICATION——**不得**在 novel-ci 内复述语言规则条目。
