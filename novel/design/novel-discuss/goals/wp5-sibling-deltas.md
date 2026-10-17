# WP5 Goal Brief — Sibling Deltas(novel-ci 路由句 + novel-expander 适配改造)

## Mission

对两个既有 skill 做最小改造:novel-ci 加一句路由;novel-expander 修一个遗留路径 bug、
把 CI mode 泛化为通用调用契约、新增 sketch 档、补 standalone 项目感知。
**铁律:standalone 行为零变化(路径 bug 修复除外)。**

## Deliverables

| 文件 | 操作 |
|------|------|
| `user/novel-ci/SKILL.md` | 仅 description 追加一句(delta a) |
| `user/novel-expander/SKILL.md` | description 追加一句 + Step 5 改造 + "CI mode" 节重写为 "Invocation contract" + Step 2 前插入项目感知 + maintainer notes 追加(delta b/c1—c4) |

不新建任何文件。改动前先 `git diff` 确认工作区干净,改动后用 git diff 自查范围。

## Required reading(按序)

1. `design/novel-discuss/contracts.md` §4.7、§9(本 WP 的全部接口来源)
2. `user/novel-expander/SKILL.md` 全文(改造对象)
3. `user/novel-ci/SKILL.md` 的 description(改造对象)+ `user/novel-ci/references/`
   中任一 workflow 文件的 sibling 委托写法(措辞范本)
4. `design/novel-ci/contracts.md` §10.3(delta 义务的先例格式)

## Content requirements

### a) novel-ci description 路由句

追加语义(措辞自定,与既有 description 的路由句风格一致):用户想讨论/头脑风暴/纠结
大纲或写法而非直接产出 → novel-discuss;novel-discuss 的 handoff 简报(纪要文件)是
planning 阶段的合法输入。

### b) novel-expander description 路由句

追加语义:用户想讨论怎么写而非要正文 → novel-discuss。

### c1) 路径修复(Step 5 + 全文核查)

`/mnt/user-data/outputs/` 是 claude.ai 容器遗留路径,在其他 harness 中失效。改为环境
中立的三级次序:caller 指定路径 > 用户指定 > 当前工作目录下合理默认(如
`./expanded/<slug>.md`,落地前告知用户)。全文搜索同类容器路径一并处理。

### c2) "CI mode" → "Invocation contract"

重写该节为通用调用契约:caller 提供 `{input_spec, constraints_priority, output_path,
budget}`。budget 枚举三档:

| budget | 行为 | 现状对应 |
|--------|------|---------|
| `full` | 整章/多章扩写,完整 Step 1—5 + 全量自查 | standalone 默认 |
| `scene` | 单场景,scene_card 驱动,结构约束归 caller | 原 CI mode,行为逐字保留 |
| `sketch` | 2—3 个短变体(各 ≤500 字),探索性;自查只跑硬禁止层(Layer 1);输出到 caller 指定目录 | 新增,服务 novel-discuss(contracts §4.7) |

原 CI mode 的四条(input/priority/structural/output)全部保留为 `scene` 档内容,
零语义变化。novel-ci 侧无需任何改动——它的调用天然落入 `scene` 档。

### c3) standalone 项目感知(Step 2 前)

standalone 调用且检测到项目内存在 `canon/style/` 时:询问用户是否沿用项目文风
(style-guide/prose-benchmark/voice-samples)替代默认参数。一次询问,不强制。

### c4) maintainer notes 追加

anti-ai-patterns 同步段追加一行:两份拷贝现已同仓,重打包前跑
`diff user/novel-expander/references/anti-ai-patterns.md user/novel-auditor/references/anti-ai-patterns.md`
核对漂移。另追加一行记录本次 Invocation contract 改造的动机与"standalone 零变化"承诺。

## Conventions(红线)

- **改动范围仅限上述条目**,对照 git diff 审查;references/ 三个文件零改动;
  novel-auditor 零改动。
- `scene` 档与原 CI mode 语义逐字等价——novel-ci 的五处引用(workflow-draft 等)
  不因此改动而失效。
- description 是 YAML frontmatter 单行长字符串,追加时保持既有格式与引号转义。
- 语言分配沿用原文件既有分配,不迁移。

## Acceptance checklist

- [ ] git diff 仅触及两个 SKILL.md,改动条目与本 brief 一一对应
- [ ] `/mnt/user-data` 在 user/ 下 grep 为零命中
- [ ] `scene` 档四条与原 CI mode 逐字语义等价(对读)
- [ ] `sketch` 档参数与 discuss contracts §4.7 键名一致(budget/variants/length/output_dir)
- [ ] 两条 description 路由句与 novel-discuss 的 description(WP1 产出)互相指认、无死循环
      (若 WP1 未完成,留占位名 novel-discuss 即可,收口时由 WP1 校对)
- [ ] standalone 默认路径(full 档、无 caller、无用户指定)有合理落点且告知用户

## Out of scope

novel-discuss 本体全部文件(WP1—WP4)、novel-auditor、design/novel-ci/ 包内文件
(该包 §10 的先例仅作格式参考,不回写)。
