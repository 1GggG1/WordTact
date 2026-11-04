# Novel CI — Workflow: Draft

> Loaded during: draft generation phase.
> Depends on: `conventions.md` §7 (shared language verification).
> Delegates narrative-craft and language generation to: `novel-expander` (contracts §10.1).
> Consumes: `scene_card` (owner: `workflow-planning.md`).

---

## 1. Input & precondition

- `scene_card` with status `card_confirmed` (Gate A passed). No confirmed card = do not enter this workflow.
- `canon_lockfile` relevant slice: `current_time`, `current_location`, `character_states` for appearing characters, `confirmed_events` relevant to this scene, `watchlist` items relevant to this scene.
- `character_profile` files for all characters appearing in this scene.
- `project_brief.structural_preference` for target scene length.

---

## 2. Structural rules (ten rules)

本阶段管**写什么/禁什么**。如何把规格落实为场景、简述、行动、对话、POV、背景与细节，
以及句段表面怎么写，委托给 expander。

1. **严格遵守 scene_card。** `target`、`required_beats`、`conflict`、`turn`、`consequence`、`exit_state` 必须全部在正文中可辨识。不增加 card 未规定的子情节或人物弧线。
2. **不新增未授权设定。** 所有世界观事实、角色背景、组织关系必须来自 lockfile/bible/profile。draft 中出现的任何新设定必须在 state_update 后经确认才能进入 canon。
3. **不改变 lockfile 已确认事实。** `confirmed_events`、`character_states`、`world_state` 中的条目是只读约束——可以在此基础上发展，不能覆盖或忽略。
4. **不让角色获得未授权信息。** 每个角色的话语、内心活动、判断必须与其 `information_access` 一致。POV 角色也不例外：POV 只是视角，不是全知通行证。`pov.information_limit` 是硬边界。
5. **不替角色说作者观点。** 叙述中不得出现"他意识到自己必须放下执念"类作者式总结。角色的认知必须来自场景事件推动，不由叙述语言代劳。
6. **不用说明书方式交代设定。** 世界观、背景、角色关系应由当前叙事目的决定呈现方式。行动/对话/环境/反应适合承载关键变化；已知惯例和次要背景可以简述。禁止脱离人物与场景需要的百科式插入。
7. **关键变化要让读者有据可推。** 发现、决定、拒绝、策略变化和后果应在其发生处获得足够前景篇幅；惯例、重复和连接可以概述或省略。“展现”不是绝对禁令，判断标准是概述是否吞掉了本场必须体验的变化。
8. **落实本场约定的情绪功能。** `turn.emotional_shift` 适用时让变化有可推断的触发和承载；安静、克制或持续同一情绪有明确功能时，不另造转折。
9. **结尾落在具体状态变化而非空泛悬念。** 最后一个段落应当落在 exit_state 的具体变化上——某人离开了、某物被拿走了、某句话被听到了、某种关系被改变了。不要以"而他不知道接下来会发生什么"类句式结尾。
10. **draft 阶段不自我解释、不自评。** 输出纯正文。写完不回头看、不润色、不在文末加注释。正文质量由 review 阶段验证——不要在生成阶段做审查。

---

## 3. Narrative-craft and language delegation

Narrative presentation and surface language are delegated to `novel-expander`.

