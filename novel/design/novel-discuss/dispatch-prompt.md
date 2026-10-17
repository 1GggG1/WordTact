# WP 分发 Prompt(复制给负责单个工作包的执行代理,替换 <N> 为 1—5)

```text
完成 novel-superpower/design/novel-discuss/goals/wp<N>-*.md 定义的工作包。

## 背景

novel-superpower 是一组解压即用的小说创作 skill(novel-ci 流水线 / novel-expander 扩写 /
novel-auditor 审稿)。本次新增 novel-discuss:
多视角集思广益的讨论室——开场并行扇出若干 lens 子代理出独立笔记,主持人汇总为保留
分歧的会议材料,进入对话式讨论,收口产出决议与移交简报。它不产正文、不改正典。

设计包位于 design/novel-discuss/:
- blueprint.md — 架构决策(D1—D12)、文件树、流程总图、WP 划分、通用红线(§8)
- contracts.md — 单一事实源:三轴、记忆目录、全部 schema、扇出协议、三铁则、写边界、
  register 栈、sibling 委托
- lens-catalog.md / register-material.md — 内容层原料(WP3/WP4 转写主体)

## 你的任务

工作目录:novel-superpower/。
先按 goal brief 的 Required reading 顺序读完再动笔;
按 brief 的 Content requirements 产出交付物;
产出必须通过 brief 的 Acceptance checklist 逐项自查并在交付说明中报告结果。

## 铁律(违反任何一条 = 交付无效)

1. schema 键名、lens_id、档位名、目录名与 contracts.md 逐字一致;schema 单一归属,
   消费方引用文件名+节号,不复制正文。
2. 防和稀泥三铁则(contracts §6)不得弱化:独立首轮 / 署名分歧强制 / 主持人立场强制。
3. 禁 persona 指令、禁好/坏示例句、**禁任何安全层内容**(拒答策略/身份声明/心理安全
   指引归 API 供应商)。register 材料只写 register 目标与评估信号。
4. 解压即用:零安装、零脚本、零外部依赖;sibling 委托必带一句话 fallback;路径相对
   用户项目根,不绑定任何 harness 容器路径。
5. 语言分配:meta 层英文、content 层中文,禁互译。
6. 写边界(contracts §7)措辞不得松动;lockfile/bible/manuscript 三类"无例外"。
7. 发现契约缺陷 → 停下报告,不得就地修改 contracts.md 或 blueprint.md。
8. 不触碰 goal brief 的 Out of scope 列表中的任何文件。

## 完成标准

- 交付物文件齐全、行数达标(见 brief)
- Acceptance checklist 逐项自查通过并附报告
- 若为 WP5:git diff 范围与 brief 条目一一对应
```

## 使用说明(给分发者)

- 构建顺序:WP2 先行 → WP3/WP4/WP5 并行 → WP1 收口。
- 并行前提:contracts.md 已冻结;WP 之间禁止引用"对方将来会写的内容"。
- WP1 兼任总集成校对,其 checklist 第二组即验收单。
- 各 WP 的执行代理无本对话上下文,brief + 本 prompt + 设计包三件套必须自足。
