# Sources, selection and reuse

This is a small, purpose-built comparison suite, **not an official EQ-Bench or EditEval
leaderboard**. Inputs were selected and frozen before generating any result in this run.
Selection targets the skills' stated tasks rather than a representative sample of all writing.
Three repeated generations measure variability on the same cases; they do not make 27
independent tasks.

## Case provenance

| Case | Source | What was adapted |
|---|---|---|
| F01 | EQ-Bench Creative Writing v3, prompt 2 | The task type: letters across time and distinct voices. Chinese characters, setting, object, brief and wording are original. |
| F02 | Original fixture | A repair-shop scene with distinct speakers, inflated narration and tracked objects. |
| F03 | EQ-Bench Creative Writing v3, prompt 13 | The task type: spatially intelligible action. Chinese scene, actions and wording are original. |
| C01 | Original fixture | A fictitious sensor-study abstract; all numbers and claims are test material, not research findings. |
| C02 | Original fixture | A fictitious workplace notice with explicitly protected Markdown, URL and command. |
| C03 | Original fixture | A target paragraph plus 37 records and an approved style sample; relevant restrictions occur at separated positions. |
| E01 | IteraTeR human sentence test set, row 158, document `2011.10896` | Exact `before_sent`; a local editing request replaces the evaluation prompt. |
| E02 | IteraTeR human sentence test set, row 174, document `2012.15859` | Exact `before_sent`; a local editing request replaces the evaluation prompt. |
| E03 | IteraTeR human sentence test set, row 137, document `2009.06891` | Exact `before_sent`; a local editing request replaces the evaluation prompt. |

Row indices are zero-based. All three English rows have label `clarity` and revision depth 2.
They were deliberately selected from longer clarity passages to exercise technical noun
strings, qualification and information order. They are all academic passages; this suite does
not establish performance on English fiction or everyday English correspondence. C03 contains
about 2,800 Chinese characters of context, not a book-length or model-window-limit stress test.

The English source strings retain the dataset's spacing. The generation and judging packets
do **not** contain the human `after_sent` references. Those references are retained only in
`upstream-references.json` for source verification, not treated as the sole correct rewrite;
some change or remove claims that this suite explicitly asks editors to preserve.

## Pinned upstream material

- [EQ-Bench Creative Writing](https://github.com/EQ-bench/creative-writing-bench), commit
  `c7c3ceef54c40a8ae02dc1c2e1a5e40970fe5c0b`.
  `data/creative_writing_prompts_v3.json`, 76,108 bytes, SHA-256
  `87f79b688261318f9182966aa238403aeaa1022f82ffc3ae4d1fe2a48cf1c412`.
  Only task concepts are adapted; the full prompts are not redistributed here.
- [EditEval](https://github.com/facebookresearch/EditEval), commit
  `013cd20aa73be0016041201454b3fcd7c2250fb4`. Its Hugging Face processor identifies
  `wanyu/IteraTeR_human_sent` and the `before_sent`/`after_sent` fields. This suite does not
  run the official EditEval prompts or metrics. See also the
  [EditEval paper](https://arxiv.org/abs/2209.13331).
- [IteraTeR human sentence dataset](https://huggingface.co/datasets/wanyu/IteraTeR_human_sent),
  revision `e22e0371dac444239b944f9293f5b491d62b73f0`.
  The file named `test.json` is JSON Lines: 364 rows, 294,380 bytes, SHA-256
  `1a30452c33bd5379ff56159016d68ecd7e2669ede1e4ea77244c6e300952e9cb`.
  The dataset card declares Apache-2.0; see the accompanying
  [Apache License](licenses/Apache-2.0.txt). Credits and document identifiers are preserved
  in each case. Only the evaluation request is adapted; source passages are unchanged.

## Comparison controls

- Chinese: [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh), commit
  `f4518a8eab97b8bfebc66a89d34320a89bef6930`.
  `SKILL.md` SHA-256: `95627fd4437d886f98032ccc62d79136e6310f1fc04e354bb86431795ff206df`.
- English: [blader/humanizer](https://github.com/blader/humanizer), commit
  `225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8` (3.1.0).
  `SKILL.md` SHA-256: `0612f1dfb1672b0ea9b97e139bf1f06cabe98d8b27424fe8ff01e1fb4cc99cad`.

Both control skills are MIT-licensed. The runner copies or downloads the pinned `SKILL.md`
and `LICENSE` together, verifies their hashes and keeps the unmodified snapshots outside the
runtime products. F01 is not scored against Humanizer because it is a drafting task.

The project skill snapshots contain the entrypoint and complete applicable resource tree.
Their per-file hashes are in the run's `suite-lock.json`; no skill is rewritten after seeing
this run's outputs. The snapshot's Git base and any working-tree differences are reported
separately from its content hashes.

## Evaluation lineage and limits

The 1–7 anchored quality ratings and order-swapped pair comparisons are inspired by the
[EQ-Bench methodology](https://eqbench.com/about.html#creative-writing-v3), but the dimensions,
correctness ledger, prompts, texts and aggregation here are local choices. There is no
conversion from these results to an EQ-Bench score, EditEval score or population-wide claim.

One evaluator model, GPT-6 Astra, judges both orderings in independent calls. This reduces
one kind of presentation bias but does not provide independent human raters or eliminate
shared model bias. Report both preference dimensions, correctness findings, disagreements,
and failures alongside any quality averages.
