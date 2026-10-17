# Novel CI — Conventions

> Canonical source: `design/novel-ci/contracts.md` §1–§6, §10.
> This file is the terminology and format baseline for ALL other novel-ci reference files.

---

## 1. Glossary & scene lifecycle

| Term | Definition |
|------|-----------|
| canon | Confirmed facts that later scenes must respect (lockfile + bibles) |
| spec | A scene's writing specification = `scene_card` |
| draft | The scene's prose body; the single editable manuscript file |
| patch | A local replacement applied to a draft, with metadata |
| regression | Post-patch check: "original problem fixed AND no new problems introduced" |
| watchlist | Items deposited from RISK findings; mandatory review in the next scene's review |

Scene lifecycle:

```
planned → card_confirmed → drafted → under_review → patching → accepted
                                        │
                                        └→ blocked (P0 unresolved / loop exceeded)
```

---

## 2. Severity system P0–P3

| Level | Definition | Action | Modification authority |
|-------|-----------|--------|------------------------|
| **P0** | Breaks canon, character, causality, or world rules | Must fix; blocks next scene | Full rewrite permitted, but must explain why local patch insufficient; full retest after rewrite |
| **P1** | Scene function, conflict, pacing, consequence, or emotional turn insufficient | Must fix | Local restructure; max 3 patches per round; retest related modules + regression |
| **P2** | Sentence-level, paragraph-level, language, action-carrying, AI-tells | Needs polish | Punctuation / word / sentence / short-paragraph level only; must NOT alter plot facts, character motivation, information access, event outcomes, or world rules |
| **P3** | Flavor, density, aesthetic preference | **Default: don't touch**; only when user explicitly requests | Minimal optional adjustment |

Three iron rules for severity judgment:

1. **Judge by what is broken, not by word count.** One word leaking information-access = P0. An entire paragraph being flat = P1.
2. **P3 is the defense against over-editing.** Treating P3 as P1 is a violation — over-edited text feels fake largely because of this.
3. **Language issues default to P2.** Upgrade only when the language error causes factual or information-access errors (becomes P0; `type` still tags the source).

---

## 3. Test output protocol

Each logical test module outputs one independent result block:

```yaml
<module>_tests_result:
  status: PASS | FAIL | RISK
  failures: []
  risks: []
```

- `FAIL` = at least one confirmed failure with evidence.
- `RISK` = suspicious items only; nothing confirmed.
- `PASS` = neither failures nor risks.

**Forbidden output:** any unlocatable, unactionable evaluation ("basically OK", "overall good", "could be stronger").

### Failure entry format (system-wide uniform)

```yaml
- severity: P0 | P1 | P2 | P3
  type: ""            # from §3.1 type enum
  location:
    anchor: ""        # verbatim quote from draft, ≤30 characters
    para: 0           # paragraph number, 1-indexed
  issue: ""           # why it failed, one sentence, specific
  evidence: ""        # citation: specific field from lockfile/bible/card, or prior-scene fact
  required_fix: ""    # fix direction (NOT replacement text; replacement text belongs to patch phase)
```

### Risk entry format

```yaml
- type: ""
  location: {anchor: "", para: 0}
  issue: ""
  watch: ""           # what to observe in the next scene. Written to lockfile.watchlist on ACCEPTED
```

### §3.1 failure type enum

`canon_conflict` `continuity_break` `unauthorized_knowledge` `character_ooc` `voice_drift`
`scene_function_failure` `causality_break` `conflict_deficit` `flat_emotion`
`missing_consequence` `genre_breach` `prose_lint` `unauthorized_canon` `reader_redundancy`

---

## 4. Patch protocol

### patch_note format (appended to `*.patches.md`)

```markdown
## Patch <scene_id>-p<N>
- Level: P1
- Type: scene_function_failure
- Original location: > verbatim quote 1–3 sentences
- Problem: <the failure from review_report>
- Fix intent: what to fix, what NOT to touch
- Replacement: > new fragment
- Self-check: changed confirmed facts? No / changed character motivation? No / changed information access? No / fixed original problem? Yes / needs lockfile update? Yes|No
```

### patch_plan (plan first; execute only after interaction-point confirmation)

