# WP6 Goal Brief — workflow-review.md + checks-*.md ×4(测试层)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写测试层五个文件:review 编排器(产出 review_report)与四个 checks 簇文件。结构簇增加 `narrative_delivery`,prose_lint 仍委托 auditor,不产出第五个 checks 文件。这是"失败要可定位"的落地处。

## Deliverables

| 文件 | 内含逻辑模块 | 行数预算 |
|------|------------|---------|
| `user/novel-ci/references/workflow-review.md` | 编排 + review_report schema(owner) | 120—250 |
| `user/novel-ci/references/checks-canon.md` | canon / continuity / information | 120—280 |
| `user/novel-ci/references/checks-character.md` | 通用层 / 角色专属层 | 100—220 |
| `user/novel-ci/references/checks-structure.md` | scene_function / causality / conflict / emotion_curve / consequence / narrative_delivery | 150—340 |
| `user/novel-ci/references/checks-genre.md` | genre 通用 + 类型扩展包 | 100—250 |

## Required reading(按序)

1. `design/novel-ci/blueprint.md`(重点 §5.1 聚类逻辑、§2 D4/D6/D7)
2. `design/novel-ci/contracts.md` §2、§3(**输出格式的全部**)、§8.7、§10.2
3. `design/novel-ci/test-catalog.md` **全文**(测试条目的单一来源,§A—§D 按文件对应转写)
4. `user/novel-auditor/SKILL.md` 的 "Two core principles"(疑似机制与最小修改——P2/RISK 处理的哲学基准)

## Content requirements

### workflow-review.md(编排器)

1. 执行序:canon → character → structure(六模块) → genre → prose_lint(委托),逐簇加载、逐模块输出结果块——**不允许一次性加载四个 checks 文件**。
2. review_report schema 全文(owner,逐字转写 contracts §8.7);failures 为全模块汇总,risks 同。
3. acceptability 判定规则:任何 P0 → BLOCKED;有 P1(无 P0)→ NEEDS_PATCH;仅 P2 → NEEDS_PATCH(lint 线);仅 P3/全 PASS → ACCEPTED。rewrite_permission 填写规则(仅 P0 且局部不可修 → full_rewrite: true + 理由)。
4. prose_lint 委托段:调用 auditor 时机、输入、输出映射(确诊→P2 failure、疑似→risk 不自动修)、SKIPPED fallback——转写 contracts §10.2,不复述语言规则。
5. watchlist 强制项:review 开始前从 lockfile 读 open watchlist,核查结果并入相应模块输出。
6. 反泛化纪律(醒目):每个 FAIL 必须有 anchor 定位 + evidence 引证;写不出 evidence 的 failure 降级为 risk。
7. 外部反馈先翻译为可观察症状和 2—3 个底层原因假设,再分派到现有模块验证;读者给出的解决方案不得直接变成 patch。

### checks-*.md ×4(转写 test-catalog §A—§D)

每个文件统一结构,每个逻辑模块一节:

1. 模块目的一句话 + 所需上下文(按 blueprint §5.1 表)。
2. 测试条目(test-catalog 语义不删改,可补充案例)。
3. 判级指引:该模块下什么是 P0、什么是 P1、什么只是 RISK(test-catalog 已给提示,须成文)。
4. 独立结果块输出示例(格式遵守 contracts §3,含一个 FAIL 示例演示 anchor/evidence 写法,内容抽象占位)。

个别文件补充要求:

- checks-canon.md:information 模块的 failure 与 character 测试第 7 条联动关系写清(归属 information,type: unauthorized_knowledge);continuity 模块含 watchlist 核查项。
- checks-character.md:角色专属层说明如何从 character_profile 动态生成逐角色测试;强调"稳定优先于讨喜"。
- checks-structure.md:scene_function 加入行动链、力量/联系变化和胜负代价;causality 检查发现是否引发回应;conflict 对对话主导场景条件检查语言目标、拒绝和策略变化;emotion_curve 附转向模板;consequence 检查 `turn.embodied_by` 并与 state_update 反向对照;narrative_delivery 检查场景/简述分配、POV 契约与细节证据。语言密度偏好默认 RISK,不得设置硬配额。
- checks-genre.md:按 project_brief.genre 选择性加载扩展段的机制;可新增 2—3 个类型包(每包 3—5 条,聚焦类型承诺与廉价解)。

## Conventions(红线)

- blueprint §9 全部适用;示例一律抽象占位。
- failure/risk 条目字段与 contracts §3 逐字一致;review_report 键名与 §8.7 逐字一致。
- 判级不得发明新等级或分数;不得把语言偏好类问题判为 P0/P1(除非造成事实/权限错误)。

## Acceptance checklist

- [ ] 全部逻辑模块落位于正确文件,structure 的六个模块各有独立结果块
- [ ] test-catalog 每个条目在对应文件中语义可寻
- [ ] 每模块有判级指引 + 一个含 anchor/evidence 的 FAIL 示例
- [ ] "写不出 evidence 降级为 risk"存在
- [ ] prose_lint 无自有规则条目,仅委托契约
- [ ] 外部反馈处方不会未经证据直接变成 patch
- [ ] 五文件长度符合各自预算

## Out of scope

patch/regression(WP7)、章节集成测试(WP4)、语言规则内容(expander canonical)。
