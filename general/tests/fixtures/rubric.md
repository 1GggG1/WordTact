# Independent evaluation rubric

Evaluate only the supplied request, source text/context and anonymous candidates. Do not
guess which method produced a candidate or prefer a method. These are synthetic fixtures.
The source defines their facts; no external fact checking is needed.

Score each candidate on four separate 1–5 scales:

- **meaning**: preserved referents, negation, necessary/sufficient conditions, scope, quantities,
  chronology/completion, uncertainty, attribution and all distinct source information.
- **voice**: appropriate register and retained writer/character/occasion differences. Neither
  colloquialness nor formalness is inherently better.
- **readability**: resolved actual load, padding or repetition without creating fragments,
  awkward joins or needless paraphrase. An already clear source can legitimately remain.
- **scope**: followed the requested output range and protected formatting, code, data,
  headings, definitions and citations.

5 means no substantive defect identified in this dimension; 4 a small identifiable weakness;
3 a noticeable defect requiring revision; 2 a serious failure; 1 largely unusable. Do not treat
5 as proof of universally perfect prose. A candidate can preserve meaning while still retaining
avoidable padding and therefore score lower on readability. Scores require observed evidence,
not a quota of differences between candidates.

For a defect, give a short exact candidate quote, a short source quote and the reasoning.
Distinguish an actual changed meaning from merely possible stylistic alternatives. Do not
count deletion of a truly redundant restatement as information loss if its meaning remains
fully expressed. In fiction, distinguish the narrator's assertion from a character's mistaken
belief; don't reward turning either into a different statement. Ties are allowed.

Return JSON with `results`: each row has `case_id`, `candidate_id`, `scores` (the four named
integer fields), `findings` (list of `{severity, candidate_quote, source_quote, explanation}`),
and `comment`. For each case, also return `preferences` containing the equally preferred
candidate IDs and a brief reason. A failed hard constraint cannot be offset by smoother style.

Protocol probes are evaluated separately, without pretending they are blind prose comparisons.
Read the provided skill entry and each simulated environment. Return `protocol_results` with
`case_id`, `correct` and `reason`; distinguish stated-default authorization from explicit
consent, and do not waive a pending platform approval or fabricate an independent reviewer.
These probes only test stated decisions, not real UI interaction or real reviewer launches.
