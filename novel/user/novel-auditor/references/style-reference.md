# Reference distributions for language review

Use this module to build a reusable language reference or compare a draft with an existing
reference. It supplies frequency evidence for wording and anti-AI review. Author-provided plot,
motivation, information order and narrative pacing are constraints, not features to optimize.
This module does not identify authors or models and does not score prose quality.

For reference-only analysis, read this module and the supplied texts; a novel project, scene card,
CI state and manuscript acceptance checks are not prerequisites. For an actual prose audit, also
follow audit-workflow.md, the canonical language rules and the existing revision protocol.

## Workflow and ownership

1. Resolve explicit source roots and selected texts. Read representative passages and relevant
   author choices. Nominate precise words, phrases or bounded sentence-pattern candidates.
2. Freeze feature definitions and measurement settings. Collect evidence over the declared corpus.
   Surface matching is the default; selectively classify semantic features in context.
3. Build a descriptive reference. Calibrate an advisory policy only with separate chapters and
   a recorded assessment; keep the final holdout separate from feature/prompt/parameter tuning.
4. Collect the target using the identical feature spec, then compare with an applicable reference
   group. Explain the measured difference, inspect its locations, and retain or suggest a local edit.
5. Authorized edits use the existing frozen-original, recount and semantic-regression workflow.
   Check replacement expressions too. A candidate that damages meaning or voice is rejected.

The agent proposes features and interprets uses; Python retrieves, counts and verifies versions.
Do not estimate counts from reading impressions, interpolate unreviewed word senses, or hand an
ordinary classification queue back to the author. No NLP dependency or tokenizer is required.

Reference profiles and the existing `language-profile.json` have different purposes. The latter
owns old scan rules and fixed review triggers. This module neither rewrites it nor clears its
mandatory review rows. Merge overlapping findings in the human report and retain both evidence
sources. A justified retention still counts. Explicit author requirements take priority.

For Chinese-fiction style consistency, [style consistency](style-consistency.md) owns the scoped
author rules, approved samples and their change history. This module owns descriptive measurement.
Neither a statistical fit nor acceptance of a draft promotes that draft into a new style rule or
reference sample. Use compatible narrator/speaker/form/scene scopes; a register label alone does
not prove two passages comparable. If reliable grouping is unavailable, read the passages or
report the limitation rather than inventing speaker labels or pooling distinct voices.

## Inputs

Run `scripts/style_reference.py` relative to this skill with Python 3.9+. Never infer corpus or
project roots from the skill path. Input text is UTF-8. Output parents must already exist; every
output path must be new. The tool never edits prose. These JSON objects live in the consuming
project, normally `agent/audits/style-references/<id>/r<N>/`, not in the skill source package.
Run-specific target evidence and comparisons belong in that project's audit directory.

### Corpus or target manifest

```json
{
  "schema_version": 1,
  "language": "zh",
  "text_type": "fiction",
  "profile_id": "selected-prose",
  "revision": 1,
  "scope": "用户选定作品中的叙述用词",
  "units": [
    {
      "unit_id": "sample-01",
      "path": "samples/01.txt",
      "complete_chapter": true,
      "source_group": "author-a/work-a",
      "partition_group": "chapter-01",
      "register": "narration",
      "role": "fit"
    }
  ]
}
```

`profile_id`, positive `revision` and `scope` are required by build, optional for target collection.
All other displayed fields are required. `complete_chapter` describes the actual input, even though
this module does not apply chapter thresholds. Enrich an ordinary reading manifest with the
required metadata before collecting; passing an unchanged legacy manifest is an error.

`source_group` identifies an author/work or other explicitly selected reference population.
`partition_group` identifies the original chapter/document, shared by all its slices and revisions.
`register` is a supplied language-context label, never an inferred scene category or speaker.
Use a broad honest label when finer labeling is unavailable. Compare like labels and text types;
do not relabel a passage merely to obtain a preferred result.

Roles are `fit`, `calibration`, `holdout`, `target`. Build permits only fit and calibration; only fit
contributes to the reference distribution. Compare permits target or holdout, rejecting known
overlap with fit/calibration. A partition cannot span roles within a manifest. Use stable metadata
across files: hashes cannot detect undeclared ancestry or every near-duplicate.

