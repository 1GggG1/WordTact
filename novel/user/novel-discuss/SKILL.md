---
name: novel-discuss
description: "Multi-perspective novel discussion room for brainstorming, stress-testing ideas, preserving disagreements, and producing decisions/handoff briefs without writing prose or canon. Trigger on Chinese phrases including 讨论大纲、聊聊怎么写、头脑风暴、帮我想想、设定怎么展开、开头怎么写好、纠结走向、讨论人物弧、这个方案靠谱吗、stress test 一下, or English equivalents like 'brainstorm', 'discuss the outline', 'talk through how to write this', 'stress test my plan'. Routing: project-state production, scene cards, drafts, review, patching, regression, or lockfile work routes to novel-ci; novel-discuss handoff minutes are valid planning input. Narrative prose from outline/notes routes to novel-expander. Finished prose diagnosis/minimal edits routes to novel-auditor. Discussion/how-to-write requests routed here from novel-ci or novel-expander are accepted."
---

# Novel Discuss

## Core principles

1. 讨论室定位。Novel-discuss produces consensus, disagreement, decisions, minutes, and
   handoff briefs. It does not produce manuscript prose, does not revise canon, and does not
   replace novel-ci or novel-expander.
2. **独立首轮**:首轮笔记生成期间 lens 互不可见。首轮输入包不得包含其他 lens 的笔记或主持人的预判。串行降级时也一样。
3. **署名分歧强制**:`standard`/`deep` 档的 `meeting_material.disagreements` 为空 = 汇总不合格。主持人必须回去挖 lens 立场差异、stance 冲突、evidence 强度差。确无分歧时,必须写明"各 lens 从不同路径到达同一结论"并列出各自路径;路径差异本身就是信息。`light` 档豁免。
4. **主持人立场强制**:`meeting_material.moderator_take` 必填。主持人是带立场的与会者;只罗列各方观点不给推荐 = 汇总不合格。对话中用户问"你怎么看"时同样适用。
5. Consent comes before durable memory. If `<project>/agent/discuss/` is absent, ask once
   before creating it. If the user refuses, run stateless and output minutes/decisions in chat.
6. Default write target is `agent/discuss/` after consent. Other project files are zero-write
   unless the user explicitly asks and confirms each target file.
7. `canon/lockfile.yaml`, `canon/*-bible*`, `characters/`, and `manuscript/` have no write
   exception. Canon changes go to novel-ci handoff; manuscript work goes to novel-ci or
   novel-expander.
8. Sketches are exploratory discussion samples only. They stay under
   `agent/discuss/sessions/<session_id>/sketches/` and never enter `manuscript/`.

---

## Workflow overview

```text
Route(mode × variant × intensity) → memory check / consent
→ digest freshness or stateless context assembly
→ topic clarification + open-question pickup
→ [standard/deep: isolated lens fanout → validated notes → synthesis]
→ meeting material with convergence / signed disagreement / options / moderator take
→ conversational discussion with register stack
   · named lens consultation when needed
   · sketch delegation to novel-expander when prose feel is needed
   · canon conflict pointing from digest.canon-summary
   · active decision conflict pointing from decisions.md
→ closeout: minutes + decisions + optional handoff + parked questions
```

`light` skips the bracketed fanout section and uses moderator-led discussion with digest
context.

---

## Routing axes quick reference

Declare all three axes at the start of the session.

| Axis | Values | Use |
|------|--------|-----|
| `mode` | `outline` / `writing` / `free` | Sets default lens mix and context emphasis. |
| `variant` | `explore` / `stress` | `explore` generates independent ideas; `stress` tests a user proposal. |
| `intensity` | `light` / `standard` / `deep` | `light` skips fanout; `standard` runs one lens round; `deep` uses all eligible lenses plus the second round; `contrarian` still only appears when named or approved. |

Default lens sets:

| mode | default lenses |
|------|----------------|
| `outline` | structure, character, culture, reader |
| `writing` | structure, character, language, reader |
| `free` | moderator selects 3-4 lenses and reports why |

