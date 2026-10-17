# WP7 Goal Brief — workflow-patch.md + workflow-regression.md + novel-auditor delta(修订层)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写修订层:patch 协议(限权修改)与回归检查(防漂移),并升级 novel-auditor 使其可被 CI 以标准格式调用。这是"修改要有限权、修完要回归"的落地处。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-ci/references/workflow-patch.md` | 新建,120—280 行 |
| `user/novel-ci/references/workflow-regression.md` | 新建,100—220 行 |
| `user/novel-auditor/SKILL.md` | **delta 修改**(不重写) |

## Required reading(按序)

1. `design/novel-ci/blueprint.md`(重点 §2 D8、§6 流程图的 patch/regression 环路)
2. `design/novel-ci/contracts.md` §2、§4(**全部**)、§5 Gate B/C、§6、§8.8、§10.2、§10.3
3. `user/novel-auditor/SKILL.md` **全文**(必须理解其两大原则与最小修改层级后才允许动它)

## Content requirements

### workflow-patch.md

1. 输入:review_report 的 failures(按 severity 分组)。
2. patch_plan schema 全文(owner,逐字转写 contracts §4)+ 交互点规则:plan 先行,interactive 模式等确认,auto 模式 P1 自动执行但 P0 永远等人(contracts §6)。
3. patch_note 格式全文(owner,逐字转写 contracts §4)+ 追加写入 `*.patches.md` 的纪律。
4. 分级执行线(content 层中文,各配一个抽象示例):
   - **P0 线**:先论证局部 patch 为何不足 → 用户确认 → 整场重写 → 全量重测(回 workflow-review 起点);每场仅 1 次,再犯 → blocked 回 planning。
   - **P1 线**:单轮 ≤3 patch;只动点名位置;修复策略优先"加铺垫/加后果/加转向"而非删减内容。
   - **P2 线**:委托 auditor 建议,执行时遵守最小修改层级(标点<词<句<短段);修辞打磨不得触碰事实、动机、信息权限。
   - **P3 线**:默认不动;用户点名才处理;完成后不进回归(P3 不算 patch 轮次)。
5. 反扩权纪律(醒目):顺手修改未点名问题 = 违规,即使"显然更好";发现新问题的正确动作是记入 risks,不是就地修。

### workflow-regression.md

1. 输入:本轮 patch_ids + patch 后 draft + 原 review_report。
2. regression_report schema 全文(owner,逐字转写 contracts §8.8)。
3. 七项检查的执行说明:每项怎么查、查什么范围(重点:scope_not_exceeded 用 patches.md 对照 draft 实际变更;voice_intact 对照 character_profile.voice)。
4. 三分支出口:ACCEPTED → workflow-state-update;NEEDS_MORE_PATCH(round<2)→ 回 patch;round≥2 或 BLOCKED → 场景 blocked,回 planning(D8)。round 计数写入报告。
5. 与全量重测的边界:regression 只针对 patch 影响面;P0 整场重写后走的是全量 review,不是本流程。

### novel-auditor delta(外科手术式,最小改动)

1. description 末尾追加一句(英文,风格一致):可被 novel-ci 以 CI 模式调用——输出映射为 CI failure 格式(确诊→P2 failure,疑似→risk),独立使用时行为完全不变。
2. 正文新增一节 `## CI mode(called by novel-ci)`(≤15 行):输入为 draft + 项目 style 文件;输出字段映射表(auditor 发现 → severity/type/location/issue/required_fix);疑似项映射为 risk 且注明"不自动修";最小修改层级即 P2 patch 的执行标准。
3. **禁止**:改动两大原则、审计流程、与 expander 的路由边界;maintainer notes 仅允许追加一行注明 CI mode。

## Conventions(红线)

- blueprint §9 全部适用;示例一律抽象占位。
- patch_plan/patch_note/regression_report 与 contracts §4/§8.8 逐字一致。
- 循环上限、轮次计数、P0 单次重写等数字与 contracts 一致,不得放宽或收紧。

## Acceptance checklist

- [ ] 四条分级执行线齐备,各有抽象示例
- [ ] 反扩权纪律醒目存在
- [ ] regression 七项检查各有执行说明;三分支出口与 Gate C 一致
- [ ] round 计数与 D8 上限机制可执行
- [ ] auditor delta:独立行为不变;CI mode ≤15 行;映射表字段与 contracts §3 一致
- [ ] 文件长度符合预算

## Out of scope

review 测试内容(WP6)、lockfile 写入(WP3)、expander 的任何改动(WP5)。
