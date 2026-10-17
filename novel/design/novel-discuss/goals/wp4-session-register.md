# WP4 Goal Brief — workflow-session.md + register-discussion.md(对话与收口)

## Mission

编写讨论主持与收口流程,以及讨论场景的 register 文件:议题澄清、汇总、对话主持、
正典冲突指认、决议演化、试写委托、纪要与 handoff。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-discuss/references/workflow-session.md` | 新建,140—280 行 |
| `user/novel-discuss/references/register-discussion.md` | 新建,80—180 行 |

## Required reading(按序)

1. `design/novel-discuss/blueprint.md` 全文(重点 D2/D4/D6/D10/D11、§6、§8 红线)
2. `design/novel-discuss/contracts.md` §1、§4.3—§4.7、§6、§7、§8、§9.1—9.2
3. `design/novel-discuss/register-material.md`(register 内容层原料,转写主体)

## Content requirements

### workflow-session.md

1. **议题澄清**:把用户诉求收敛为一句话议题 + 三轴declaration(模式/变体/强度);
   开放问题回捡(digest.open-questions 非空时,开场问一句要不要捡)。
2. **汇总**:meeting_material schema(contracts §4.3)逐字转写——本文件是 owner。
   三铁则(§6)在汇总步骤中逐条落地:分歧挖掘方法(立场差/stance 冲突/evidence 强度差)、
   "确无分歧写各自路径"、moderator_take 必填。汇总以自然语言呈现,YAML 归档。
3. **对话主持**:主持人单人带材料;按需点名咨询的触发与回收(引用 workflow-fanout,
   不复制);**正典冲突指认**(依 digest.canon-summary,一句话点出撞了哪条);
   **决议冲突指认**(D10:引用 decisions.md 条目、复述 because、问是否 supersede)。
4. **试写委托**(D11):sketch 参数(contracts §4.7)逐字转写——本文件是 owner;
   expander 不可用时 fallback(主持人自写单变体粗样,显式标注);草样永不进 manuscript/。
5. **收口**:纪要写入(引用 state-layout 的 schema,不复制);decision 条目写入与
   supersede 操作;handoff schema(contracts §4.6)逐字转写——本文件是 owner;
   移交提议话术要点(不写成台词,写成要点);开放问题汇入 digest。
6. **写边界执行面**(contracts §7):默认态、用户要求直改时的逐文件确认、三类无例外。

### register-discussion.md(转写 register-material.md)

1. 蒸馏红线(原料前言)以英文保留在文件头:register targets only / no personas /
   no example sentences / density not elimination / **safety layer: zero content**。
2. 通用基座一段(原料§一),由本 skill 自有,不依赖个人 skill。
3. 讨论专属五节(原料§二):呈现分歧 / 给推荐 / 不和稀泥的语言纪律 / 讨论的温度 /
   篇幅与节奏。全部保留,可润色,不得加示例句。
4. harness 插槽协议(原料§三)完整转写:只读、加载时机、冲突裁决、persona 提示一次
   规则、建议放什么不放什么。
5. 豁免区声明(工作产物电报体,contracts §8)。
6. 维护注记(原料§四)以英文保留。

## Conventions(红线)

- blueprint §8 全部适用(特别是红线 3/4/8/9)。
- meeting_material / handoff / sketch 三 schema 键名与 contracts 逐字一致(本 WP 是
  三者的 owner 转写者)。
- lens_note / digest / minutes / decision schema 归 WP3/WP2,引用不复制。
- register 文件不得出现好/坏示例句、persona 指令、安全层内容——验收最严的一条。

## Acceptance checklist

- [ ] 三铁则在汇总步骤逐条可执行,措辞未弱化
- [ ] meeting_material/handoff/sketch schema 与 contracts §4.3/4.6/4.7 逐字一致
- [ ] 决议冲突指认(D10)与正典冲突指认均有明确触发条件与动作
- [ ] sketch 草样"永不进 manuscript/"在委托与收口两处均出现
- [ ] register 文件零示例句、零 persona、零安全内容;蒸馏红线在文件头
- [ ] harness 插槽只读义务与冲突裁决规则完整
- [ ] 两文件行数达标;meta 层英文、content 层中文

## Out of scope

lens 章程与扇出(WP3)、digest/consent/minutes/decision schema 正文(WP2)、
SKILL.md(WP1)、sibling 改动(WP5)。
