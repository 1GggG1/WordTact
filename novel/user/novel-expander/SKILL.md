---
name: novel-expander
description: "Expand rough outlines, character/world notes, and fragments into narrative prose. Trigger on '扩写', '写成小说', '展开章节', '写正文', '把大纲写成文', '帮我写小说', '续写', '扩充', '根据这个大纲写一段', or English equivalents like 'expand this outline', 'write this scene out', 'turn this into a chapter'. Also triggers when synopsis, character sheet, or worldbuilding notes ask for narrative text. Handles input-outline to output-narrative. Finished prose audit, AI-tell checks, or minimal edits route to novel-auditor. Discussion of how to write rather than prose output routes to novel-discuss. Goal: turn story intent into readable narrative action while avoiding AI-generated surface patterns. In novel-ci, input is scene_card; scene_card and canon constraints take priority; novel-ci owns structure gates; this handles narrative craft and language generation."
---

# Novel Expander

Turn story intent into readable narrative action, discovery, response and character experience.
Do not optimize for imitating human imperfection. Preserve the project's voice and factual bounds
while controlling language habits, repetition and punctuation.

## Preparation

Read `../novel-ci/references/project-context.md`. Load effective author decisions, relevant prior
prose and reader disclosure records, plus the project language profile. Use established project
style without asking again. If there is no style basis, read `references/style-guide.md` for defaults.
Finished-prose diagnosis or authorized minimal edits route to novel-auditor; outline-to-prose stays
here. Resolve ambiguous wording from the supplied material and prior authorization before asking.

For style-consistency requests or applicable author rules/approved samples, read sibling auditor's
[style consistency](../novel-auditor/references/style-consistency.md). Carry a short, source-bound
brief for this narrator, character, form and scene. Explicit rules and inferred sample observations
stay distinct; stable terminology and purposeful voice differences are both part of consistency.

Apply the shared [evidence boundaries](../novel-ci/references/project-context.md#evidence-boundaries-in-writing-and-review):
outline outcomes guide construction, but do not give characters advance knowledge or establish
unwritten decisions. Keep narrator access, character knowledge and reader information distinct.

If an applicable language reference is already established or explicitly requested, read sibling
auditor's `references/style-reference.md`. Use a short source-backed wording brief, pin its reference
version and keep author-provided narrative choices fixed. Do not fill word quotas or rebuild the
reference from the draft. Missing reference data does not invent a new drafting prerequisite.

Answer: who perceives this, what matters to them now, what resistance/discovery changes their
response, and what experience or changed state the scene should leave. Do not fabricate conflict
to fill a form. A consequential missing creative choice is the reason to ask one focused question.

## Drafting

Read `references/anti-ai-patterns.md` before every expansion. It is the single canonical source for
language habits and the punctuation set. Read relevant modules of `references/narrative-craft.md`
for action chains, foreground vs summary, dialogue strategy, POV, detail and object function.

Scene-card constraints and effective project decisions govern default style. With no supplied
style, use limited third person and a readable web-novel register; do not impose this on existing
voices. A formal officer and an informal narrator need not sound alike.

Check reader disclosures before explaining rules, numbers or a plan again. Preserve genuine new
conditions, changed listeners' reactions and useful callbacks. Do not always replace repeat
explanation with a synonym; sometimes its narrative function is what repeats.

## Standalone two-pass self-check

1. Review narrative presentation: action/response, comprehension, POV, useful detail and voice.
   Check consequential knowledge/state changes against the prose and supported inference, not
   just the intended plot. Preserve intelligible time shifts, omniscient narration and purposeful
   omission; do not add explanations merely because the author knows more than the reader.
   Check applicable style rules against their pinned sources and comparable scene conditions.
   For reading-load obstacles, use sibling auditor's
   [Chinese reading load](../novel-auditor/references/reading-load-zh.md); do not smooth all voices
   into one register or split clear long sentences merely to shorten them.
2. Run canonical language checks: actual counts, LLM semantic classification, density resolutions,
   punctuation, and replacement-word recurrence using sibling auditor's `references/language-tools.md`.

When reference comparison is enabled, include its same-version evidence in the language pass.
Statistical departure alone is not a failed draft and does not authorize narrative redesign.

If revising the generated draft, follow sibling ci's `references/revision-tools.md` and
`references/workflow-regression.md`: fixed original, latest accepted text, actual diff, proportional
semantic verification. Do not call unperformed or unresolved checks a pass. Acceptance is tied to
final hashes, then reader-index state can be committed under the project's acceptance policy.

## Output

Keep manuscript prose separate from editorial records. Deliver long prose as the requested file;
use caller path, then user path, then a stated project-local default. Short requested passages may
be inline. No self-praise, explanations or verification tables inside the manuscript. Verification
status and gaps belong in the accompanying report, so pure prose does not conceal unfinished work.

## Invocation contract

```yaml
input_spec: ...
constraints_priority: ...
output_path: ...
budget: full | scene | sketch
```

### budget: full

Standalone default: preparation, drafting and the two-pass self-check. Read
`references/expansion-workflow.md` for multi-chapter work and continuous reading triggers.

### budget: scene

Input is the confirmed scene_card owned by ci's workflow-planning.md. Map `change_chain` to
act/discover/respond, `dialogue_dynamics` to language goals and strategy, `time_handling` to
foreground/compress/omit, `pov` to attention and knowledge, and `turn.embodied_by` to visible change.
Write only the supplied draft path; do not redesign the card or silently update canon.

**Evaluation separation:** Return the draft directly to workflow-review.md, without self-scoring
or revising it. This routes mandatory frequency, punctuation and semantic verification to the
review owner; it does not waive them or mark a raw draft accepted.

### budget: sketch

Exploratory variants for novel-discuss, stored only in the caller's
`agent/discuss/sessions/<session_id>/sketches/`, never formal manuscript or reader-index state.
Honor the requested number/length, project facts and punctuation. Label status exploratory in
metadata, not inside prose. Full manuscript acceptance is not claimed for a sketch.

## Reference ownership

- `references/anti-ai-patterns.md`: canonical language rules, required.
- `references/narrative-craft.md`: conditional presentation modules, required as relevant.
- `references/style-guide.md`: adjustable defaults.
- `references/expansion-workflow.md`: longer works.
- Sibling ci `references/project-context.md`, `reader-index.md`, `revision-tools.md` and
  `workflow-regression.md`: shared context, accepted disclosures and editing verification.
- Sibling auditor `references/language-tools.md`: deterministic scan and LLM classification contract.
- Sibling auditor `references/style-consistency.md` and `references/reading-load-zh.md`:
  scoped style basis and Chinese sentence-comprehension review, loaded when applicable.

Keep entrypoints concise and substantial procedures in references. Do not copy a second language
rule body or store project-specific vocabulary in the skill. A failed density check calls for
contextual editing, not silently raising a threshold.