Paths must resolve inside `--source-root`; escaping symlinks and traversal are rejected. Duplicate
resolved files, identical text copies and declared overlapping original spans are rejected. For
an exact extracted slice, add `extraction: {path, source_sha256, start, end}` to the unit: the origin
path is relative to the same root, hash covers original UTF-8 bytes, offsets are zero-based Unicode
characters with exclusive end. The script verifies the exact substring. For other cleaning or
conversion, preserve a separate provenance record; do not claim it is an exact slice.

### Feature spec

```json
{
  "schema_version": 1,
  "measurement": {
    "denominator": "nonwhite_characters",
    "normalization": "none",
    "overlap": "merge_connected",
    "window_algorithm": "nonwhite-v1",
    "window_chars": null
  },
  "features": [
    {
      "id": "connector-bian",
      "label": "便的连接用法",
      "definition": "排除方便、便宜、随便等词内成分，判断实际连接用法",
      "forms": [{"kind": "literal", "value": "便"}],
      "count_basis": "semantic"
    },
    {
      "id": "meanwhile",
      "definition": "与此同时这个连续字符串的表面出现次数",
      "forms": [{"kind": "literal", "value": "与此同时"}],
      "count_basis": "surface"
    }
  ]
}
```

Each unique feature requires `id`, `definition`, nonempty `forms`, and `count_basis`. Optional fields
are `label` and `legacy_category_id`. A form has only `kind: literal|regex` and `value`. Regexes are
candidate retrieval: use bounded spans, avoid ambiguous nested repetitions; zero-length matches
are errors. A legacy-category mapping is advisory metadata: verify identical definitions and
forms before merging evidence, never match by category name alone.

The displayed measurement constants are fixed in v1. `window_chars` is null for unit descriptions
or a positive integer selected for the task. A change requires recollecting both sides; there is no
universal recommended window length. Preserve raw bytes and character offsets, including CRLF;
do not normalize Unicode, case or simplified/traditional characters implicitly.

Counts use all nonwhitespace characters including punctuation. Within a feature, connected
overlapping matches are merged; separate features are never added into a total problem score.
Match on the whole unit, assigning crossing matches by start position. Nonoverlapping windows
contain the specified number of nonwhite characters and never cross units. A short tail is partial:
keep its counts and positions, but exclude it from full-window distributions. Include zero windows.
No punctuation-protection span changes this counting denominator.

## Commands and semantic labels

```sh
python3 <auditor>/scripts/style_reference.py collect \
  --source-root <corpus> --manifest corpus.json --features features.json \
  --output reference-evidence.json --template-output reference-labels.json

python3 <auditor>/scripts/style_reference.py build \
  --source-root <corpus> --evidence reference-evidence.json \
  --annotations reference-labels.json --output reference.json

python3 <auditor>/scripts/style_reference.py collect \
  --source-root <project> --manifest target.json --features features.json \
  --output target-evidence.json --template-output target-labels.json

python3 <auditor>/scripts/style_reference.py compare \
  --source-root <project> --evidence target-evidence.json \
  --reference reference.json --annotations target-labels.json --output comparison.json
```

Replace placeholder paths; JSON paths are explicit. `--output` can be omitted for stdout.
`--template-output` and `--annotations` are optional for surface-only analysis. Fill the generated
template with `reviewer` (agent/reviewer and version context), and for each semantic hit a boolean
`applies` plus a substantive `reason`; null means unresolved. Preserve evidence/feature IDs.
Surface hits are not classified or subtracted. Retaining a semantic use means `applies: true`.

Missing/null labels leave that feature's count unknown, with confirmed counts, raw surface counts
and unresolved IDs visible. Other complete features remain usable. Sampling labels may assess
reliability, but cannot produce exact semantic totals. Prefer precise phrase features or a smaller
declared corpus over making large ambiguous single-character annotation a mandatory prerequisite.

