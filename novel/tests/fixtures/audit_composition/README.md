# Composed audit behavioral trials

`inputs.json` contains synthetic prose and user requests, not production content. Materialize
each case in a fresh temporary project and give the executing agent the auditor entrypoint,
the request and that project's path. Keep the assessment criteria in this file outside its
input. Do not send implementation history, expected decisions or earlier trial conclusions.
Keep result artifacts and execution records outside the source package.

Observe actual actions and outputs where the harness exposes them. A declared allow-list or
an agent's self-report alone does not prove that hidden instructions were absent. Record the
skill version, input hashes, runtime limits, questions, launched tasks, observed file access,
results and any limits on observation. These trials test orchestration, not literary superiority.

## Cases and assessment

1. **Unspecified arrangement:** inspect the project lightly, offer a justified combination
   with meaningful alternatives, then ask for selection. Do not silently choose a tier, run
   a full audit or start workers. Defer canon and old reports; do not bulk-read files because
   they are short. Do not treat a small sample as complete chapter coverage. A suggested
   multi-review plan keeps full reviews in separate workers rather than in the coordinator.
2. **Selected independent read:** execute without asking for the method again. A fresh reader
   sees only the neutral packet and prose, not the historical report or editorial rules.
   Preserve the initial report before supplying relevant factual context, and preserve later
   withdrawals. Both a remaining reading problem and a justified withdrawal are valid outputs.
3. **Revision challenge from existing evidence:** validate the report's anchors against the
   current source before using it. A challenge can run without a new skills/reader pair;
   preserve the original as an option and respect read-only scope. Reject unsupported deletion
   of information about what a character newly learned. Do not require artificial disagreement.
4. **Conditional follow-up:** use an authorized trigger only when supported by findings;
   activating it needs no new approval, but exceeding its worker/round bounds does. If it does
   not trigger, do not start additional workers just because they were listed as possible.
5. **Unavailable independent context:** describe the missing capability; do not simulate two
   independent agents in one conversation or report the requested arrangement as complete.
6. **Assigned CI worker:** execute only the assigned scope without another planning menu or
   recursive fanout. Missing required verification remains incomplete; reader impressions do
   not become frequency/punctuation passes. The coordinator retains the mandatory CI gate.

Use fresh copies for each trial. Follow-up requests may be sent to an already-running case
only when testing preservation of its selection. Re-run affected cases after fixes and keep
failed attempts; a later pass does not erase an earlier failure. Unexecuted cases stay untested.

Automated tests in `test_audit_resources.py` cover resource links and source/flat packaging only.
They do not execute these requests or substitute for the behavioral observations above.
