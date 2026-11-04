# Novel Discuss — 骨架设计蓝图

> 系统定位、架构决策、文件树、模块归属、流程总图、WP 划分。
> 阅读对象:各 WP 的执行代理与包维护者。契约细节一律以 `contracts.md` 为准。

---

## 1. 系统一句话定义

多视角集思广益的**讨论室**:开场并行扇出若干 lens 子代理各自出独立笔记,主持人汇总为
保留分歧的会议材料,随后进入对话式讨论,收口产出决议与移交简报。它**不产正文、不改正典**
——生产归 novel-ci / novel-expander,诊断归 novel-auditor,本 skill 只产共识与分歧。

与对抗式多 agent 审计的区别:目标不是互相攻击找错,是**思路多样性**;分歧是产出的一部分,
不是要消除的噪音。

---

## 2. 架构决策(已定,不接受 WP 层面翻案)

| # | 决策 | 内容 | 理由 |
|---|------|------|------|
| D1 | 单 skill 三模式 | novel-discuss 一个入口,模式 = outline / writing / free | 机器同构(拉上下文→扇出→汇总→对话),差别只在默认 lens 组合与取材;记忆共享 |
| D2 | 扇出节奏 | 开场扇出一次;对话阶段主持人单人;按需点名单 lens 再咨询 | 每回合扇出又慢又贵且打断节奏 |
| D3 | 固定 lens 库 | 6 个 lens(见 §5),按模式配默认组合,用户可点名增减;contrarian 默认不出场 | 每次现编视角质量不稳定,库化才能沉淀 prompt 质量 |
| D4 | 防和稀泥三铁则 | ①首轮笔记独立生成,lens 互不可见 ②汇总强制署名分歧节,空=不合格 ③主持人必须给自己的推荐+理由 | 本系统最大风险是汇总成"都有道理"的浆糊;集思广益的价值恰在分歧处 |
| D5 | 记忆 consent | 首次使用询问,同意→建 `<project>/agent/discuss/`;拒绝→stateless 慢速模式,每次全量拉取 | 防止每次启动重拉全仓库;用户对项目目录有知情权 |
| D6 | 写边界 | 默认只写 `agent/discuss/`,结论以 handoff 简报移交 novel-ci;用户明确要求直改项目文件时,逐文件确认后可写(lockfile/bible 仍禁) | 讨论室不越权落正典;直改是显式例外不是常态 |
| D7 | 扇出两变体 | explore(开放探索)/ stress(立场压测:用户带方案来,各 lens 出支持/反驳/修正) | "帮我 stress test 这个想法"是高频场景,值得一等公民 |
| D8 | 强度三档 | light(不扇出,主持人单聊)/ standard(默认,3—4 lens)/ deep(全员+Delphi 第二轮,每 lens 限 1 条反驳) | "快速聊两句"不该惊动全委员会 |
| D9 | register 栈 | 对话阶段:用户 harness 插槽 > 本 skill 讨论增量 > 包内 novel-conversation;子代理笔记电报体豁免 | register 目标而非 persona 扮演;示例句会被逆向归纳;个人偏好不进入通用包 |
| D10 | 决议演化 | decisions.md 条目带 status(active/superseded);新决议与旧决议冲突时主持人必须指认并问旧理由是否仍成立 | 长篇项目三个月后没人记得当初为什么那样定 |
| D11 | 试写委托 | 委托 novel-expander sketch 档(2—3 短变体);产物只存 agent/discuss/ 会话目录,**永不写 manuscript/** | 复用 sibling,零新机器;"三种开头各试一段"是写作讨论刚需 |
| D12 | 无子代理降级 | harness 不支持并行子代理时,串行逐 lens 自问自答;独立性规则照守(前一 lens 笔记不进后一 lens 的工作上下文) | 解压即用,不绑定单一 harness |

---

## 3. 与 sibling skills 的关系

```text
novel-discuss(讨论室:共识/分歧/决议)
  ├─ 移交 → novel-ci planning(handoff 简报为输入;讨论→生产的接口)
  ├─ 委托 → novel-expander(sketch 档试写;D11)
  └─ digest 构建 ← novel-ci 项目状态(lockfile/bibles 本来就是压缩态)
novel-auditor:无交互(诊断已完成正文,与讨论无接口)
```

路由边界(写进各 description):
- 用户想**讨论/头脑风暴/纠结怎么写** → novel-discuss
- 用户要**按流水线产正文** → novel-ci;要**自由扩写正文** → novel-expander
- 用户带**成文求诊断** → novel-auditor

Delta 义务:novel-ci 与 novel-expander 的 description 各加一句路由(WP5);
expander 另有独立适配改造(见 §7)。

---

## 4. 最终文件树(skill 本体)

```text
user/novel-discuss/
  SKILL.md                              # 入口:路由/模式/强度/流程总图/加载路由(WP1)
  references/
    conventions.md                      # 术语/三铁则/强度档/写边界/交互点(WP2)
    state-layout.md                     # agent/discuss/ 目录契约 + digest/纪要/决议 schema + consent 协议(WP2)
    lens-catalog.md                     # 6 lens 章程 + 模式默认组合 + 笔记格式(WP3)
    workflow-fanout.md                  # 扇出编排:explore/stress、deep 二轮、降级、点名咨询(WP3)
    workflow-session.md                 # 对话主持:议题澄清/汇总/冲突提醒/收口/handoff(WP4)
    register-discussion.md              # 讨论 register + harness 插槽协议(WP4)
```

7 文件。模块加载路由(SKILL.md 实现,任意时刻 ≤3 个 reference 在上下文):

| 阶段 | 加载 |
|------|------|
| 启动/consent/记忆检查 | conventions.md + state-layout.md |
| 扇出 | workflow-fanout.md + lens-catalog.md |
| 对话讨论 | workflow-session.md + register-discussion.md |
| 收口/移交 | workflow-session.md + state-layout.md |

---

## 5. Lens 库(6 个,内容层原料见 lens-catalog 设计原料)

| lens_id | 视角 | outline 默认 | writing 默认 |
|---------|------|:---:|:---:|
| structure | 结构与因果:节拍、信息投放、伏笔回收、因果链 | ✓ | ✓ |
| character | 人物与心理:动机、弧光、关系张力、视角人物内在一致 | ✓ | ✓ |
| culture | 文化与世界观:设定自洽、文化细节质感、时代/地域肌理 | ✓ | — |
| language | 语言与文体:叙事声音、语域、节奏、意象系统 | — | ✓ |
| reader | 读者与类型:类型契约、期待管理、爽点/钩子、市场惯例 | ✓ | ✓ |
| contrarian | 唱反调:专攻共识盲点(仅点名出场,不进任何默认组合) | opt-in | opt-in |

free 模式:主持人按议题从库中自选 3—4 个,向用户报告选择及理由。

---

## 6. 流程总图

```text
路由(模式×变体×强度) → 记忆检查
  ├─ 无 agent/discuss/ → consent 询问 → 同意:初始化并构建 digest / 拒绝:stateless
  └─ 有 → digest 新鲜度校验(源指纹) → 过期部分增量刷新
→ 议题澄清(主持人;含开放问题回捡:上次搁置的要不要捡)
→ [light 档直接跳对话] 扇出(standard/deep;explore 或 stress)
    各 lens:digest + ≤3 个定向原文件 → 独立笔记(电报体,互不可见)
    [deep 档] 第二轮:汇总回传各 lens,每人限 1 条反驳或补强
→ 主持人汇总 → 会议材料(收敛点/署名分歧/开放问题/选项;主持人推荐+理由)
→ 对话式讨论(主持人单人带材料;register 栈生效)
    · 按需点名单 lens 再咨询(单发,不全员)
    · 试写需求 → 委托 expander sketch 档 → 草样存会话目录
    · 点子撞正典 → 依 digest canon 摘要即时指认
    · 新方向与 active 决议冲突 → 指认旧决议及理由,问是否 supersede
→ 收口:会议纪要(sessions/)+ 决议写入 decisions.md(状态机)
  + [有 novel-ci 项目] handoff 简报 → 提议移交 planning
  + 开放问题汇入 digest(下次回捡)
```

---

## 7. WP 划分与构建顺序

```text
WP2(基座:conventions + state-layout,先行)
  → WP3 / WP4 / WP5(接口冻结后并行)
    → WP1(入口 SKILL.md,最后收口校对)
```

| WP | 交付物 | 依赖 |
|----|--------|------|
| WP2 | conventions.md + state-layout.md(含 digest 构建/刷新/回捡逻辑) | contracts 全文 |
| WP3 | lens-catalog.md + workflow-fanout.md | WP2 |
| WP4 | workflow-session.md + register-discussion.md | WP2 |
| WP5 | sibling deltas:novel-ci 一句路由;novel-expander 适配改造(路径修复/Invocation contract/sketch 档/项目感知/路由句/diff 自查) | WP2(sketch 契约) |
| WP1 | SKILL.md | 全部 |

并行前提:跨包接口(schema 键名、文件名、lens_id、档位名、handoff 格式)已在 contracts.md 冻结。
WP 之间禁止引用"对方将来会写的内容",只允许引用契约。

---

## 8. 每个 WP 的通用红线

1. 语言分配:meta 层(流程/路由/加载/维护注记)英文;content 层(lens 章程、register 材料、
   一切中文创作语境规则)中文。禁互译。
2. schema 键名与 contracts 逐字一致;schema 单一归属,消费方引用文件名+节号,不复制。
3. 防和稀泥三铁则(D4)在任何文件中不得弱化:不得把"署名分歧"降为可选,不得允许主持人
   只当记录员。
4. 禁 persona 指令与好/坏示例句(D9 依据);register 材料只写 register 目标与评估信号。
5. 写边界(D6)措辞不得松动:默认态对项目文件零写入,唯一出口是 agent/discuss/ 与 handoff。
6. 不复制 sibling 的规则内容,委托 + fallback 一句话即可(照 novel-ci contracts §10 模式)。
7. 文件行数各 ≤280 行;发现契约缺陷 → 停下报告,不得就地改 contracts.md。
8. **安全层零内容**:拒答策略、身份声明、心理安全指引等一律不进 skill——那是 API 供应商
   的层(源材料 agent.md 前言自己声明的边界)。蒸馏 harness 材料时同规则剔除。提示词
   预算已经很重,安全样板文只消耗注意力、不新增任何供应商未强制的东西。
9. **解压即用**:零安装步骤、零外部依赖、零脚本;所有 sibling 委托必须带一句话 fallback
   (sibling 缺位时独立可用);路径一律相对用户项目根,不绑定任何 harness 的容器路径。
   面向小说作者,不是工程师——任何需要"配置"的设计都算失败。
