# Novel Discuss — Workflow: Fanout

> Loaded during: standard/deep fanout, named lens consultation.
> Depends on: `conventions.md` §2-§3, `state-layout.md` §3-§4.
> Uses: `lens-catalog.md` for lens charters and `lens_note` schema.

---

## 1. Preconditions

Run fanout only when:

1. `intensity` is `standard` or `deep`.
2. The topic has been clarified enough to state in one sentence.
3. `mode`, `variant`, and lens set are declared.
4. `digest.md` is available, or stateless mode has assembled an in-memory digest equivalent.
5. Targeted source files, if any, have been selected per lens, with no more than three files
   per lens input package.

`light` intensity skips fanout. The moderator handles the discussion directly with digest
context and still observes write boundaries and register rules.

---

## 2. Single-lens input package

Each lens receives only:

1. 议题陈述 + variant + mode(以及 stress 变体下的用户方案原文)
2. digest 全文(stateless 模式为现场汇编等价物)
3. ≤3 个定向原文件(主持人按 lens 取材倾向挑选;可为零)
4. 本 lens 章程(lens-catalog 对应节)
5. lens_note 格式(`lens-catalog.md` §2)

**独立性铁则:任何其他 lens 的笔记、主持人的预判,不得进入输入包。** This applies to
the entire first round.

---

## 3. Variant prompt skeletons

Use these as assembly skeletons for child-agent calls or serial fallback notes. Replace only
the bracketed placeholders with session-local material.

### 3.1 explore

```text
Task: produce one independent lens_note for novel-discuss.

Lens: [lens_id]
Mode: [outline | writing | free]
Variant: explore
Topic: [one-sentence topic]

Context:
- Digest: [digest or stateless equivalent]
- Targeted source files: [0-3 items, selected for this lens]
- Lens charter: [the matching lens-catalog section]
- Required output format: lens-catalog.md §2 lens_note schema

Requirements:
- Work only from this lens.
- Propose 2-4 independent idea elements from this lens.
- Give evidence for every claim, or mark it as "推断".
- Return telegraphic notes only.
```

### 3.2 stress

```text
Task: produce one independent lens_note for novel-discuss.

Lens: [lens_id]
Mode: [outline | writing | free]
Variant: stress
Topic: [one-sentence topic]
User proposal under test: [proposal text]

Context:
- Digest: [digest or stateless equivalent]
- Targeted source files: [0-3 items, selected for this lens]
- Lens charter: [the matching lens-catalog section]
- Required output format: lens-catalog.md §2 lens_note schema

Requirements:
- Work only from this lens.
- Cover support, objection, and amendment material in `points`.
- State the overall stance in `stance`.
- Give evidence for every claim, or mark it as "推断".
- Return telegraphic notes only.
```

These skeletons must stay free of persona instructions, example sentences, project-specific
content, and provider-layer policy material.

---

## 4. Execution

If the harness supports parallel child agents, dispatch all first-round lens calls in parallel.
Keep each input package isolated.

If parallel child agents are unavailable, use serial fallback:

1. Prepare the input package for one lens.
2. Produce that lens note.
3. Clear the working context for the next lens as far as the environment allows.
4. Repeat for the next lens without passing any previous lens note forward.

**独立性铁则 applies in fallback too:**逐 lens 自问自答,前一笔记不进后一 lens 的工作上下文;
实现手段由 harness 能力决定,原则不变。

---

## 5. Note validation

For each returned lens_note, check:

- `lens` is one of `structure`, `character`, `culture`, `language`, `reader`, `contrarian`.
- `variant` matches the session variant.
- `stance` is present and specific.
- `points` is present.
- Every point has `claim`, `why`, and `evidence`.
- Each `evidence` points to a digest section, source-file anchor, or exactly says "推断".
- `stress` notes cover support, objection, and amendment material.

If a note fails validation, return it once to the same lens with the missing fields named.
If it fails again, drop it and carry the failure forward to the next workflow as a discarded
note with reason. Do not invent a replacement note.

---

## 6. Anti-mush carry-forward

Fanout directly enforces **独立首轮**:首轮笔记生成期间 lens 互不可见, and fallback must not
pass earlier notes into later lens contexts.

Fanout must also preserve the raw material needed for **署名分歧强制**. Do not flatten notes
into a consensus before session synthesis; carry forward stance differences, stance conflicts,
and evidence-strength gaps so `workflow-session.md` can build a signed disagreement section.

Fanout must not pre-decide that the moderator is only a recorder. Preserve enough stance and
evidence for **主持人立场强制**: `workflow-session.md` must be able to fill a real
`moderator_take` with a recommendation and reasons.

---

## 7. deep second round

For `deep`, after first-round notes are validated, prepare a first-round synthesis draft and
send it back to each active lens.

Second-round limit: each lens may output exactly one item: rebut one convergence point,
rebut one disagreement position, or strengthen its own first-round claim. If a lens outputs
more than one item, use only the first item.

After this second round, pass the full set of first-round notes plus accepted second-round
items to `workflow-session.md` for final meeting material.

---

## 8. Named consultation

During discussion, the user or moderator may name a lens for one more consultation. This is a
single-lens call, never a full re-fanout by default.

Input package = §2 plus a concise summary of the current dispute. At this stage, relevant
disagreement positions may be included; the first-round independence rule no longer applies.

Return format remains `lens-catalog.md` §2 `lens_note`. Validate it with §5 before using it.

---

## 9. Handoff point

This workflow stops when all required notes are collected and validated, or when invalid
notes have been dropped with reasons. Synthesis, user-facing meeting material, decisions,
handoff, and session close are owned by `workflow-session.md`.
