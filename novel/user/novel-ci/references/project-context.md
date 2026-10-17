# Shared project context

Owner: novel-ci. Reading this protocol does not start the CI pipeline or require a scene card.
Use it before standalone expansion, editing, CI planning/review and chapter integration.

For standalone audits, resolve the arrangement through
[audit planning](../../novel-auditor/references/audit-planning.md) first. Reconnaissance uses only
the task-resolution information below; the selected skills review/revision loads the relevant
evidence and methods. Do not send this protocol or the complete context record to an independent
reader: its coordinator constructs the minimal packet specified by
[audit execution](../../novel-auditor/references/audit-execution.md). Existing CI handoffs keep
their selected method and required verification; they do not restart plan selection.

## Resolve the task

Read the project entry instructions and the user's current request before selecting documents.
Record objective, authorized edit scope, explicit project root, authoritative manuscript and derived
reading files, reading order, reader condition (continuous reading / serial following / companion
story), and the checks this task claims to complete. A fragment is not a complete chapter.
Never infer a novel root from a skill's installation directory.

## Load only relevant evidence

Support existing `agent/context` project/progress/conventions/decisions files and optional
`canon/style` style-guide, prose-benchmark and voice-samples. Use established project conventions
without asking the author to opt in again. Read current status first; follow references into history
only when the task needs it. Do not rewrite or migrate project memory to use this protocol.

For each operative instruction keep source, scope and any later superseding decision. The latest
explicit applicable author decision wins over a generic style default. A preserved line, joke or
plot beat is not a global exemption for all similar wording. Do not impose chat register on fiction;
voice follows the novel, character identity, relationship and scene. Resolve routine ambiguities
by reading adjacent prose and decisions. Ask one question only when missing author intent would
change a consequential creative choice; continue independent work meanwhile.

## Evidence boundaries in writing and review

Keep these sources of knowledge distinct when drafting, reviewing and revising:

- Author/project knowledge: established world facts, private plans and intended outcomes.
  Plans remain plans; an outline or memory summary is not evidence that an event happened on page.
- Narrator knowledge: what the established voice, form, distance and time of narration permit.
  An omniscient or retrospective narrator may know more than the current viewpoint character.
- Character knowledge: what this person could have perceived, learned or reasonably inferred
  by this point in story time. Another character's knowledge does not transfer automatically.
- Reader information: what the declared audience has received in publication order up to this
  passage, including what the passage itself legitimately introduces. A disclosed claim may
  still be a lie, mistake or unresolved clue rather than a world fact.

Judge two questions separately: is the passage compatible with project facts, and does the
text support the knowledge, action or connection it asks the reader to accept here? Background
context may settle the first while leaving the second unresolved. Do not use an outline,
author explanation, later chapter or remembered summary to invent an earlier decision, message,
transition or object transfer, or to dismiss a textual gap merely because the intended result
is familiar. An explicit instruction to preserve a mystery limits revision; it does not make
the hidden answer information already available to the reader or character.

For a material concern, cite the relevant passages and identify support as explicit, reasonably
inferable, background-only or unresolved. Track only the relevant knowledge/state change, not
every sentence. Test the strongest plausible reading before declaring a defect. If support is
missing, distinguish a contradiction from an insufficiently established connection and from
an optional stylistic preference. Missing coverage limits certainty; it does not prove absence.
When context changes a finding, state which question it resolves and what textual issue, if any,
remains. Use the existing findings/semantics record; no additional acceptance schema is needed.

Preserve legitimate narrative choices. Reconstruct story time separately from narration order:
a flashback or flashforward is not a time contradiction. Temporal cues can be implicit when the
surrounding text makes the shift intelligible. Naming or revealing facts through an established
omniscient narrator does not grant that knowledge to a character. Ellipsis, off-page routine
actions and withheld explanations may work through supported inference or purposeful uncertainty;
do not demand every transfer be shown, every name be introduced in dialogue, or every mystery be
explained immediately. Require correction only for a concrete broken connection or a violation
of the established narrative contract, not simply because a fact was previously unstated.

During writing, realize the needed decisions, discoveries and transitions in prose or supported
implication; do not treat the outline's intended outcome as the character's existing knowledge.
During review, already knowing the project does not count as an independent first reading.
These checks supplement, rather than replace, a separately selected independent reader.

## Task context record (in memory or the task's audit directory)

Record `objective`, `edit_scope`, `source_paths`, `reading_order`, `reader_condition`,
`applicable_decisions` (source + scope), `protected_items`, `language_profile`, `reader_coverage`,
`required_checks`, and `gaps`. This is a reference bundle, not a second canon or an automatic
summary of all historical logs. Preserve the original source when summarizing a decision.

For a composed audit, keep a reference to its selected arrangement, authorization, task inputs,
dependencies and results alongside this record. The auditor planning/execution references own
that orchestration; this file remains the owner of shared context and verification. Record
method-specific coverage without weakening the checks required for a claimed acceptance.

