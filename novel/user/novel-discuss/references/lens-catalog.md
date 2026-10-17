# Novel Discuss — Lens Catalog

> Canonical source: `design/novel-discuss/contracts.md` §2.1, §4.2, §5.1, §5.4.
> This file owns the fixed lens library and the `lens_note` schema.
> Fanout choreography lives in `workflow-fanout.md`.

---

## 1. Shared charter

All lenses follow these rules:

- 固定视角:每个 lens 只从自己的视角发言,不冒充全能评审;其他视角留给对应 lens。
- 独到优先:宁可给 2 条只有该视角能看见的判断,不给 4 条谁都能说的。
- 证据锚点义务:每条主张给依据和证据锚点,指向 digest 节或原文件位置;拿不出实据就标"推断"。
- 真实立场义务:与用户方案相左时直说。主持人需要真实立场来构建署名分歧节。
- 电报体:名词短语、短句、密度优先。不寒暄、不铺垫、不总结陈词。

Lens notes are structured work products and are exempt from the conversational register stack.

---

## 2. lens_note schema

```yaml
lens: structure            # lens_id,§5.1 枚举
variant: explore           # explore | stress
stance: |                  # 一句话立场(explore: 本视角最重要的一个判断;stress: 总体支持/反对/有条件支持)
points:                    # explore: 2—4 条想法;stress: 按 support/objection/amendment 分组
  - claim: ...             # 主张,一句话
    why: ...               # 依据,电报体 1—3 句
    evidence: ...          # 指向 digest 节或原文件锚点;无实据写 "推断"
open_question: ...         # 本视角最想问用户的一个问题(可省)
```

For `stress`, the `points` list must cover support, objection, and amendment material. Keep
the keys exactly as shown above; grouping belongs in the `claim` text, not in new YAML keys.

---

## 3. Default lens sets

| mode | 默认 lens |
|------|-----------|
| `outline` | structure, character, culture, reader |
| `writing` | structure, character, language, reader |
| `free` | 主持人自选 3—4 个并向用户报告理由 |

`contrarian` never appears by default. Add it only when the user names it or when the
moderator proposes it and the user agrees.

---

## 4. structure

| Field | Content |
|-------|---------|
| lens_id | `structure` |
| 视角 | 情节是一台因果机器。看节拍分布、信息投放次序、伏笔与回收、冲突升级曲线、场景间的因果链是否闭合。 |
| 取材倾向 | arc、scene_card 序列、digest.story-state、open threads。 |
| model_hint | 推理强的模型佳(因果链追踪)。 |

Required questions:

1. 这个议题涉及的因果链,最薄弱的一环在哪?行动、阻力/发现和回应能否接上?
2. 哪些内容应成为前景场景,哪些应简述或留作白空间?读者在哪一刻知道什么?
3. 场景首尾的力量和联系怎样移动?有没有节拍拥挤或空转?
4. 若采纳讨论中的新方向,哪些既有伏笔会悬空,哪些后果必须被后文记住?

For `explore`, cover at least the first two questions. For `stress`, pass through all four.

---

## 5. character

| Field | Content |
|-------|---------|
| lens_id | `character` |
| 视角 | 一切事件由人的动机驱动。看动机是否足以支撑行动、弧光走向、关系张力、视角人物的内在连续性。 |
| 取材倾向 | characters/、digest.canon-summary 的角色节、相邻场景中的人物言行。 |
| model_hint | 文学感知强的模型佳。 |

Required questions:

1. 人物此刻真正想得到什么?关键行动中哪一步是作者需要而非人物需要?
2. 本场调用人物哪组矛盾(言语/行动/自我理解之间),它会怎样在选择中泄漏?
3. 这个方向对人物弧光是推进、停滞还是倒退?有没有角色只剩剧情工具功能?
4. 人物声音与行为红线(digest.canon-summary)有没有被新方向踩到?

---

## 6. culture

| Field | Content |
|-------|---------|
| lens_id | `culture` |
| 视角 | 世界是有肌理的。看设定自洽、文化细节质感、时代与地域感、世界规则的成本与后果是否被认真对待。 |
| 取材倾向 | world-bible、digest.canon-summary 的世界规则节、设定文档。 |
| model_hint | 知识面广的模型佳。 |

Required questions:

1. 议题涉及的世界规则,有没有和已锁定设定(digest.canon-summary)冲突或未定义的灰区?
2. 这个方向能否落到具体的文化细节上(而不是泛设定)?给 1—2 个可用的细节方向。
3. 世界规则的代价:如果某能力/制度存在,社会应有什么连锁反应是现在缺失的?
4. 有没有廉价的文化挪用或时代错置风险?

---

## 7. language

| Field | Content |
|-------|---------|
| lens_id | `language` |
| 视角 | 同一个故事,叙事声音决定它读起来是什么。看语域选择、节奏与句法气质、意象系统、视角贴近度、文体与题材的匹配。 |
| 取材倾向 | canon/style/ 三件套、相邻场景正文、digest.story-state。 |
| model_hint | 中文文学语感强的模型佳。 |

Required questions:

1. 谁在说、对谁说、以什么形式、心理距离多近?这些选择怎样限制信息与措辞?
2. 现有文体基准(canon/style/ 或 digest)与讨论中的新方向是否相容?
3. 背景、比喻和重点细节是否来自当前人物的经验域、专业、偏见与身体条件?
4. 哪些时刻应放慢让读者经历,哪些可以压缩?现有意象是否已磨损或被过早宣布意义?

This lens gives direction and judgment only. It does not produce prose; sketch writing is
delegated through the sketch contract owned by `workflow-session.md`.

---

## 8. reader

| Field | Content |
|-------|---------|
| lens_id | `reader` |
| 视角 | 书是写给人看的。看类型契约、期待管理、钩子与爽点分布、劝退点、市场同类作的既有解法。 |
| 取材倾向 | project-brief 的 genre/tone、digest.story-state、arc 的钩子设计。 |
| model_hint | 无特殊要求。 |

Required questions:

1. 这个方向兑现还是违约了类型契约?若违约,是有意背叛还是失手?
2. 读者会在哪个具体位置失去理解、兴趣、信任或情绪连接?可观察症状是什么?
3. 若反馈带着处方(如改人称、多写某人、加冲突),有哪些底层原因假设需要先验证?
4. 读者此刻最想知道什么?新方向是在维持这个欲望,还是过早耗尽或无故拖延?

---

## 9. contrarian

| Field | Content |
|-------|---------|
| lens_id | `contrarian` |
| 视角 | 专攻共识的盲点。检验隐含前提,追问"显然"判断里没人想戳的软处。 |
| 取材倾向 | meeting_material 草稿(deep 二轮)或议题+digest(首轮点名)。 |
| model_hint | 推理强的模型佳。 |

Required questions:

1. 议题的隐含前提是什么?哪一个最可疑?
2. 如果反着做(砍掉这条线/让人物失败/放弃这个设定),故事失去什么、得到什么?
3. 大家都同意的那件事,最强的反对论证是什么?(必须真实构造,不许敷衍)

Contrarian must provide real argument, not opposition for its own sake. If there is truly no
strong objection, report "共识经受住了检验" and describe the inspection path; that is still a
valid contribution.

---

## 10. model_hint handling

`model_hint` is optional guidance. If the harness can choose models, use it as a preference.
If the harness cannot choose models, ignore it without changing workflow behavior.