Build/compare reread their own source root and reject stale or modified evidence. Comparison uses
a frozen reference snapshot offline; it does not claim that original reference files are still
current. Pin `reference_id` in the task context, and verify originals when rebuilding or refreshing
a reference. Hashes detect version changes, not incorrect interpretation or malicious re-signing.
Targets and their edits never update the reference automatically.

## Optional calibrated advisory policy

Without `--policy`, build produces `state: descriptive`: full measurements and empirical positions,
with no automatic review candidates. Agent interpretation can still find a concrete reading issue.

A policy supplied to build contains `schema_version: 1`, the exact `feature_sha256`, `parameters`,
and `calibration`. Required parameters are positive integers `min_partitions`, `min_windows`,
`min_feature_count`, `min_feature_partitions`, a finite `upper_quantile` in (0.5, 1], and a positive
finite `min_extra_count`. The first two require at least two: an implementation eligibility floor,
not an assertion that two samples establish a reliable literary distribution.

The calibration record contains the source `evidence_id`, `annotations_sha256` (hash of null if
none), `parameter_sha256`, all calibration `unit_ids` exactly once, and a substantive `assessment`
of observed reminders and unnecessary alerts. SHA-256 uses canonical JSON: UTF-8,
`ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`. A small Python command can compute
these hashes; do not invent hash strings. Calibration requires at least two distinct partitions.
Read its texts and compare candidate settings before recording that assessment; holdout remains
unseen. Recollect and reassess after changing measurement or feature definitions.

The tool recomputes calibration window results and binds the assessment to exact data, labels and
parameters. It does not verify the literary truth of that assessment. `calibrated` means the record
is present and version-consistent; eligibility is checked separately for every feature/group.

Reference summaries are separate for each source group and register. Multiple source groups
require `compare --reference-group <group>`; never silently average authors. An incomplete or
unsupported group, insufficient calibration coverage or zero observed reference use cannot
generate automatic candidates. A target language/text-type mismatch is an error; a register
mismatch is recorded with no comparable baseline. A short target retains counts without being
extrapolated into a chapter failure.

For an eligible full window, a candidate requires both a rate above the reference upper quantile
and an excess count at least `min_extra_count` over that quantile's expected count. Quantiles use
linear interpolation at `(n-1)*q`. Empirical percentile uses strict-less counts plus half of ties.
These are descriptive editing cues, not p-values, confidence bounds or multiple-testing claims.
Low frequency never requests filler; reference zero means “not observed in this reference”.

## Report interpretation and integration

Comparison returns `measurement_status: complete|partial`, per-unit/feature comparisons, zero-
inclusive window rates, source positions, qualification reasons and `review_candidates`. Successful
exit 0 means a valid report was produced, including valid reports with insufficient data; it never
means prose PASS. Invalid/stale inputs and I/O errors return 2 without a fallback reference.
`--max-results` limits the candidate summary only; `candidate_total` and `truncated` disclose the
limit, while all measured windows and occurrences remain in the report.

Present the expression, scope, count/denominator, applicable reference, locations, and contextual
judgment. Merge repeated pointers to the same issue. Valid outcomes include justified retention,
local revision suggestion, scope mismatch and insufficient evidence. Statistical departure alone
can finish as a retained observation; it does not create an obligation to converge on a quota.

Confirmed language defects follow existing P2/prose_lint routing; optional preferences remain P3.
A suspected issue can enter the existing risks record. No new CI check or gate is introduced.
An explicitly requested comparison still needs an honest completion/gap report. Incomplete
measurement is distinct from a completed measurement that cannot support an inference.

For drafting, distill applicable evidence into a short wording brief with examples and source IDs.
Keep the full machine report as an audit artifact, rather than copying all zero rows and repeated
statistics into the writing prompt. Include only relevant observations, their count/denominator,
locations and material limitations; if comparison adds no useful guidance, say so and stop there.
Do not fill rare-word quotas, copy entire reference passages or make every character share one
frequency profile. Keep planned events, information, certainty and character voice intact. After
an actual edit use the same frozen reference version, recollect target evidence, inspect the real
diff and perform existing semantic regression. No distribution improvement can waive that check.
