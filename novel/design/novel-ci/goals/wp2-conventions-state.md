# WP2 Goal Brief — conventions.md + state-layout.md(规范基座)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写 novel-ci 的两份基座文件:全系统规范(严重度/测试协议/patch 权限/门禁/交互点)与项目状态目录契约(状态文件布局 + 状态对象 schema)。其余全部模块以这两份文件为术语与格式基准。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-ci/references/conventions.md` | 新建,120—280 行 |
| `user/novel-ci/references/state-layout.md` | 新建,120—280 行 |

## Required reading(按序)

1. `design/novel-ci/blueprint.md` 全文(重点 §2 D4/D7/D8/D9、§9)
2. `design/novel-ci/contracts.md` **全文**(本 WP 是契约的主要转写者)
3. `user/novel-expander/SKILL.md` 的 "Three-layer rule structure" 一节(三层规则哲学的表述范本)

## Content requirements

### conventions.md(转写 contracts §1—§6 + §10 的 fallback 红线)

1. 术语表与 scene 生命周期(§1)。
2. P0—P3 严重度表 + 三条判级铁则(§2)。
3. 测试输出协议:PASS/FAIL/RISK 定义、禁止泛泛评价、failure/risk 条目格式、location 锚点格式、type 枚举(§3 全部)。
4. Patch 权限与执行规则:含循环上限 2 轮、P0 重写仅 1 次(§4)。
5. 门禁总表 Gate A—E(§5)+ 交互点/auto 模式表(§6)。
6. **最小语言红线**(fallback 用,§10.1):AI 签名式成句禁用 / 章尾总结升华与俗套悬念禁用 / 输出纯正文。必须注明 canonical 源为 `novel-expander/references/anti-ai-patterns.md`,此处仅为 sibling 不可用时的降级拷贝。
7. **三层规则哲学与 P0—P3 的映射**(英文小节):P0/P1 = hard gate;P2 = strong recommendation(警戒线+自查,配合 auditor 的疑似机制);P3 = suggestion(默认不动)。明示:除 P0/P1 gate 外禁止新增"违反一次即失败"的规则,理由引 expander 的防御性回避论证。

### state-layout.md(转写 contracts §7—§9 的状态部分)

1. 项目状态目录树(§7)+ 各文件读写者说明(谁读、谁写、何时)。
2. 必需性分级表:full vs lite 最小集;lite 下状态缺失 → RISK 而非 FAIL(§7)。
3. Schema 全文:project_brief、world_bible、character_profile、canon_lockfile(§8.1—8.4,字段名逐字保留,可为字段补一句中文注释)。
4. 命名约定:各类 ID 格式、character_id 拼音 slug 规则、review 覆盖写/patches 追加写(§9)。
5. 增量补全规则:lite 起步的项目何时、如何把状态补厚(首次触发某世界规则/角色首次出场时就地补档)。

## Conventions(红线)

- blueprint §9 全部适用。
- schema 字段名与 contracts §8 **逐字一致**——下游 5 个 WP 依赖这些键名。
- conventions.md 不含状态文件内容;state-layout.md 不含流程步骤。

## Acceptance checklist

- [ ] contracts §1—§6 的每个表、每条铁则在 conventions.md 中语义完整
- [ ] watchlist 生命周期(add/清查/clear/renew)在两文件中说法一致
- [ ] 四个状态 schema 字段与 contracts §8.1—8.4 逐字一致
- [ ] 最小语言红线注明 canonical 源
- [ ] 两文件均 ≤280 行

## Out of scope

不写测试条目(WP6)、不写 scene_card/review/patch 等流程 schema(归 owner WP)、不写初始化访谈流程(WP3)。
