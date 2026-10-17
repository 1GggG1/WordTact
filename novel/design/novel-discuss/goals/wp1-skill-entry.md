# WP1 Goal Brief — SKILL.md(入口,最后收口)

## Mission

编写 novel-discuss 的入口文件 SKILL.md,并执行全包收口校对。前置:WP2—WP5 全部完成。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-discuss/SKILL.md` | 新建,120—260 行 |

外加收口校对义务(见 Acceptance 第二组)。

## Required reading(按序)

1. `design/novel-discuss/blueprint.md` 全文
2. `design/novel-discuss/contracts.md` 全文
3. `user/novel-discuss/references/` 已产出的全部 6 个文件(WP2—WP4 产物)
4. `user/novel-ci/SKILL.md`(入口文件范本:frontmatter 格式、加载路由表、maintainer notes)
5. `user/novel-expander/SKILL.md` 与 `user/novel-ci/SKILL.md` 的 description(WP5 改后版,
   校对互相指认)

## Content requirements

### frontmatter description

沿家族格式:一句功能定位 + 中文触发短语列表(如 "讨论大纲""聊聊怎么写""头脑风暴"
"帮我想想""这个设定怎么展开""开头怎么写好""stress test 一下我的想法" 等,自行扩充到
8—12 个)+ 英文等价 + 路由边界四句(→ci 产正文、→expander 自由扩写、→auditor 诊断成文、
←两 sibling 的讨论类请求)。与 WP5 改后的两条 description 互相指认、无死循环。

### 正文结构(参照 novel-ci SKILL.md 的密度)

1. **Core principles**:讨论室定位(不产正文不改正典)、三铁则、写边界三类无例外、
   consent 先行。数字与 references 一致。
2. **流程总图**(blueprint §6 的压缩版,text 块)。
3. **三轴速查表**(模式×变体×强度,契约 §2 的压缩)+ 开场白声明义务。
4. **模块加载路由表**(blueprint §4:四阶段各载哪两个文件,任意时刻 ≤3 个 reference)。
5. **Reference files 表**:6 个文件各一行"何时加载"。
6. **Maintainer notes**(英文):语言分配声明;schema 单一归属表(digest/minutes/decision
   → state-layout;lens_note → lens-catalog;meeting_material/handoff/sketch →
   workflow-session);sibling 委托与 fallback 所在位置;三铁则不得弱化;安全层零内容
   +解压即用两条红线(blueprint §8 红线 8/9)原文引入。

### 收口校对(本 WP 的第二职责)

对照下方 checklist 第二组逐项核对全包一致性;发现不一致 → 修 references 侧或报告
维护者(schema 冲突归 contracts 裁决),不得静默放过。

## Conventions(红线)

- blueprint §8 全部适用。
- SKILL.md 不复制任何 schema 正文、lens 章程、register 细则——只路由。
- description 触发词覆盖三模式与两变体的自然说法,但不得与 ci/expander/auditor 的
  触发词正面冲突(routing boundary 句负责消歧)。

## Acceptance checklist

**本文件:**
- [ ] description 含中英触发词 + 四句路由边界,与两 sibling(WP5 版)互相指认
- [ ] 加载路由表与 blueprint §4 一致;任意阶段 ≤3 reference
- [ ] 三铁则、写边界、consent 在 principles 中出现且数字/措辞与 conventions.md 一致
- [ ] maintainer notes 含 schema 归属表 + 安全零内容 + 解压即用
- [ ] ≤260 行;meta 英文、content 中文

**全包收口:**
- [ ] user/novel-discuss/ 共 7 文件,名字与 blueprint §4 逐一对应
- [ ] 抽 3 个 schema(lens_note / meeting_material / decision)在 owner 文件与 contracts
      间对读,零语义差异
- [ ] 三铁则在 conventions / fanout / session / SKILL.md 四处措辞强度一致
- [ ] "sketch 永不进 manuscript/"在 session 与 expander Invocation contract 两侧一致
- [ ] lens_id、档位名、session_id/decision-id 格式全包 grep 一致
- [ ] `/mnt/user-data` 全仓 user/ 零命中(WP5 复核)
- [ ] 干跑:虚构一个带 canon/ 的项目,人工走 consent → digest → 议题 → standard 扇出
      → 汇总 → 对话(含一次点名、一次决议冲突指认)→ 收口 handoff,各产物路径与
      state-layout 契约一致

## Out of scope

references/ 内容重写(只允许收口性小修)、sibling 再改动、design 包回写。
