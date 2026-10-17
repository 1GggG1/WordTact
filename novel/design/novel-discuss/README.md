# Novel Discuss 骨架设计包

> 目标:在 `novel-superpower/user/` 下建成 `novel-discuss` skill——多视角集思广益的
> 讨论室(consent 记忆 → lens 扇出 → 保留分歧的汇总 → 对话式讨论 → 决议与 handoff),
> 并完成 novel-ci / novel-expander 两个 sibling 的最小适配。
> 本包是**设计交付物**,阅读对象是负责编写各工作包的执行代理与包维护者。

## 包内文件

| 文件 | 角色 |
|------|------|
| `blueprint.md` | 架构基准:决策 D1—D12、文件树、lens 库总表、流程总图、WP 划分、红线 §8 |
| `contracts.md` | **单一事实源**:三轴、记忆目录、consent、schema 全集、扇出协议、三铁则、写边界、register 栈、sibling 委托与 delta |
| `lens-catalog.md` | 内容层原料:6 lens 章程 + 必答问题(WP3 转写主体) |
| `register-material.md` | 内容层原料:三份 harness 文档的 register 蒸馏(WP4 转写主体) |
| `dispatch-prompt.md` | 分发模板(含背景、铁律、完成标准,可直接复制) |
| `goals/wp1—wp5` | 五份工作包任务书,每份自包含 |

## 构建顺序

```text
WP2(基座:conventions + state-layout,先行)
  → WP3(lens+fanout) / WP4(session+register) / WP5(sibling deltas)(并行)
    → WP1(SKILL.md 入口 + 总集成校对,最后)
```

并行前提:跨包接口(schema 键名、lens_id、档位名、handoff 格式)已在 `contracts.md`
冻结。WP 之间禁止互相引用"对方将来会写的内容",只允许引用契约。

## 总集成验收

以 `goals/wp1-skill-entry.md` 的 Acceptance checklist 第二组为准(7 文件对应、schema
对读、三铁则四处一致、sketch 边界两侧一致、`/mnt/user-data` 零命中、干跑走通)。

## 设计不变量(改包前必读)

- **三铁则**(contracts §6):独立首轮 / 署名分歧强制 / 主持人立场强制。本 skill 的
  存在价值,任何修订不得弱化。
- **安全层零内容 + 解压即用**(blueprint §8 红线 8/9)。
- **写边界**(contracts §7):默认只写 agent/discuss/;lockfile / bible / manuscript 无例外。
- register 蒸馏三规则:targets not personas / signals not examples / density not
  elimination;依据保持模型无关,不引用个人 memory。

## 维护规则

- 契约变更只改 `contracts.md`,同步检查受影响 WP 产物;blueprint 决策表(D1—D12)
  变更需用户确认。
- lens 库增删属决策级变更(动 D3 + contracts §5.1 枚举),需用户确认。