`contrarian` never appears by default. Add it only when the user names it or approves the
moderator's suggestion.

User overrides always win for mode, variant, intensity, or lens set. Acknowledge the override
in the opening declaration.

---

## Module loading route

Load references lazily. Keep at most three reference files in context at any time.

| Stage | Files loaded |
|-------|--------------|
| Startup, consent, memory check | `references/conventions.md` + `references/state-layout.md` |
| Fanout | `references/workflow-fanout.md` + `references/lens-catalog.md` |
| Discussion | `references/workflow-session.md` + `references/register-discussion.md` |
| Closeout and handoff | `references/workflow-session.md` + `references/state-layout.md` |

When a named lens consultation happens during discussion, temporarily load
`workflow-fanout.md` + `lens-catalog.md`, run the single-lens consultation, then return to the
discussion pair.

---

## Reference files

| File | When to load |
|------|--------------|
| `references/conventions.md` | Startup and anytime terminology, three axes, anti-mush rules, write boundaries, or register stack order is needed. |
| `references/state-layout.md` | Consent, `agent/discuss/` layout, digest freshness, minutes container, decisions ledger, naming, and write modes. |
| `references/lens-catalog.md` | Choosing lenses, reading lens charters, validating `lens_id`, or using the `lens_note` schema. |
| `references/workflow-fanout.md` | Running standard/deep fanout, serial fallback, deep second round, note validation, or named consultation. |
| `references/workflow-session.md` | Topic clarification, synthesis, meeting material, discussion hosting, canon/decision conflict pointing, sketch delegation, closeout, and handoff. |
| `references/register-discussion.md` | Conversational discussion after meeting material exists, including harness slots and fallback register. |

---

## Sibling boundaries

- `novel-ci`: production pipeline. Use it for scene specs, draft generation through the
  pipeline, review, patch, regression, state update, and lockfile maintenance. Novel-discuss
  handoff minutes are valid planning input.
- `novel-expander`: prose expansion. Use it when the user wants narrative text generated.
  Novel-discuss may delegate `budget: sketch` samples and has a moderator fallback in
  `workflow-session.md`.
- `novel-auditor`: finished-prose diagnosis and minimal-modification suggestions. There is no
  direct novel-discuss interface.

---

## Maintainer notes

**Language allocation is intentional.** Meta-layer content such as workflow structure,
routing, loading rules, and this maintainer section stays in English. Content-layer material
for Chinese creative-writing discussion stays in Chinese. Do not translate one layer into the
other for neatness.

**Schema single ownership.** Consumer files reference owner file + section; they do not copy
schema bodies.

| Schema | Owner |
|--------|-------|
| `digest.md`, `session_minutes`, `decision` | `state-layout.md` |
| `lens_note` | `lens-catalog.md` |
| `meeting_material`, `handoff`, `sketch` | `workflow-session.md` |

**Three iron rules are load-bearing.** Do not soften independent first round, signed
disagreement, or moderator-take requirements. Signed disagreement is not optional in
`standard`/`deep`; moderator recommendation is not optional.

**Sibling delegation stays shallow.** Do not inline novel-ci, novel-expander, or
novel-auditor rules. The generic discussion baseline is owned locally by
`register-discussion.md`; project or user preferences stay in read-only harness slots.

**Safety layer: zero content.** Provider-level policy material stays outside this skill. Do
not add provider-policy material here.

**Unpacked use only.** Keep this skill zero-install, zero-script, zero-external-dependency.
All paths are relative to the user's project root. Do not bind instructions to a harness
container path.

## Production handoff context

Use sibling `../novel-ci/references/project-context.md` when a discussion depends on existing
manuscript, author decisions, voices or publication scope. Keep independent first-round views,
real disagreement and a clear recommendation. Preserve production decisions in the existing
minutes/handoff with source, applicable chapters/roles and superseded decisions; do not turn a
one-line retention into a global exemption or write a reader index from an exploratory sketch.
