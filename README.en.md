# WordTact

[中文：小说完整版与通用轻量版](README.md)

WordTact is a skill for editing English and Chinese text. It works on formulaic phrasing,
nested clauses, overloaded modifiers and inconsistent terminology while preserving the
writer's meaning and voice. Academic editing also checks citations, quantities, attribution
and the strength of claims.

The skill lives in [general/wordtact/](general/wordtact/SKILL.md). It works directly
with the text you provide and does not need Python or a writing-project setup.

## Use it

Copy the entire `general/wordtact/` directory into your agent tool's skill directory.
Keep `SKILL.md`, `references/`, `LICENSE` and `THIRD_PARTY_NOTICES.md` together. You can also point the
agent to the entrypoint:

> Use general/wordtact/SKILL.md to edit this paragraph for clarity. Preserve the house
> style, every substantive claim and its attribution.

> Polish this academic passage. Keep the citations, numerical bounds and degree of
> uncertainty. Use only the main agent; skip independent review.

For a longer document, specify the section to edit and provide any relevant style sample
or terminology list. The skill checks surrounding passages when needed. It returns the
edited text, or findings and suggested changes if you ask for a review.

The main agent offers one independent reviewer, enabled by default. Decline when asked,
or request a main-agent-only edit, to avoid the extra call. It also works without a reviewer
when the host does not support one.

## Why I use it

Many changes came from problems I encountered while writing and revising: terminology
shifting between drafts, sentences that only make sense after a second reading, and edits
that make the prose smoother but change what it says. I find the workflow more useful than
Humanizer's raw output, particularly in my Chinese writing, so I am sharing it here.

My English experience is limited. Beyond the tests, I have used it to write a few papers for
low-tier conferences with EI-indexed proceedings.
I prefer the results to Humanizer's raw output, but that is a personal judgment from a small
sample. I cannot promise it will work well for your writing.

## Benchmark

The general editing test has three Chinese tasks and three English academic passages from
[IteraTeR](https://huggingface.co/datasets/wanyu/IteraTeR_human_sent). The Chinese tasks are
original. The repository also has three Chinese fiction tasks, two inspired by
[EQ-Bench Creative Writing](https://github.com/EQ-bench/creative-writing-bench).

Luna and Terra were configured for max reasoning and standard processing, with three runs
per task and Astra as the evaluator. Results are **wins / ties / losses** for overall
usability against the same model used without a task skill or with Humanizer.

| Tasks | Model | No task skill | Humanizer |
|---|---|---:|---:|
| All six general tasks, 18 comparisons | GPT-6 Luna | 6 / 10 / 2 | 6 / 8 / 4 |
| All six general tasks, 18 comparisons | GPT-5.6 Terra | 7 / 10 / 1 | 3 / 13 / 2 |
| Three English tasks only, 9 comparisons | GPT-6 Luna | 3 / 6 / 0 | 3 / 4 / 2 |
| Three English tasks only, 9 comparisons | GPT-5.6 Terra | 2 / 6 / 1 | 1 / 7 / 1 |

Gains over Humanizer are limited, with many ties. These are
first-pass results; they do not measure an ongoing revision workflow. The
[full report](benchmarks/nine-case/results/2026-10-16/REPORT.md) contains the texts, scores
and evaluation method.

## Development

Use Python 3.10+ to run the development tests from the repository root:

```sh
python3 -m unittest discover -s general/tests
python3 -m unittest discover -s benchmarks/nine-case/tests
```

The tests check packaging, resource links and the benchmark runner. The skill itself does
not need Python.

## License and credits

This project uses the [MIT License](LICENSE). Third-party materials retain their own licenses;
benchmark sources and terms are listed in [SOURCES.md](benchmarks/nine-case/SOURCES.md).

The pattern guidance adapts [Humanizer-zh](https://github.com/op7418/Humanizer-zh) and
[Humanizer](https://github.com/blader/humanizer).
[Third-party notices](general/wordtact/THIRD_PARTY_NOTICES.md) include the upstream licenses.

## Chinese fiction

[Zhanghui (章回)](novel/README.md) is the other skill package in this repository. It supports
planning, drafting, review and continuity work for Chinese fiction. It does not cover English
novel writing; WordTact can be used on its own.

This README was written and revised by Codex from the project maintainer's instructions:
model `gpt-6-astra`, effort `max`, speed tier `ultrafast`. First-person accounts and opinions
are the maintainer's.
