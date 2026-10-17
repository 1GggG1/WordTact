# Composing an audit

Coordinator only. Arrange work around the user's question; there are no fixed levels or
mandatory combinations. Read [audit execution](audit-execution.md) after an arrangement is
selected. Workers receive their own packets, not this planning document.

## 1. Lightweight reconnaissance

Identify the request as diagnosis, revision, or a decision about revision. Resolve the project
root, target files and versions, publication order, intended reader, available context, and
existing authorization. Use the task-resolution section of
[shared project context](../../novel-ci/references/project-context.md); do not load the full
canon, historical audits, language rules or scanner output just to choose a method.

Start with the project entry and file metadata only. Do not batch-read every file mentioned
by an entry: the existence of a canon file or old audit does not make its contents necessary
for planning, even when the files are short. Read an existing arrangement's explicit scope
only if needed to establish a prior selection; defer story facts and diagnoses until selection.
Sample a small amount of prose only if a routing question remains after that first step.
Record what was sampled; a sample does not establish full coverage or a manuscript diagnosis.
Ask only if a consequential choice cannot be resolved from these inputs. Keep any preliminary
suspicion out of a later independent reader's packet.

## 2. Recommend and select

Give one recommended arrangement, and one or two alternatives only when they offer meaningful
differences. Explain the task-specific reason, covered scope and omissions, planned worker
count and parallel/sequential phases, relative effort, and whether the result is findings,
revision directions or authorized edits. Do not promise measured speedups or quality gains.
Ask one concise question allowing selection or a custom combination; do not expose a long
configuration questionnaire. Wait for the answer before dependent audits or fanout.

An explicit current method, applicable established arrangement or fixed CI handoff already
selects the method. If the user delegates the choice, select and briefly state the arrangement,
then proceed. Do not ask again for an authorization already given. A generic new request to
audit prose without such context gets reconnaissance and a choice, not an automatic tier or
an unrequested team. Reference-corpus analysis stays on its own entry route.

Agree conditional follow-ups when useful: the condition, affected scope, added work and a
resource bound. A condition becoming true activates an already authorized task without another
question. An out-of-scope addition needs a concrete proposal; continue unaffected authorized
work meanwhile. Silence is not selection, and selection is not permission to edit.

## 3. Available components

| Module | Purpose and input | Dependencies and limits |
|--------|-------------------|-------------------------|
| `skills_review` | Existing [audit workflow](audit-workflow.md), relevant project facts and language tools; full semantic/editorial judgment as well as counts. | Can run alone under the current executor; in a composed multi-review plan, use its own worker. Preserve all existing required checks. |
| `independent_read` | Direct reading of the same declared prose/version and reader condition, without injected editorial skills, scan results or prior diagnoses. | Freeze first-pass findings before any factual-context check. Does not certify mechanical checks or complete manuscript acceptance. |
| `targeted_check` | Verify a specific disputed claim against passages, prior disclosures, author decisions or relevant primary sources. | Can follow a new finding or an existing report after source/version validation; no full audit is a prerequisite. |
| `revision_challenge` | Develop evidence-based revision directions and independently check their premises and side effects. | Needs anchored questions/findings and relevant original text. Existing current evidence is sufficient; neither a dual audit nor a fixed number of viewpoints is mandatory. |

The execution reference owns these modules' packet and output rules. Select only useful
components; combining modules does not require creating a separate agent for each tool/check.
In a multi-review plan the main agent coordinates; the full reviews stay in separate workers.
Thus a skills review paired with independent reading uses two review workers, not the main
agent as one of the reviewers. An independent perspective requires a separate context. Use question-specific
assignments, not personalities or an obligation to disagree. Expansion or canon redesign
outside the authorized revision scope remains a separate handoff.

## 4. Keep a compact plan

Keep the plan in task memory, temporary task artifacts or an existing authorized audit location.
Do not create runtime state in the skill package or change project conventions to store it.
Record enough to resume without replaying the whole discussion:

- Selection and its source: pending, user-selected, established, or delegated.
- Objective, scope/version references, reader condition, edit permission and required checks.
- Tasks with an ID, module, exact question/scope, allowed input references and dependencies.
- Conditional tasks with their activation criteria and authorization; limits on worker count,
  concurrency and challenge rounds appropriate to this plan.
- As work proceeds: actual input exposure, coverage, result location, unresolved gaps and status.

Use the shared context record as the coordinator's index, not as a bundle to forward wholesale
to all workers. A stored prior report is evidence to verify, not authority to repeat its verdict.
Changing methods can narrow the declared task; it cannot silently waive the checks required for
an existing CI gate, selected skills review or actual edits. Preserve the difference between a
completed limited inspection and acceptance of the manuscript.