Read the shared [evidence boundaries](project-context.md#evidence-boundaries-in-writing-and-review)
when turning the card into prose, including when using the fallback below. A target outcome is
not an event already witnessed or knowledge already acquired. Keep narrator and character
access distinct. This drafting constraint does not add a self-review phase to the CI pipeline.

Priority chain:

```
current applicable author decisions (resolve scope and supersession in project-context.md)
  > scene_card.prose_constraints / scene_card.forbidden
  > project agent/context and canon/style/
  > novel-expander default style parameters
```

- Load relevant modules from expander's `references/narrative-craft.md`, then load
  `references/anti-ai-patterns.md` for the surface ruleset.
- If the scene includes character speech, also load
  [novel-dialogue](../../novel-dialogue/SKILL.md), including in the fallback path. Apply its
  drafting guidance now and leave its verification questions to the scheduled review.
- When expander invocation is unavailable, read its shared references directly. If unavailable too, report the missing verification; conventions.md §7 does not substitute a shortened rule copy.
- This file maps card fields but does NOT replicate expander craft or language rule entries (D3/D11).

---

## 4. required_beats usage discipline

Beats are **waypoints**, not section templates.

- **禁止** 一 beat 一段的机械展开。Beats 指定的是必经情节节点，不是段落分界线。
- Beats 之间的连接材料由 `conflict` 和 POV 视角驱动——冲突如何从一个 beat 推向另一个 beat？
- 如果一个 beat 和另一个 beat 之间只需要一句话过渡，那就一句话。不为了"看起来完整"而填充。

---

## 5. Length & output

- Target word count: from `scene_card` (if specified) or `project_brief.structural_preference.scene_length`.
- Output path: `manuscript/ch<NNN>/<NNN>-<SS>.draft.md`.
- Output format: **pure prose body**. No markdown headers, no title, no "Scene N" label, no commentary, no self-evaluation.

---

## 6. After draft: go straight to review

Draft 落盘后：不要润色、不要自读回改、不要自己先检查一遍。立即进入 `workflow-review`。

**完成即测。** 在生成和测试之间插入"我先看看"环节会导致未测先修——修的内容可能不是测试会发现的问题，浪费修改预算。

---

## 7. Scene card field mapping for expander

When the language layer (expander) is loaded, map `scene_card` fields to expander's internal inputs:

| scene_card field | Maps to expander's | Notes |
|-----------------|-------------------|-------|
| `entry_state.character_states[].goal` + `target` | Step 1: what the POV character wants | Do not invent a second desire field |
| `change_chain` | Craft: action → resistance/revelation → response | Includes deliberate inaction when it has a cost |
| `dialogue_dynamics` | Craft: language goal, refusal, strategy shift | Conditional; dialogue-led scenes only |
| `time_handling` | Craft: foreground / compress / omit | Preserve discoveries and decisions in foreground |
| `pov.*` | Craft: narrator, narratee, form, distance, information, attention | All fields must remain mutually consistent |
| `turn.embodied_by` | Craft: visible turn | Realize through action, object, or consequence |
| `dynamics` | Craft: power / connection movement | May be not applicable when exit_state carries another change |
| `conflict` + `stakes` | Step 1: resistance and cost | Quiet scenes may use refusal, discovery, or costly inaction |
| `entry_state` + `exit_state` | Step 1: before/after state | Spatial grounding and changed situation |
| `prose_constraints` | Step 2: style parameters | Overrides expander defaults |
| `forbidden` | Step 3: hard boundaries | Must never appear in output |

This mapping is provided so the expander does not need to re-derive what the card already specifies. The expander's Step 1 internal questions are answered by the card.

---

## 8. Common structural failures to preempt

Before writing, scan for these predictable failure patterns. Each maps to a review module that would catch it:

| Failure pattern | Caught by | Prevention |
|----------------|-----------|------------|
| POV character knows things they shouldn't | information_tests | Re-read `pov.information_limit` before every paragraph from POV |
| A change promised by the card is not realized | emotion_curve_tests / consequence_tests | When a turn is planned, identify its trigger and `turn.embodied_by`; otherwise realize the agreed experience or stable emotional function |
| Planned resistance cannot be understood from the prose | conflict_tests | Make the relevant resistance legible through the chosen POV; internal conflict need not be converted into an external dispute |
| Exposition dump disguised as dialogue | scene_function_tests | Count: how many lines of dialogue exist purely to convey information to the reader? |
| Known information is repeated without a new function | information_tests / narrative_delivery_tests | Check B's knowledge and the reader's prior disclosures; preserve useful reactions, reminders, challenges and callbacks |
| A planned consequence is not legible | consequence_tests | Choose scene, summary or implication according to its importance and POV; not every consequence needs a separate visible event |
| Key discovery compressed into a report | narrative_delivery_tests | Keep the discovery and response in `time_handling.foreground` |
| A dialogue strategy change required by the card is absent | conflict_tests | Follow applicable `dialogue_dynamics`; useful transmission, stable relationships or a new understanding do not require invented refusal |

These are writing-phase guardrails, not review-phase tests. Use them during drafting to reduce review failures.

---

## 9. Draft self-restraint checklist

Before writing the first sentence, confirm you can answer YES to all:

- [ ] I have read the `scene_card` in full and can locate every `required_beat` in my mental outline.
- [ ] I have checked `forbidden` and know the specific things that must NOT appear.
- [ ] I have verified `pov.information_limit` against the POV character's `information_access`.
- [ ] I have re-read the last scene's `exit_state` from the lockfile to ensure continuity of character physical state, location, and resources.
- [ ] If `emotional_shift` is planned, I know its trigger and placement; otherwise I can describe the agreed stable emotional or experiential function.
- [ ] I can trace the applicable `change_chain` and planned `turn.embodied_by`, or explain how this scene fulfills its agreed function without inventing a turn.
- [ ] I know which material is foregrounded, compressed, or omitted.
- [ ] If the scene is dialogue-led or uses a special form, I have read the corresponding conditional fields.

If any answer is NO, stop and read the relevant source before writing. This is not a gate — it's a pre-flight check to reduce avoidable review failures.

## Shared project and reader context

Before planning or drafting, read project-context.md and retrieve relevant disclosures through
reader-index.md using only the prefix before the target. Verify source anchors when relying on
an indexed summary. Load project language habits before generation; the later review performs
mandatory scans and semantic judgments. Existing author decisions and local exceptions retain
their scope; no second canon or new mandatory project-state migration is required.
