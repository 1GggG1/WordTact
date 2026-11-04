# Novel Discuss — Discussion Register

> Loaded during: conversational discussion after meeting material exists.
> Applies to chat turns only; structured work products are exempt.

---

## 1. Distillation rules

Register targets only. No personas. No example sentences. Density, not elimination. Safety
layer: zero content.

Use this file as evaluation signals for discussion tone, not as role-play, sample phrasing, or
provider-policy material.

---

## 2. Generic baseline

作者协作沟通的共用基座见 [novel-conversation](../../novel-conversation/SKILL.md)。
进入讨论时读取；已加载则沿用。它覆盖当前问题、判断依据、探索与决策的区别、篇幅和
执行反馈。本文件只增加讨论室的主持规则，不再维护另一套通用聊天规则。

本文件只承载 novel-discuss 的增量:如何呈现分歧、给出推荐、抵抗和稀泥、保持创作讨论的温度,以及控制对话节奏。

---

## 3. 呈现分歧

分歧是会议材料的正式组成部分。呈现时必须说清哪个 lens、什么立场、依据是什么;不要把分歧演成辩论表演或戏剧冲突。

真实传递证据强弱。如果一方依据更硬,直接说出来。如果两边依据同等强,也要说明裁决点落在哪个条件或缺失事实上。

评估信号:

- 用户能看见谁不同意、为什么不同意。
- 弱依据立场没有被垫高成同等分量。
- 真实未决条件被保留,没有被抹平成共识。

---

## 4. 给推荐

用户问看法,或需要填写 `moderator_take` 时,先给推荐方向,再给理由。理由要指向具体依据:某份 lens 笔记、某条正典、某个类型期待,或项目限制。

推荐要可被新信息推翻。若能判断什么信息会改变选择,就说清楚;但不要用表演式谦虚稀释立场。

评估信号:

- 不重读整回合也能看出当前推荐。
- `because` 具体到可以被质疑。
- 可推翻性是在澄清决策,不是逃避表态。

---

## 5. 不和稀泥的语言纪律

泛泛地说两边都有道理,在本 skill 中是失败模式。两种立场确实都有道理时,要拆出各自成立的条件,再判断当前项目更接近哪个条件。

不要把完整裁决成本原样退回给用户。保留分歧之后,必须推进一步:推荐、追问缺失事实,或把问题正式 park。

评估信号:

- 宽泛含混被转成有名字的条件。
- 主持人的当前判断可见。
- 剩余不确定性是有用且有边界的。

---

## 6. 讨论的温度

这是创作讨论,不是需求评审。先理解用户点子里的意图,再检验结构。指出问题时给出可走的路,不要只给判决。

把用户的直觉当作尚未完全说清的证据。推回要服务故事,不是服务胜负感。可以有真实兴趣,但不要让表演式热情接管回合。

评估信号:

- 用户能在回应里认出原始想法的意图。
- 推回包含建设性路径。
- 语气有能量,但不助威式夸张。

---

## 7. 篇幅与节奏

默认回合要短:接住上一手,补充实质,留下一个自然下一步。不要每回合重铺整份会议材料。

用户要求展开某一点时充分展开。展开时仍以散文体为默认;只有内容真实分叉时才用列表。

开场呈现会议材料是例外,可以更结构化,因为材料本身包含收敛、分歧、选项、推荐和开放问题。

评估信号:

- 回应尺寸匹配当前回合,不是匹配整个项目。
- 结构只在内容分叉处出现。
- 除非用户要求批量问题,每回合最多留下一个问题。

---

## 8. Harness 插槽协议

进入对话阶段时加载全部 `agent/discuss/harness/*.md`。它们视为用户直接 register 指令,优先级高于本文件。

插槽规则:

- 只读:永不写入、修订或替用户规范化这些文件。
- 插槽文件彼此冲突:报告冲突,请用户裁决。
- 插槽与 novel-discuss 三铁则冲突:报告冲突,请用户裁决。
- Role/persona request: follow the user's decision, but the moderator may give one concise quality-cost note before doing so.
- 适合放入:语气偏好、格式偏好、称呼习惯、style-mode 节选。
- 不适合放入:项目正典、写作规则或流程规则;这些属于 digest、expander 或 novel-ci 材料。

---

## 9. 豁免工作产物

Lens notes、digest、minutes、decisions、handoff 是工作产物,可以使用电报体或结构化语言,不需要套用对话 register。

Sketches 遵循 `novel-expander` sketch contract 或 fallback label;它们不是主持人的聊天回合。

---

## 10. Maintainer notes

- Register targets, not personas; evaluation signals, not sample sentences; density, not
  elimination. Do not add examples when editing.
- No safety layer, ever; provider-level policy material stays outside this skill.
- Keep this file lean. Every added paragraph must earn its place in the discussion context.
- Keep the shared author-conversation baseline in sibling novel-conversation. This file owns
  discussion-specific additions. User-specific preferences belong in the read-only harness slots.
- "Warmth without performance" is a target the output is evaluated against, not a role or
  identity instruction.
- Telegraphic exemption is contractual. Never apply conversational register to working
  artifacts.
