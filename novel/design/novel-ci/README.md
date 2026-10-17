# Novel CI 骨架设计包

> 目标:在 `novel-superpower/user/` 下建成 `novel-ci` skill——规格驱动的小说写作流水线(spec → card → draft → tests → patch → regression → lockfile)。
> 本包是**设计交付物**,阅读对象是负责编写各工作包的执行代理与包维护者。

## 包内文件

| 文件 | 角色 |
|------|------|
| `blueprint.md` | 架构基准:决策、修正清单、文件树、模块归属、流水线、WP 划分 |
| `contracts.md` | **单一事实源**:严重度、协议、门禁、状态目录、全部 schema、sibling 委托 |
| `test-catalog.md` | 内容层原料:12 个测试模块条目、判级案例、转向模板、类型扩展 |
| `goals/wp1—wp7` | 七份工作包任务书,每份自包含 |

## 给工作包执行代理的分发模板

完整版见 `dispatch-prompt.md`(含背景、铁律、完成标准,可直接复制)。速记版:

```text
完成 novel-superpower/design/novel-ci/goals/<wpN>.md 定义的工作包。
工作目录:novel-superpower/。
先按 brief 的 Required reading 顺序读完再动笔;
产出必须通过 brief 的 Acceptance checklist 逐项自查;
发现契约缺陷 → 停下报告,不得就地修正 contracts.md。
```

## 构建顺序

```text
WP2(基座,先行)
  → WP3 / WP4 / WP5 / WP6 / WP7(接口已冻结,五包并行)
    → WP1(入口,最后收口校对)
```

并行的前提:所有跨包接口(schema 键名、文件名、门禁、type 枚举)已在 `contracts.md` 冻结。WP 之间禁止互相引用"对方将来会写的内容",只允许引用契约。

## 总集成验收(全部 WP 完成后,由维护者或 WP1 作者执行)

- [ ] `user/novel-ci/` 共 15 个文件(SKILL.md + 14 references),文件名与 blueprint §4 逐一对应
- [ ] 任选 3 个 schema(scene_card / review_report / state_update),在 owner 文件与 contracts §8 间 diff,零语义差异
- [ ] failure 条目六字段(severity/type/location/issue/evidence/required_fix)在 conventions、review、四个 checks 中格式一致
- [ ] 门禁 A—E、循环上限 2 轮、P0 单次重写:SKILL.md 与 conventions/patch/regression 三处数字一致
- [ ] watchlist 闭环可走通:review 产 risk → state-update 落 lockfile → 下一场 continuity 核查 → clear/renew
- [ ] expander/auditor 两个 delta:独立使用边界不变;expander 另有 narrative-craft 条件加载、standalone 预检/自查与 CI 字段映射
- [ ] 抽查语言分层:meta 层英文、content 层中文;无项目实例内容(具体角色名/作品设定)
- [ ] 干跑测试:虚构一个 lite 项目,人工走一遍 setup → card → draft → review → patch → regression → state-update,各阶段产物文件名与 state-layout 契约一致

## 维护规则

- 契约修改须同步运行时 owner 与 `contracts.md` 镜像，并执行契约测试；历史 WP brief 不覆盖现行契约。
- 外部原稿已被本包吸收并修正,后续以本包为准,不再回溯原稿。
