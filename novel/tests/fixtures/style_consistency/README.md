# Chinese-fiction style trials

These cases are synthetic. `inputs.json` is the worker input; `expectations.json` belongs only
to evaluation. Do not supply intended judgments, this document's case discussion or other
workers' outputs to a worker. Retain originals, generated candidates and reports outside the
source package. These trials do not establish performance on an author's real novel.

Materialize A with `--context plain` and B/C with `--context guided` using
`tests/style_consistency_cases.py --output <new-directory> --context <variant>`.
A uses the frozen previous skills; B uses the same previous skills with the concise guidance
and approved samples; C uses the upgraded skills with exactly B's input. All three keep the
same task, manuscript, hard author constraints and source history. Guidance is the intentional
A/B difference; B/C isolate the procedure change. Save skill/input hashes and model conditions.

Use fresh isolated workers with only the selected skill location, materialized request and
project paths. Each audit is an authorized candidate revision, not permission to edit other
projects. Writing is a `budget: scene` handoff: write the draft without self-scoring or revision.
Compare anonymous outputs with the original and author constraints before revealing methods.
Assess factual/epistemic preservation, distinct voices, actual comprehension, terminology,
unnecessary edits, missed issues and scope/version reporting separately. No exact ideal rewrite
or aggregate literary score is defined. A may lack guidance needed for a normative judgment;
report that limit instead of counting an unavailable preference as a failure.

Include both needed edits and intentional retention. The stale-reference case supplies an old
digest and the current file: a worker must not invent approval of the changed file. Missing
history limits a longitudinal conclusion. Approved tone changes must not be rolled back merely
to match older chapters. Scanned frequencies do not establish literary quality.

Save first failures and any later reruns. Once used to adjust rules, cases are regression data,
not an untouched holdout. Automated tests check input identity, digest binding and exclusion of
the answer key; model behavior requires executing and reviewing the trials.

For an external-skill control, pin the public repository commit and the exact skill-file digest,
retain its license, and read it only in an isolated trial directory. Keep all author context and
source versions identical to C. Compare editing cases primarily when the external skill targets
editing; label new-prose generation separately. A no-project-skill control still inherits platform
defaults. Report judge model, scoring dimensions and missing evidence; do not turn a small set of
subjective ratings into a general quality or AI-authorship score.
