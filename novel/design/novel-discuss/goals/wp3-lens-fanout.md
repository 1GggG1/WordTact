# WP3 Goal Brief — lens-catalog.md + workflow-fanout.md(扇出机器)

## Mission

编写 lens 库与扇出编排两份文件:6 个 lens 的章程与笔记义务,以及开场扇出、deep 二轮、
无子代理降级、点名咨询的完整编排规则。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-discuss/references/lens-catalog.md` | 新建,120—280 行 |
| `user/novel-discuss/references/workflow-fanout.md` | 新建,100—240 行 |

## Required reading(按序)

1. `design/novel-discuss/blueprint.md` 全文(重点 D2/D3/D4/D7/D8/D12、§5、§8 红线)
2. `design/novel-discuss/contracts.md` §2、§4.2、§5、§6(本 WP 的接口来源)
3. `design/novel-discuss/lens-catalog.md`(内容层原料,转写主体)
4. `user/novel-ci/references/workflow-review.md` 浏览一遍(多模块编排文件的成熟范本)

## Content requirements

### lens-catalog.md(转写设计原料 + contracts §4.2、§5.1、§5.4)

1. 通用章程(原料"通用章程"节):固定视角定位、独到优先、证据锚点义务、真实立场义务、
   电报体。全部保留,可润色。
2. 六个 lens 各一节:视角定义、必答问题、取材倾向、model_hint。lens_id 与原料逐字一致;
   必答问题不得删减(可补充);contrarian 的"真论证义务 + 无可反驳时报告检验路径"必须保留。
3. lens_note schema(contracts §4.2)逐字转写——本文件是该 schema 的 owner。
4. 模式默认组合表(contracts §2.1 的 lens 列)+ contrarian 永不默认出场规则。

### workflow-fanout.md(转写 contracts §5 + §6 的执行面)

1. 扇出时机与前置条件:standard/deep 档、议题已澄清、digest 可用(或 stateless 等价物)。
2. 单 lens 输入包(§5.2)逐项转写;**独立性铁则**原文强度保留。
3. explore / stress 两变体的扇出 prompt 骨架(给主持人的模板,含 lens 章程与议题的拼装
   方式;骨架用占位符,不含具体项目内容,不含示例句)。
4. 并行执行指引 + **无子代理降级**(D12):串行逐 lens 自问自答,前一笔记不进后一 lens
   工作上下文;声明"由 harness 能力决定手段,原则不变"。
5. deep 档第二轮(§5.3):回传范围、每 lens 限 1 条、超限只取第一条、二轮后定稿。
6. 按需点名咨询(§5.5):单发、输入包差异(允许携带争论焦点)、返回格式不变。
7. 收笔笔记的验收:主持人检查每份 lens_note 是否有 stance、evidence 锚点或"推断"标注;
   不合格的笔记退回重出一次(仅一次,再不合格则弃用并在汇总中注明)。
8. model_hint 的使用与忽略规则(§5.4)。

## Conventions(红线)

- blueprint §8 全部适用(特别是红线 3:独立性与三铁则不得弱化;红线 9:解压即用,
  降级路径必须完整可用)。
- lens_id、schema 键名与 contracts 逐字一致。
- 扇出 prompt 骨架不得包含 persona 指令、示例句、安全层内容(红线 4/8)。
- 汇总(meeting_material)的产出规则**不属于本 WP**(owner: workflow-session,WP4),
  fanout 文件到"全部笔记收齐并验收"为止。

## Acceptance checklist

- [ ] 六 lens 齐全,必答问题与原料逐条对应,contrarian 约束完整
- [ ] lens_note schema 与 contracts §4.2 逐字一致
- [ ] 独立性铁则在输入包与降级两处均有,措辞未弱化
- [ ] explore/stress 骨架无示例句、无 persona、无安全内容
- [ ] deep 二轮限 1 条规则与 contracts §5.3 数字一致
- [ ] 两文件行数达标;meta 层英文、content 层中文

## Out of scope

汇总与对话主持(WP4)、digest 构建(WP2 已写)、SKILL.md 路由(WP1)、sibling 改动(WP5)。
