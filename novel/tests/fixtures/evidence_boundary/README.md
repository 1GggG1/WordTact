# Evidence boundary forward trials

All cases are synthetic. `inputs.json` contains only raw prose, narrative agreements, project
context and user requests. `expectations.json` is evaluator-only; never give it to a worker.
The prose is identical between `brief` and `expanded` context variants. Narrative agreements
also stay fixed, so adding a backstage synopsis must not change what the prose has disclosed.

Materialize a fresh workspace with:

```sh
python3 tests/evidence_boundary_cases.py --output /tmp/evidence-brief --context brief
python3 tests/evidence_boundary_cases.py --output /tmp/evidence-expanded --context expanded
```

Use separate fresh workers for the two audit variants. Supply the auditor skill entrypoint,
the materialized audit request and paths only; no implementation history, expected answer,
other worker output or leading description of the issue. They may load the specified context:
the test concerns evidence discipline with context available, not a claim of blind reading.
Use the expander entrypoint, writing request and briefs for a separate writing worker. Allow
generated drafts/reports only in its temporary project. Follow the selected skill's normal
verification route; bounded semantic audit workers must not claim unperformed full acceptance.

Assess outcomes against the original text and evaluator criteria, not exact wording or a
single ideal rewrite. Check every negative and retention case, the two dimensions in A09,
and correct attribution in A02/A06. Extra context may improve factual understanding without
erasing a remaining textual problem. Do not reward flagging every case or adding explanations
to every gap. Evaluate generated prose separately from the writer's self-assessment.

Record skill/input hashes, actual context access where observable, findings, changed source
files, missed issues and false positives. Retain failed runs; after tuning on a case it is
regression material, not held out. Unexecuted cases remain untested. These are small workflow
trials, not proof of improved long-form literary quality or guaranteed context isolation.

Automated fixture tests validate the reproducible input split, byte-identical paired prose,
source anchors and no-overwrite behavior. They do not judge whether a model applied the rule.
