# WP2 Goal Brief — conventions.md + state-layout.md(规范基座,先行)

## Mission

编写 novel-discuss 的两份基座文件:全系统规范(术语/三轴/三铁则/写边界/交互点)与
记忆目录契约(agent/discuss/ 布局 + consent 协议 + digest/纪要/决议 schema)。其余 WP 以
这两份为术语与格式基准。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-discuss/references/conventions.md` | 新建,120—280 行 |
| `user/novel-discuss/references/state-layout.md` | 新建,120—280 行 |

## Required reading(按序)

1. `design/novel-discuss/blueprint.md` 全文(重点 §2 决策表、§8 红线)
2. `design/novel-discuss/contracts.md` **全文**(本 WP 是契约的主要转写者)
3. `user/novel-ci/references/conventions.md` + `state-layout.md`(基座文件的成熟范本:
   结构、密度、语言分配)

## Content requirements

### conventions.md(转写 contracts §1、§2、§6、§7 + §8 的栈次序)

1. 术语表与讨论生命周期(§1);主持人"带立场的与会者"定位原文保留。
2. 模式×变体×强度三轴(§2 三表),含用户显式覆盖规则、开场白声明义务。
3. **防和稀泥三铁则**(§6)完整转写,含"确无分歧时写各自路径"的例外处理与 light 档豁免。
4. 写边界表(§7)逐行转写,lockfile/bible/manuscript 的"无例外"措辞不得软化。
5. Register 栈优先级次序(§8 的 1→2→3 + 豁免区),细则指向 register-discussion.md,不复制。
6. Stateless 模式行为差异(§3.4)。

### state-layout.md(转写 contracts §3、§4 + §10)

1. agent/discuss/ 目录树(§3.1)+ 各文件读写者(谁读/谁写/何时;harness/ 只读义务)。
2. Consent 协议(§3.2)完整转写。
3. digest 构建与新鲜度(§3.3):CI 项目路径 / 无 CI 路径、指纹校验、增量刷新、
   decisions-active 闭环。
4. Schema 全文:digest(§4.1)、session_minutes(§4.4)、decision 条目(§4.5,含
   冲突指认义务与唯一回改例外)。字段名逐字保留,可补一句中文注释。
5. 命名与写模式约定(§10:kebab-case、session_id/decision-id 格式、追加写 vs 覆盖写)。

## Conventions(红线)

- blueprint §8 全部适用。
- schema 键名与 contracts **逐字一致**——下游 4 个 WP 依赖这些键名。
- conventions.md 不含目录/schema 内容;state-layout.md 不含流程步骤与 lens 内容。
- meeting_material / lens_note / handoff / sketch 四个 schema **不属于本 WP**(owner 分别
  是 workflow-session / lens-catalog),不得抢写。

## Acceptance checklist

- [ ] contracts §1/§2/§6/§7 的每个表、每条铁则在 conventions.md 中语义完整
- [ ] 三铁则措辞未被弱化(与 contracts §6 对读)
- [ ] digest/minutes/decision 三 schema 字段与 contracts §4 逐字一致
- [ ] consent 拒绝路径(stateless)在两文件中说法一致
- [ ] 两文件均 ≤280 行;meta 层英文、content 层中文

## Out of scope

lens 章程(WP3)、扇出编排(WP3)、对话主持与收口流程(WP4)、register 细则(WP4)、
SKILL.md(WP1)、sibling 改动(WP5)。
