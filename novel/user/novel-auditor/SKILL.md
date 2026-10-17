---
name: novel-auditor
description: "Review or revise Chinese fiction for language habits, punctuation, meaning, reading load and voice; maintain style across chapters without flattening characters or scenes; build language reference profiles and compare wording distributions. Open-ended audits start with project-entry/metadata reconnaissance and a selected combination of methods. Use for 审稿、改稿、润色、检查口癖、检查重复、统一中文小说文风、检查跨章措辞、读者视角通读、建立语言参考档案、参照用词审稿. Diagnose for feedback; make minimal authorized edits for revision. Reference-only analysis needs no novel project. Outline-to-prose routes to novel-expander. Statistical differences are evidence, not automatic prose failures. English and academic editing are outside this fiction workflow."
---

# Novel Auditor

Preserve author intent while resolving concrete reading problems. Existing prose is the starting
point, not an invitation to rewrite the author's voice. Identify the request as diagnosis,
authorized revision, or broader reconstruction from context; do not ask again when authorization
is already clear. Major changes beyond that scope require a concrete proposed change first.

## Reference-only analysis

For building or refreshing a language reference, read `references/style-reference.md` and the
selected corpus. Establish feature definitions and collect/build evidence with its script.
This mode does not require novel project state, scene cards, audit-plan selection or manuscript
acceptance checks. It does not edit prose. For draft review, resolve the route below and load that reference only
when the task requests comparison or an applicable project reference is already established.

## Resolve the audit arrangement first

- **Coordinator:** first read [audit planning](references/audit-planning.md); the only project
  inputs at this point are its entry/instructions and file metadata. Do not batch this read
  with canon, historical audits or prose. Planning permits a bounded prose sample later only
  if it is needed to resolve a routing question. Recommend a task-specific combination,
  and obtain the user's choice unless it is
  already explicit, established for this task, or delegated. There are no fixed tiers.
  After selection, use [audit execution](references/audit-execution.md) for worker packets,
  independent contexts, conditional follow-ups and evidence-based synthesis. Do not preload
  the preparation below just to offer a plan.
- **Assigned worker:** execute only the assigned module and scope. Do not offer another plan
  or spawn more auditors. A `skills_review` worker uses the preparation below; other workers
  follow their supplied module packet. An `independent_read` worker must be launched directly
  with its minimal packet, without loading this entrypoint or the suite's review references.
- **Existing workflow:** a fixed CI review, patch handoff, explicit request for the usual
  audit, or established project arrangement is an existing choice. Preserve that workflow
  and its required checks without an extra selection question. Optional modules require
  selection or delegated authority; ordinary drafting self-checks remain unchanged.
  An explicit style-consistency or reading-load task can use `skills_review` directly within
  that scope; it does not imply adding independent readers or a whole-book rewrite.

## Skills review preparation

These requirements and the decision rules below apply to `skills_review` and authorized
revision. Module selection never removes their required evidence or editing safeguards.

1. Load `../novel-ci/references/project-context.md` relative to this skill directory.
2. Read `references/anti-ai-patterns.md`, the compatibility pointer to canonical language rules.
3. Read `references/audit-workflow.md`. For scans and punctuation use `references/language-tools.md`.
4. When editing, also read `../novel-ci/references/revision-tools.md` and
   `../novel-ci/references/workflow-regression.md`; multi-chapter tasks use reader-index.md there.
5. When comparing reference usage, read `references/style-reference.md`. Pin the reference version,
   keep surface and semantic counts separate, and merge shared findings with existing review rows.
6. For style consistency or applicable project style rules/samples, read
   [style consistency](references/style-consistency.md). For reading-load review or concrete
   sentence-comprehension obstacles, read [Chinese reading load](references/reading-load-zh.md).
   Keep these within the selected task; no corpus or scene card is required.

## Decision rules

- Apply the shared [evidence boundaries](../novel-ci/references/project-context.md#evidence-boundaries-in-writing-and-review):
  project compatibility and support in the prose are separate judgments. Familiarity with the
  outline cannot clear a missing connection; preserve supported inference and narrative license.
- Author decisions have concrete scopes. A single retained line is not an exemption for an entire
  word class. Formal dialogue is checked for collective monotony while preserving necessary detail.
- LLM judgment resolves word sense, voice, repetition function and contextual equivalence. Scripts
  locate/count/hash; do not build a tokenizer or delegate ordinary classification to the author.
- Every over-threshold category needs a resolution: revised and recounted, specifically retained
  with evidence, or unresolved. Individual grammatical sentences can still be monotonous together.
- Prefer the smallest change that solves the problem, but do not force synonym substitution when
  removing an unnecessary explanation or changing sentence structure better preserves the passage.
- Punctuation glyph normalization differs from changing sentence boundaries or semantic emphasis.
- Keep the original as an option; if the candidate is worse, reject it without erasing the old issue.
- A reference deviation needs contextual interpretation, not convergence to a quota. Retain legitimate
  variation and report insufficient evidence. Keep the author's narrative design fixed during language edits.
- Compare like scopes: narrator, speaker, form and scene conditions. Preserve purposeful differences,
  stable terms and clear long sentences; an accepted chapter does not automatically become the style baseline.

## Output and CI boundary

Diagnosis returns scope/versions, anchored findings, raw and semantic counts, retention reasons,
coverage gaps and suggested changes. Authorized revision also returns actual diff, frozen-original
reference, regression evidence and final status. Keep editorial records outside manuscript prose.

In CI, only language findings map to P2/prose_lint. Route factual, causal, knowledge and voice
failures to the appropriate checks and severity; never downcast them because auditor found them.
Reader repetition uses reader_redundancy. Unfinished mandatory verification is NEEDS_VERIFICATION,
not PASS or a speculative patch. Optional taste alone is P3. Do not change canon or a confirmed
scene card as a side effect of polishing.
