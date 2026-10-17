# Audit workflow

This is the existing `skills_review` method, also used for authorized revision after synthesis.
The coordinator resolves [audit planning](audit-planning.md) before entering it. An assigned
worker comes here directly, stays within its packet, and does not restart planning or delegate.
Use [audit execution](audit-execution.md) to combine methods; independent readers do not load
this workflow. In a multi-worker audit all reviewers diagnose only; the designated executor
performs any authorized edits after the selected reviews and necessary synthesis are complete.

## 1. Scope and versions

Read the shared project-context protocol before auditing. Diagnose when requested; when the user
has requested edits, carry out the authorized minimal revision without repeated permission prompts.
Identify fragment vs complete chapter from actual material. A short fragment has measured counts,
not extrapolated chapter failures. Missing context limits a conclusion rather than proving absence.

Record canonical files, reading files, their hashes, reader condition and author decisions. Use
existing publication mapping; do not count both versions. Do not judge manuscript quality from
assumptions about whether a person or a model wrote it.

For a style-consistency task or applicable project style rules/samples, use
[style consistency](style-consistency.md) to pin the relevant sources and their narrator,
character, form and scene scope. Keep explicit rules separate from observations inferred from
samples. Existing author decisions remain operative; no new corpus or full-book audit is required.

## 2. Read before classifying

Read the target and adjacent passages. Multi-chapter review follows publication order and the
continuous-window protocol in `../../novel-ci/references/project-context.md`. Retrieve older
relevant disclosure passages through reader-index.md; future disclosures must not leak backward.

Review references and actors, causes/conditions, what the reader and each character know, repeated
functions, voice, and the canonical language rules. Repetition can be necessary for a changed
listener, calculation, disagreement or callback; explain the actual function rather than labeling
all military speech or all catchphrases exempt. An unnamed recurring person needs intervention
only if identification or differentiation fails. Suggest a stable label/name if needed; do not
silently name, merge or promote a candidate into canon.

For sentence-comprehension obstacles or requested reading-load review, use
[Chinese reading load](reading-load-zh.md). Trace the actual head, actor, referent and relation
before proposing a change. A long sentence can be clear; many short sentences can obscure a
condition. Compare voice within compatible scene conditions rather than averaging all dialogue.

Apply the shared [evidence boundaries](../../novel-ci/references/project-context.md#evidence-boundaries-in-writing-and-review)
to material concerns about knowledge, decisions, chronology and object continuity. Locate the
prose that establishes the relevant state and its change; distinguish explicit support,
reasonable inference, background-only explanation and unresolved coverage. Report project
compatibility separately from textual support. A familiar outline outcome cannot supply a
missing causal step. Before flagging a gap, test narration order, the narrator's established
access and purposeful ellipsis; do not turn an unstated fact into an automatic failure.
If project context clears an apparent contradiction, retain any independently supported reading
problem and explain the narrower conclusion. This applies to the skills review and synthesis,
even when no independent reading module was selected.

## 3. Mandatory language evidence

Use `language-tools.md` for scan, punctuation and recount. Load the project language profile or
run generic defaults and nominate new recurring patterns from the prose. The LLM classifies all
relevant occurrences with source IDs, senses, register, narrative function and retained/changed/
unresolved outcome. Scripts verify this record and recount; no tokenizer or author classification
queue. Preserve both raw and semantic counts. Retention does not subtract from the latter.

Assess paragraphs, complete chapters and rolling three-unit statistics. For every threshold
crossing inspect collective monotony as well as individual usages. Reference corpora require
matching definitions and denominators; they are calibration evidence, not an obligatory target
style. Never relax a threshold during revision to hide a failure. Recount replacement expressions.

When reference comparison is requested or an applicable project reference exists, follow
`style-reference.md`. Pin its reference_id, measure with the same feature definitions and window
contract, and attach difference evidence to the relevant findings. Surface and semantic counts
must not be mixed. Pure statistical departure may be retained after contextual review; it is not
automatically a defect. Merge duplicate alerts while preserving existing scan/recount records.
Missing or mismatched reference evidence limits the comparison, not the author's narrative design.
Reference distributions describe use; they do not update author rules or the approved sample set.
For cross-chapter style review, compare the declared history with the pinned style basis and
record legitimate changes, incomparable passages and missing coverage separately from drift.

## 4. Anchored findings

For each finding report its source/version, exact location, concrete reading effect, supporting
context, minimum useful fix and protected meaning. Uncertain intent first prompts further reading;
only a consequential unresolved author choice requires a question. A localized author decision
stays localized. Uncertainty is not a license for an automatic edit.
Merge style-rule conflicts, reading-load findings and statistical alerts at the same location,
retaining each basis. A suggested preference is not a confirmed rule violation. Stable terms and
names do not need synonym rotation; preserve character and scene differences that serve the text.

## 5. Authorized revision

Freeze full originals and latest accepted versions with revision-tools.md. Preflight the whole
batch for matching hashes, unique anchors, allowed range and non-overlap. Generate the smallest
candidate, inspect actual diff, apply safely and keep recoverable before-images. Annotate temporary
candidate names or other author-pending proposals; they are not established facts.

Do not blindly remove the negative half of a contrast or turn all periods into commas. Changing
“不能排除” to “会发生”, or “已核对” to “交给核对”, can change the story despite fewer repeated words.
Use workflow-regression.md against original and latest accepted prose, not only character sheets.

## 6. Acceptance

On the same final hashes: normalize punctuation; recount words and newly introduced habits;
verify semantic preservation, narrative function, voice and cumulative change; rebuild/check
publication mapping when applicable. Only then apply the project acceptance policy and commit
reader-index candidates. Every actual edit, including optional P3 wording, receives proportional
verification; pure glyph normalization may use a smaller semantic surface.

Report each required check as PASS/FAIL/RISK/SKIPPED with evidence. Unperformed or incomplete
mandatory checks result in NEEDS_VERIFICATION, not a claim of completed editing. Confirmed
problems remain NEEDS_PATCH; a failed candidate may be reverted without clearing that finding.
Reader coverage is judged against the stated scope, never an invented whole-book claim.

## Compressing a repeated explanation

Before deleting an apparently repeated sentence, separate its claims: an established rule may
share a sentence with new evidence about who learned it, when, under which condition, or what
someone actually did. Remove the repeated explanation while preserving the distinct information,
or record why that information is dispensable within the authorized edit goal. Adjacent mention
of a rule does not itself establish that the current character already knows it. Compare the
actual deleted span, not just the polished replacement, during semantic regression.
