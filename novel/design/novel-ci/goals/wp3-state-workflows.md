# WP3 Goal Brief — workflow-setup.md + workflow-state-update.md(状态层)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写状态层两个工作流:项目初始化(建立 canon 状态)与场景通过后的状态更新(维护 canon 状态)。两者是 lockfile 的唯一写入者。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-ci/references/workflow-setup.md` | 新建,120—280 行 |
| `user/novel-ci/references/workflow-state-update.md` | 新建,120—280 行 |

## Required reading(按序)

1. `design/novel-ci/blueprint.md`(重点 §2 D2/D7/D9)
2. `design/novel-ci/contracts.md` §5 Gate D、§7、§8.4、§8.9、§9
3. `design/novel-ci/test-catalog.md` §C5(consequence 清单是 state_update 的反向对照表)

## Content requirements

### workflow-setup.md

1. **三种初始化模式**:
   - full:访谈式逐档建立(brief → world_bible → 主要角色 → lockfile 空骨架)。
   - lite:按 state-layout.md 的最小集快速起步;声明增量补全规则。
   - **存量文稿冷启动**:用户已有章节时,从既有文本反向提取 brief/bible/lockfile **草案**,逐项请用户确认后落盘——未经确认不得写入 canon。
2. 访谈问题设计(content 层中文):每个状态对象 3—6 个高杠杆问题,直接映射 schema 字段;避免一次性问卷轰炸,按对象分轮。
3. 铁则:**setup 阶段不发明设定**。所有写入内容必须来自用户输入或用户确认的提案;LLM 的建议必须标注为提案。
4. 完成校验清单:目录结构符合 state-layout;lockfile 骨架字段齐全;每个已建角色有 character_id(拼音 slug)。

### workflow-state-update.md

1. 输入:accepted 的 draft + 对应 review_report 的 risks + 现行 lockfile。
2. `state_update` schema 全文(owner;逐字转写 contracts §8.9)。
3. 生成流程:对照 test-catalog §C5 十问逐项提取后果 → 填 state_update → **以 diff 视角**呈现 lockfile 变更(before/after)→ 应用写入。
4. watchlist 维护:本场 risks → `action: add`;上一场 open 条目已核查 → `clear` 或 `renew`。
5. 同步职责:更新 `arc.yaml` 中该场景 `status: accepted`;confirmed_events 追加保持时间序。
6. 铁则(醒目呈现):只记录正文已确认发生的内容;作者计划、猜测、可能性不入 canon。Gate D:非 accepted 场景到达本流程 = 直接拒绝。

## Conventions(红线)

- blueprint §9 全部适用;示例一律抽象占位(角色 A、事件 X)。
- lockfile/state_update 字段名与 contracts §8.4/§8.9 逐字一致。
- 不复制 lockfile schema 全文(owner 是 state-layout.md),只列本流程实际写入的字段路径。

## Acceptance checklist

- [ ] 三种初始化模式齐备;冷启动模式含"逐项确认"步骤
- [ ] "不发明设定"与"只记确认事实"两条铁则显著存在
- [ ] state_update schema 与 contracts §8.9 逐字一致
- [ ] watchlist add/clear/renew 全生命周期覆盖
- [ ] lockfile 变更以 diff 形式呈现的要求存在
- [ ] 两文件均 ≤280 行

## Out of scope

不定义 lockfile schema(WP2);不写章节规划(WP4);不写 review/patch 流程(WP6/WP7)。
