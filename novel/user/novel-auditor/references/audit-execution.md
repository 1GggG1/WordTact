# Executing a composed audit

Coordinator reference, loaded after [selection](audit-planning.md). Launch only selected tasks
and authorized conditional follow-ups. The coordinator owns scheduling and synthesis; workers
execute bounded tasks and return results, without selecting another plan or spawning workers.
A solo `skills_review` may use the current executor and the existing
[audit workflow](audit-workflow.md) directly.
For a composed multi-review plan, launch the full reviews as separate worker tasks and keep
the main agent on coordination and evidence-based synthesis. In particular, a skills review
plus independent reading uses two workers; moving the skills review back into the coordinator
would defeat the selected context separation. Limited concurrency permits sequential fresh
workers, not silently replacing a worker with a full review in the coordinator's context.

## Packets and independence

Pin authoritative files and reading files/ranges to the same source hashes, reading order and
reader condition. Do not count canonical and publication copies twice. Each worker packet
states its task ID/module, question, scope, allowed inputs, read-only boundary, output location,
resource limit and no-delegation boundary. Send source references rather than the coordinator's
entire history. Reviewer output belongs in a task-specific artifact or memory, not manuscript
prose; use separate result locations and retain original reports.

Use a fresh context without inherited conversation for independent work. Do not assume that a
new role label clears prior instructions. Inspect the runtime's actual context/injection
behavior where available, and record limitations; an input allow-list is not proof of isolation.
Required platform instructions and applicable user constraints still apply. Here “without
skills” means no injected editorial methodology, not exemption from those obligations.

When true separation is unavailable, report it. Fresh isolated workers may run sequentially if
that still fits the selected arrangement; describe the actual scheduling. Never impersonate
two independent agents inside one contaminated context or claim an unavailable module passed.
Complete unaffected work; propose an alternative if the selected method cannot be delivered.

## skills_review

Give this worker the [skills review preparation](../SKILL.md), relevant shared project context,
and the pinned prose. It follows the existing method, including language evidence and semantic
judgment; it is not restricted to mechanical errors. When paired with independent reading, both
cover the same declared scope and neither sees the other's findings before its first report.
The packet marks this as an assigned read-only worker, so it skips plan selection and revision.

## independent_read

Launch directly with a neutral task packet, not through the suite dispatcher or auditor skill.
The packet contains only the user's reading goal, manuscript files/ranges and hashes, order,
intended reader, necessary operational constraints and this output request: concrete reading
observations with source locations, supporting passages, uncertainty and actual coverage.
Tell the reader to return that first-pass record before requesting any additional factual
context; the coordinator releases the next phase only after the initial report is preserved.
Do not include this reference, other review instructions/checklists, project language profiles,
scan/index diagnoses, prior audits, other workers' findings or the coordinator's suspicions.

**First pass:** read the full selected prose in publication order. Do not inspect editorial
skills, project canon summaries or historical audit directories. Preserve the report as the
initial reading record before accessing contextual evidence. A reader familiar with a main
story is a different task from a completely new reader; state that condition and disclose gaps
in supplied prior prose rather than silently changing the audience.

**Context check:** after freezing that record, provide only relevant raw prior passages, facts
or scoped author decisions, without another worker's diagnosis or editorial methodology.
Record each initial finding as retained, revised or withdrawn with the evidence and reason;
keep the initial report. Context may explain the event while leaving a real communication
problem in the prose. Future disclosures do not retroactively make information available to
the reader or character. If needed context is unavailable, preserve uncertainty.

## targeted_check

Send the claim as a question, its anchors and versions, and the relevant original evidence.
Check whether it holds and seek plausible counterevidence. A prior report supplies a lead,
not a verdict. Return confirmed, refuted or unresolved with citations, applicability and gaps.
Use primary sources for external factual claims when needed. Do not override an intentional
fictional premise with real-world assumptions. Limit conclusions to the assigned question.

## revision_challenge

Provide anchored findings/questions, original passages, applicable author decisions and the
authorized edit scope. Validate existing report versions before reusing them; a fresh complete
audit is unnecessary when its evidence is already sufficient.

Separate proposal and evaluation assignments. The proposer develops the smallest useful
revision direction and genuinely different alternatives where warranted, identifying intended
benefits, protected meaning and likely costs. The checker first examines the premises and
original evidence independently of the proposal, then checks the proposed directions for
missed evidence or damage to facts, voice, causality and disclosure order. These are tasks,
not personas: either may recommend retaining the original, and neither must invent dissent.

Schedule the independent initial work in parallel when possible, followed by a bounded exchange
of proposal, objections and response. Recommend one exchange initially; additional rounds need
new checkable evidence and must remain within the selected plan. No consensus is required.
Return a preferred direction, alternatives, supporting/counterevidence and unresolved author
choices. This module does not itself edit prose or authorize broader reconstruction; an
out-of-scope narrative decision can be handed to novel-discuss without loading its entire
discussion workflow into an ordinary audit.

## Synthesis without losing evidence

Request a short summary plus a complete finding index and pointers to full evidence, rather
than full scan dumps or reading logs in the coordinator context. Index every finding, including
withdrawn and lower-priority ones; a summary length limit must not silently discard them.
Fetch only the necessary passages/details for adjudication. Record actual parent-context cost,
total usage and elapsed time separately when available; do not infer savings from agent count.

Merge duplicates by claim, location and version, preserving contributing IDs and disagreements.
For each issue record evidence, counterevidence, a decision (accepted, rejected or unresolved),
reason, suggested direction and any required follow-up. Multiple votes or confident wording are
not proof. A finding from only one worker is still eligible. Validate conclusions against the
original passages and applicable context, not just the summaries; keep subjective author choices
distinct from demonstrable errors. Apply the shared [evidence boundaries](../../novel-ci/references/project-context.md#evidence-boundaries-in-writing-and-review):
context can settle compatibility with the world while leaving a textual connection insufficient.
Do not discard that narrower finding merely because the coordinator knows the intended plot.
Reuse completed same-version checks instead of rerunning the
whole workflow merely because a second module or CI consumer needs the result.

## Revision and completion

All audit workers remain read-only. After the selected reviews and relevant follow-ups finish,
one designated executor performs already authorized edits, using
[revision tools](../../novel-ci/references/revision-tools.md) and
[proportional regression](../../novel-ci/references/workflow-regression.md). Diagnosis-only
requests end with findings/directions. Selection of more reviewers never expands edit scope.

Report each task's actual coverage, independence limitations and completion/gaps. If sources
change, invalidate affected findings/checks and verify the new version before acceptance.
Unavailable workers, stale evidence and unfinished selected checks stay explicit; mandatory
verification gaps yield NEEDS_VERIFICATION, not PASS. Confirmed problems remain NEEDS_PATCH.
A completed independent read or plan discussion alone does not certify the existing skills
review or CI gate. Use the shared verification record for checks actually performed on the
final hashes; do not manufacture frequency/punctuation passes from reader impressions.
