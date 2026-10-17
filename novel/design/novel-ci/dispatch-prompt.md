# WP 分发 Prompt(复制给负责单个工作包的执行代理,替换 <N> 为 1—7)

```text
完成 Novel CI skill 的工作包 WP<N>。

## 背景

仓库 novel-superpower/ 是一套小说写作 skill 库,现有 novel-expander(大纲→正文,anti-AI 文风)
和 novel-auditor(成稿诊断,最小修改)两个 skill。我们正在新建第三个 skill:novel-ci——
规格驱动的小说写作流水线(spec → scene_card → draft → tests → patch → regression → lockfile)。

完整骨架设计已冻结,位于 novel-superpower/design/novel-ci/:
- blueprint.md   架构基准(决策 D1—D10、文件树、模块归属、流水线)
- contracts.md   单一事实源(严重度、协议、门禁、全部 schema、sibling 委托)
- test-catalog.md 测试内容原料库
- goals/         七份工作包任务书

整个 skill 由 7 个工作包并行建造,你负责其中一个。你的产出会与其他 6 个执行代理的产出
直接拼装,因此接口纪律高于一切。

## 你的任务

1. 打开 novel-superpower/design/novel-ci/goals/ 下文件名以 wp<N>- 开头的任务书,
   它定义了你的 Mission、交付文件、内容要求与验收清单。
2. 严格按任务书 "Required reading" 的顺序读完全部指定材料,再动笔。
3. 在 novel-superpower/ 下按任务书的 Deliverables 表创建/修改文件。
   新建文件放在 user/novel-ci/ 对应路径;标注 "delta 修改" 的文件只做最小改动,不重写。

## 铁律(违反任何一条 = 交付无效)

1. contracts.md 是接口冻结基准:schema 键名、文件名、门禁数字、type 枚举必须逐字遵守。
   发现契约有缺陷或歧义 → 停下来书面报告,禁止就地修改 contracts.md 或在自己文件里"顺手修正"。
2. 单一事实源:不复制其他文件拥有的 schema 或规则全文,只引用文件名+节号,
   或按任务书要求列出你实际读写的字段名。schema 归属见 blueprint.md §5.2。
3. 语言分层:meta 层(流程结构、路由、加载规则、maintainer notes)用英文;
   content 层(测试条目、案例、写作规则等中文创作相关内容)用中文。不得互译。
4. 三层规则哲学:除 contracts.md 明确的 P0/P1 硬门禁外,禁止新增"违反一次即失败"的硬规则;
   密度类、风格类规则一律写成"警戒线 + 停下自查"。
5. 不引入项目实例内容:任何具体作品、角色名、题材设定不得进入 skill 文件;
   示例一律抽象占位(角色 A、事件 X)。
6. 文件预算:遵守任务书中每个文件的行数区间;超限先删减再考虑拆分,拆分需报告。
7. 只做任务书 Deliverables 列出的文件;Out of scope 列出的内容一个字都不写。

## 完成标准

- 逐项通过任务书末尾的 Acceptance checklist,并在最终回复中贴出自查结果(每项 ✅/❌ + 一句证据)。
- 最终回复附:交付文件清单、与 contracts.md 的接口对照说明(用了哪些 schema/节号)、
  发现的契约问题(如有)。
```

## 使用说明(给分发者)

- 一次会话只发一个 WP;WP2 先行完成后,WP3—WP7 可各开一个会话并行,WP1 最后收口。
- 若目标执行代理无文件系统访问权,把任务书 + Required reading 指定的文件内容按序粘贴在本 prompt 之后。
- 收到产出后,按 README.md 的"总集成验收"清单抽查。