When a language reference is established or requested, add optional `style_reference` context:
artifact path, pinned reference_id, source_group, scope/register and whether this task explicitly
requires comparison. Its contract belongs to sibling auditor's `references/style-reference.md`.
Discover it through current project instructions or the task's selected artifacts; do not choose
an arbitrary profile merely because it exists. Reference data stays in the consuming project.

For Chinese-fiction style consistency or applicable author rules/approved samples, add optional
`style_basis` to the same context record: authoritative source paths/versions or hashes, explicit
rules and strengths, narrator/speaker/form/scene scope, stable terms and allowed aliases, approved
sample spans, separate inferred observations, and effective exceptions/superseding decisions.
Follow [style consistency](../../novel-auditor/references/style-consistency.md). Keep a short brief
with source links; existing project style files remain authoritative, without a second canon or
required new directory. Missing samples do not block work on existing rules and local clarity.
This normative context is distinct from descriptive `style_reference` measurements. Do not
silently refresh either from newly accepted chapters; record gaps and scope-limited conclusions.

## Shared methods and ownership

- Language rules: `../../novel-expander/references/anti-ai-patterns.md` (canonical entry).
- Scoped Chinese-fiction style and reading load: [style consistency](../../novel-auditor/references/style-consistency.md)
  and [Chinese reading load](../../novel-auditor/references/reading-load-zh.md), loaded when applicable.
- Scan/recount and literal repetition: `../../novel-auditor/references/language-tools.md`.
- Reader index, publication mapping, prefix queries: `reader-index.md`.
- Frozen originals, staged batch edits and bound acceptance receipts: `revision-tools.md`.
- Semantic checks and final acceptance: `workflow-regression.md`.

Sibling references resolve relative to this file in both `user/<skill>` source layouts and flat
`<skill>` installations. Root dispatch resolves `user/<skill>/SKILL.md` first, then
`<skill>/SKILL.md`. This locates bundled resources, never project data.

## Ordered reading and source mapping

Use the project's existing publication order and chapter mapping. One file is one reading unit
only when there is no split. Count actual reading text once: never add canonical and published
copies together. The reader manifest also accepts whole-file `unit_id/path/complete_chapter`
entries used by the scanner. For mapped slices follow `reader-index.md`; scanners receive the
actual corresponding publication files, in the same order, or explicit extracted task copies.
Verify extracted text against its recorded slices. Do not invent a mapping when unavailable.

The authoritative manuscript is edited, then existing project commands rebuild derived files.
Verify coverage, sequence, duplicate/omitted passages and hashes before accepting a new mapping.
A broken mapping blocks dependent writes/completeness claims, not unrelated read-only work.

## Reading coverage

Three-unit rolling counts detect recent language drift; they do not replace continuous reading.
On initial relevant indexing, each five newly accepted published chapters, a substantive earlier
revision, or a multi-chapter review request, read a continuous window of up to ten published
chapters. With fewer than ten read all; fewer than five explicitly limits the evidence. For a
longer requested range cover the entire range in windows, retaining prior disclosures between
windows; do not silently reduce a whole-book review to its last ten chapters.

Read full prose in the window. Use earlier index entries to retrieve relevant original passages.
Check repeated explanation/confirmation/decisions, voice convergence and pacing. A new listener,
a calculation, a challenge, a joke callback or a changed consequence can justify repetition.
New listeners do not automatically require either a full replay or a one-sentence summary.

## Acceptance boundary

Apply the project's actual acceptance policy. A candidate, author-pending copy or unbuilt
publication is not accepted merely because a script can hash it. Read-only tasks may prepare
index candidates in memory but do not commit them. Only accepted and version-verified prose
enters the derived reader index; future plans and unconfirmed statements never become canon.

## Verification record contract

A new review/regression carries `verification` using this schema. Its hash map identifies the
complete declared manuscript scope. `checks` contains each required check, with actual evidence.
Mapping is required only for tasks using derived publication text. Reader coverage is required
only for the cross-chapter scope actually claimed. Never infer PASS from absent historical fields.

```yaml
verification_record:
  source_hashes: {}                 # project-relative path -> SHA-256 of final bytes
  required: [frequency, punctuation, semantics]
  checks:
    frequency: {status: SKIPPED, evidence: "", sha256: ""}
    punctuation: {status: SKIPPED, evidence: "", sha256: ""}
    semantics: {status: SKIPPED, evidence: "", sha256: ""}
  coverage: {requested: [], verified: [], gaps: []}
```

Check statuses use PASS/FAIL/RISK/SKIPPED; frequency retention is PASS only with localized reasons
and actual counts still visible. Revision-tool receipts separately support RETAINED and require
hash-bound evidence. This record must be converted explicitly to that documented receipt; it is
not an invitation to fill all fields with PASS. Script validation establishes integrity, not truth.
