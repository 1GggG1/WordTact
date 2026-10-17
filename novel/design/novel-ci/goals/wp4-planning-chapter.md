# WP4 Goal Brief — workflow-planning.md + workflow-chapter.md(规划层)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写规划层两个工作流:章节规划与场景规划(产出 scene_card,流水线的 spec 源头),以及章末集成收口。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-ci/references/workflow-planning.md` | 新建,150—300 行(含两个大 schema,允许上限 300) |
| `user/novel-ci/references/workflow-chapter.md` | 新建,120—280 行 |

## Required reading(按序)

1. `design/novel-ci/blueprint.md`(重点 §2 D8/D10、§6)
2. `design/novel-ci/contracts.md` §5 Gate A/E、§6、§8.5、§8.6、§9
3. `design/novel-ci/test-catalog.md` §C4 转向模板、§E 全部
4. `user/novel-expander/references/expansion-workflow.md`(章节切分与长弧节奏的既有经验,可引用不可复制)

## Content requirements

### workflow-planning.md

1. **章节规划**:从 lockfile 当前局面 + open_threads/unresolved_consequences 推导本章目标 → 产出 `chapter_arc`(schema owner,逐字转写 contracts §8.6);scene_sequence 中每场必须有互不重复的 function。
2. **场景规划**:产出 `scene_card`(schema owner,逐字转写 contracts §8.5)。
3. **关键字段的填写指引**(content 层重点,示例一律抽象占位):why_this_scene_must_exist、success_condition、stakes、change_chain、dynamics、time_handling、dialogue_dynamics、pov、turn、consequence、exit_state、forbidden。条件字段必须说明何时填写、何时可写不适用。
4. **card 自查清单**(Gate A auto 模式的通过标准):目标一句话可判定;至少一种冲突非空;行动—阻力/发现—回应可追踪;turn 有可见承载;场景/简述/省略分配合理;对话主导场景有语言目标、拒绝和策略变化;POV 契约内部一致;consequence 与 exit_state 非空且互相呼应;forbidden 含对 lockfile 敏感项的防线;entry_state 与 lockfile 一致。安静场景与不适用条件不得为了过门禁而伪造激烈冲突。
5. **规划阶段的信息纪律**:entry_state 必须从 lockfile 抄录而非记忆复述;pov.information_limit 必须与该角色 profile 的 information_access 一致。
6. blocked 场景回流处理(D8):循环超限回到本流程时,先诊断 card 缺陷(通常是 success_condition 不可判定或 conflict 空心),重出 card 而非微调。

### workflow-chapter.md

1. 触发时机:arc.scene_sequence 全部 accepted。
2. chapter_integration_tests(转写 test-catalog §E1,输出格式遵守 contracts §3)+ 章节三问(§E2)。
3. 结果写入 `arc.yaml` 的 `integration_result`;FAIL 时按 Gate E 定位问题场景并给出回流建议(回 review / 回 planning)。
4. 在 `integration_result.emergent_patterns` 记录反复选择与代价、物件变化、关系模式、主题问题和反例；它只发现模式,不参与 Gate E,不自动把物件或主题升级为正典。
5. 章末汇报格式(交互点):三问答案 + open_threads 增减表 + 下一章可用的钩子清单 + 非门禁模式观察。

## Conventions(红线)

- blueprint §9 全部适用;示例一律抽象占位。
- scene_card/chapter_arc 字段与 contracts §8.5/§8.6 逐字一致(下游 WP5/WP6 依赖)。
- 不写 draft 生成规则(WP5)、不写场景级测试条目(WP6)。

## Acceptance checklist

- [ ] 两个 schema 与 contracts 逐字一致
- [ ] 新增常用字段与条件字段都有填写纪律,不为 schema 完整而硬填
- [ ] card 自查清单可机械执行(每条可答是/否)
- [ ] blocked 回流路径明确
- [ ] chapter_integration_tests 条目与 test-catalog §E1 语义一致
- [ ] emergent_patterns 明确为只观察、不定论、非门禁
- [ ] 文件长度符合预算

## Out of scope

正文生成、review 测试内容、patch 协议、lockfile 写入。
