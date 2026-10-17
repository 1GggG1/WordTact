# WP5 Goal Brief — workflow-draft.md + novel-expander delta(生成层)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写 draft 生成协议(结构层),并升级 novel-expander 使其承接 CI 流程内的叙事呈现与语言层生成。核心分工:novel-ci 管**写什么/不能写什么**,expander 管**怎么让读者看见变化**以及具体怎么写。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-ci/references/workflow-draft.md` | 新建,120—250 行 |
| `user/novel-expander/SKILL.md` | **delta 修改**:接入 standalone 预检、自查顺序与 CI 映射 |
| `user/novel-expander/references/narrative-craft.md` | 新建,叙事呈现层的六个条件加载模块 |

## Required reading(按序)

1. `design/novel-ci/blueprint.md`(重点 §2 D3、§7)
2. `design/novel-ci/contracts.md` §8.5(scene_card 字段,消费者视角)、§10.1、§10.3
3. `user/novel-expander/SKILL.md` **全文**(必须理解其规则层次与 maintainer notes 后才允许动它)
4. `user/novel-expander/references/narrative-craft.md`（已实现的叙事呈现契约）

## Content requirements

### workflow-draft.md

1. **输入**:已确认(card_confirmed)的 scene_card + lockfile 相关切片 + 出场角色 profiles。无确认 card 不得进入本流程(Gate A 前置)。
2. **Draft Generation Rules**(结构层十条,content 层中文):严格遵守 scene_card;不新增未授权设定;不改变 lockfile 已确认事实;不让角色获得未授权信息;不替角色说作者观点;不用说明书方式交代设定;重要信息通过动作/对话/环境/后果承载;场景必须有情绪转向;结尾落在具体状态变化而非空泛悬念;draft 阶段不自我解释、不自评。
3. **叙事呈现与语言层委托**(转写 contracts §10.1):加载 expander 的 `narrative-craft.md` 与表层规则;优先级 scene_card.prose_constraints/forbidden > 项目 canon/style/ > expander 默认;fallback 指向 conventions.md 最小语言红线。
4. **required_beats 的使用纪律**:beats 是必经点不是分段模板——禁止一 beat 一段的机械展开;beats 之间的连接材料由冲突与 POV 视角驱动。
5. **长度与产出**:目标字数来自 scene_card 或 project_brief.structural_preference;产出写入 `<NNN>-<SS>.draft.md`;纯正文,无标题注释自评。
6. **完成即测**:draft 落盘后不润色、不自读回改,直接进入 workflow-review(防止未测先修)。

### narrative-craft.md

1. 六个模块:细节是证据、叙事时间分配、行动链、对话策略、视角与背景、物件与主题纪律。
2. 规则采用条件加载;不设置感官、比喻、对话比例或冲突强度的固定配额。
3. 不复制书摘、练习题或既有 anti-ai 句式规则。

### novel-expander delta

1. standalone Step 1 改为三项最低预检,按对话、跨时段、特殊文体、重点背景启用条件项。
2. standalone 扩写后先做叙事呈现检查,再做 anti-AI 表层检查。
3. CI 模式直接消费 scene_card,将 change_chain、dialogue_dynamics、time_handling、pov、turn.embodied_by、dynamics 映射给 craft 模块;生成完成后不自修,直接交给 review。
4. scene_card/canon 约束高于 expander 默认建议;与 auditor 的既有路由边界不变。

## Conventions(红线)

- blueprint §9 全部适用。
- workflow-draft.md 不复述任何 expander 语言规则条目(D3)。
- delta 改动以 diff 思维执行:改动行数最小化,现有行为完全保留。

## Acceptance checklist

- [ ] 结构层十条规则齐备且无一条涉及具体句式/词汇(那是语言层)
- [ ] 优先级链与 contracts §10.1 一致;fallback 指向正确
- [ ] "完成即测,不先润色"存在
- [ ] expander standalone 与 CI 两条路径均明确,CI 不重复规划也不自我评测
- [ ] narrative-craft 六模块可按场景条件加载,且无固定数字配额
- [ ] 文件长度符合预算

## Out of scope

测试内容(WP6)、patch(WP7)、scene_card 定义(WP4)、auditor 的任何改动(WP7)。