```yaml
patch_plan:
  scene_id: ""
  round: 1
  patches:
    - patch_id: ""         # <scene_id>-p<N>
      severity: ""
      failure_type: ""
      target: {anchor: "", para: 0}
      fix_strategy: ""
      estimated_scope: ""  # punctuation | word | sentence | short-paragraph | segment-restructure
      risks: []
  full_rewrite_required: false
  reason_if_full_rewrite: ""
```

### Execution rules

1. Only fix failures named in `review_report`. Fixing unnamed problems = violation.
2. Single-round P1 patches ≤ 3. P2 patches use the smallest level that works (punctuation < word < sentence < short-paragraph).
3. Patch outputs a fragment replacement, never the full draft.
4. **Loop cap:** Same-scene patch→regression loop max 2 rounds. After round 2, if still NEEDS_MORE_PATCH → scene is `blocked`, return to planning for a new `scene_card`.
5. P0 full rewrite does NOT consume a patch round, but max 1 full rewrite per scene. A second P0 → `blocked` + return to planning.

---

## 5. Gate table (Gate A–E)

| Gate | Location | Pass condition | On failure |
|------|----------|---------------|------------|
| **A** Card Gate | After scene_card generation | User confirms (auto mode: passes self-check checklist) | Revise card, resubmit |
| **B** Review Gate | After review_report generation | Required checks complete on final hashes, then branch by highest severity: P0→rewrite line; P1→patch line; P2-only→lint line; P3-only or all PASS→ACCEPTED | Enter corresponding branch |
| **C** Regression Gate | After regression_check | `result.status: ACCEPTED` | NEEDS_VERIFICATION → finish checks without a repair round; NEEDS_MORE_PATCH (≤2 rounds) → back to patch; exceeded or BLOCKED → back to planning |
| **D** State Gate | Before writing lockfile | Scene status = accepted; state_update contains only confirmed facts from the draft | Reject write |
| **E** Chapter Gate | Chapter end | chapter integration tests complete on final hashes, no FAIL | Locate problem scene, return to its review/patch or planning |

**Hard rule:** P0 or P1 not cleared through Gate B/C → do NOT proceed to next scene. Gate D not passed → do NOT update canon.

---

## 6. Interaction points & auto mode

| Interaction point | Default (interactive) | Auto mode ("continuous writing") |
|-------------------|----------------------|----------------------------------|
| Gate A card confirmation | Stop, wait for user | Auto-pass if self-check passes |
| P0 rewrite plan | Stop, wait for user | **Still stop** (P0 always needs human confirmation) |
| P1 patch_plan | Stop, wait for user | Auto-execute; patch_note archived |
| Gate E chapter report | Stop, present report | Stop, present report |

Mode is detected from user utterance (e.g. "write the next two scenes back to back" → auto). SKILL.md declares current mode.

---

## 7. Shared language verification and fallback

Read the single canonical language body in sibling expander and the auditor language-tools
contract. If a sibling cannot be invoked, the current executor performs these checks directly.
Do not maintain a shortened second ruleset. Missing required checks produce NEEDS_VERIFICATION.

## 8. Severity is not verification completeness

P0/P1 protect canon and scene function; confirmed P2 language defects need repair; P3 preferences
remain optional. Frequency triggers require context and a resolution, not automatic deletion.
Do not raise thresholds to make a candidate pass. Author retention is localized and visible in
actual counts. Required RISK/SKIPPED or stale evidence stops acceptance until verified, without
consuming a repair round. Optional non-required risks still enter watchlist.

## 9. Naming & format conventions

- `scene_id`: `ch<NNN>-s<SS>` (zero-padded). `event_id`: `ev-<increment>`. `thread_id`: `th-<increment>`. `watch_id`: `w-<increment>`. `patch_id`: `<scene_id>-p<N>`.
- `character_id`: ASCII pinyin slug, never changed after creation. Display name goes in `display_name`.
- YAML: English keys, Chinese values. `anchor` fields must be verbatim quotes.
- Review files: overwrite (keep only latest). Patches files: append (keep full history).

Existing explicit authorization satisfies the corresponding interaction point within its scope; do not ask again merely because a skill names a confirmation step. New creative decisions outside that scope still require author input.
