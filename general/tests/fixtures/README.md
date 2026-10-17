# WordTact behavioral fixtures

These are synthetic editing requests, not real research findings or source quotations.
`inputs.json` contains ten cases shared byte-for-byte by the bare, original-Humanizer and
wordtact conditions. Each case exposes only the request, source, language/mode and any
provided context. It contains no model names, scores, expected wording or evaluation hints.

L01–L08 cover Chinese/English meaning, register and protected document content. L09 and L10
ask for a standalone paragraph using a definition in section 11 of a longer record. The
surrounding records deliberately add retrieval load. These are bounded source-lookup probes,
not proof of whole-book editing or a test of every context position.

`fiction-inputs.json` supplies four identical cases to the pre-change and current novel-rule
conditions. `protocol-inputs.json` supplies four dry-run decision cases for reviewer refusal,
the declared default, absent tools and pending platform approval. The protocol results are
not evidence that a real asynchronous user interaction or a reviewer launch occurred.

Execution: assigned Luna max workers, one final candidate per case, no recursive reviewers.
An independent Astra evaluator receives anonymous candidates and source-grounded criteria,
without condition names or the generator's self-assessment. Keep first outputs even if a
later repair is requested. Do not silently replace them with improved candidates.

The runtime skill is the sibling `wordtact/` directory. These fixtures and tests are
development material; they are not part of that standalone skill or the novel full archive.
