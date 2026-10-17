# Novel Discuss — Workflow: Session

> Loaded during: topic clarification, synthesis, discussion, sketch delegation, and close.
> Depends on: `conventions.md`, `state-layout.md`, `workflow-fanout.md`, `register-discussion.md`.
> Owner of: `meeting_material`, `handoff`, and `sketch` schemas.

---

## 1. Topic clarification

Before fanout or direct discussion, reduce the user's request to:

- one-sentence `topic`
- `mode`: `outline`, `writing`, or `free`
- `variant`: `explore` or `stress`
- `intensity`: `light`, `standard`, or `deep`
- lens set, when user override or free-mode selection applies

Declare the three axes in the opening. If `digest.open-questions` is non-empty, ask once
whether the user wants to pick up a parked question from a prior session. If the user declines,
continue with the new topic.

For `stress`, preserve the user's proposal text as the object under test. For `free`, report
why the selected 3-4 lenses fit the topic.

---

## 2. Fanout boundary

For `standard` and `deep`, call `workflow-fanout.md` after clarification and digest readiness.
For `light`, skip fanout and move directly to discussion with the moderator's own reading of
digest context.

Named lens consultation during the conversation is delegated to `workflow-fanout.md` §8. Do
not copy its input package or `lens_note` schema here.

---

## 3. meeting_material schema

```yaml
topic: ...
mode: outline | writing | free
variant: explore | stress
intensity: light | standard | deep
lenses: [structure, character, ...]
convergence:               # 收敛点:≥2 个 lens 独立同向的判断
  - point: ...
    backed_by: [structure, reader]
disagreements:             # 署名分歧节。standard/deep 档下为空 = 汇总不合格(§6)
  - question: ...          # 分歧聚焦为一个问题
    positions:
      - lens: structure
        position: ...
      - lens: language
        position: ...
options:                   # 可选方案 2—3 个(explore),或 方案修正稿(stress)
  - label: ...
    gist: ...
    tradeoff: ...
moderator_take:            # 主持人推荐 + 理由,必填(§6)
  pick: ...
  because: ...
open_questions: [...]
canon_flags: [...]         # 与 canon-summary 冲突的点子预警(可空)
```

Present meeting material to the user in natural language. Archive the YAML in the session
minutes container defined by `state-layout.md`.

---

## 4. Synthesis rules

Build meeting material from validated fanout notes.

Three iron rules applied at synthesis:

1. **独立首轮**: only use notes produced under the first-round isolation rule. If fallback
   fanout reported contamination, exclude the affected note rather than laundering it.
2. **署名分歧强制**: in `standard`/`deep`, empty `disagreements` is invalid. Mine lens
   stance differences, direct stance conflicts, evidence-strength gaps, and different
   conditions attached to similar conclusions. If there is still no disagreement, state that
   the lenses reached the same conclusion through different paths and list those paths.
   `light` is exempt.
3. **主持人立场强制**: fill `moderator_take.pick` and `moderator_take.because`. The moderator
   must recommend a direction with reasons; a neutral transcript is invalid.

For `explore`, produce 2-3 options unless the material clearly supports only one viable path.
For `stress`, convert support, objection, and amendment material into a revised proposal or
explicit tradeoff set.

---

## 5. Discussion hosting

After presenting meeting material, the moderator carries the conversation alone. Use the
register stack from `register-discussion.md` and `conventions.md` §6.

During discussion:

- Let the user steer among options, objections, and open questions.
- When a point needs one lens's judgment, run named consultation through `workflow-fanout.md`
  §8, validate the returned note there, then fold it into the live discussion.
- Do not rerun full fanout unless the user asks for a new round or the topic materially
  changes.
- Track turns that change the decision direction for later `key-turns`.

### Canon conflict pointing

Trigger: a proposed idea conflicts with `digest.md` `## canon-summary`.

Action: name the conflicting canon point in one sentence, explain the relevant impact, and
route any canon change through handoff instead of direct write. Do not edit lockfile, bible,
characters, or manuscript.

### Decision conflict pointing

Trigger: a new direction conflicts with an active entry in `decisions.md`.

Action: name the decision id, restate its `because`, and ask whether the old decision should
be superseded. If yes, append a new decision and perform only the supersede update allowed by
`state-layout.md` §6. If no, keep the active decision and record the rejected branch in
minutes if it mattered.

---

## 6. sketch delegation

Use sketch delegation only when the user wants to feel how an option reads in prose. Sketches
are exploratory discussion material, not draft manuscript.

```yaml
caller: novel-discuss
budget: sketch             # expander Invocation contract 的档位(§9.2)
variants: 2                # 2—3
length: ≤500字/变体
input: ...                 # 节拍/开头意图,自由文本;可附 digest 相关节
constraints: ...           # 视角/文体约束,来自讨论现场
output_dir: agent/discuss/sessions/<session_id>/sketches/
```

Delegate to `novel-expander` with this parameter shape. If `novel-expander` is unavailable,
fallback: the moderator writes one rough variant, labels it "未过 expander 语言层,仅供讨论",
and stores it under the same sketches directory.

Sketch samples never enter `manuscript/`, never leave the session `sketches/` directory as a
formal draft, and never become handoff content except as a discussion reference.

---

## 7. Closeout

Close when the user has a usable decision, decides to park the topic, or asks to stop.

Closeout actions:

1. Write `minutes.md` using the container schema in `state-layout.md` §5; do not duplicate it
   here.
2. Append decision entries using `state-layout.md` §6. If superseding, update only the old
   `status` and `superseded_by`.
3. Copy the handoff YAML below into the minutes `handoff` section when planning handoff is
   relevant; otherwise write `none`.
4. Add parked questions to `digest.md` `## open-questions`.
5. Keep sketch samples under `agent/discuss/sessions/<session_id>/sketches/`; they never enter
   `manuscript/`.

Offer handoff by stating the handoff exists, what planning can consume from it, and asking
whether the user wants to start a novel-ci planning pass with the minutes path as input.

---

## 8. handoff schema

```yaml
from: novel-discuss
session: <session_id>
decisions: [D-20260708-01, ...]
summary: ...               # 3—5 句:定了什么、为什么
impact:                    # 影响范围,novel-ci 侧的落点
  - target: chapter-arc | scene-card | character | world-rule | style
    what: ...
suggested_actions:         # 建议动作,planning 可直接消化
  - ...
unresolved: [...]          # 明知未决、留给 planning 的
```

Handoff is one-way. Novel-discuss prepares the brief; a later novel-ci planning session
consumes the minutes file path when the user agrees.

---

## 9. Write-boundary enforcement

Default write target is `agent/discuss/` after consent.

If the user asks to modify project files outside `agent/discuss/`, confirm each target file
before writing. This exception never applies to `canon/lockfile.yaml`, `canon/*-bible*`,
`characters/`, or `manuscript/`.

Those protected targets have no exception. Needed canon changes go to handoff for novel-ci
Gate D. Needed manuscript changes become planning or expansion work outside novel-discuss.
