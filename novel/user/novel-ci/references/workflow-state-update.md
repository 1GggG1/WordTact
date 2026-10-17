# Novel CI — Workflow: State Update

> Loaded during: state-update phase (after scene ACCEPTED).
> Depends on: `conventions.md` §2–§5, `state-layout.md` §3.4.
> Related: `test-catalog.md` §C5 (consequence checklist — reverse reference for state extraction).
> Owner of: `state_update` schema (contracts §8.9).

---

## 1. Input

- Accepted `draft` (scene status = `accepted`).
- Corresponding `review_report` (specifically `risks` array, for watchlist seeding).
- Current `canon_lockfile` (the lockfile before this scene).

Gate D precondition: scene status MUST be `accepted`. Non-accepted scenes arriving here = reject immediately.

---

## 2. state_update schema

```yaml
state_update:
  scene_id: ""
  confirmed_events: []
  character_state_changes:
    - {character_id: "", before: "", after: "", reason: ""}
  relationship_changes:
    - {characters: [], change: "", evidence: ""}
  world_state_changes:
    - {entity: "", new_awareness: "", new_action: ""}
  resource_changes:
    - {character_id: "", gained: [], lost: [], consumed: []}
  new_constraints: []
  open_threads_added: []
  open_threads_updated:
    - {thread_id: "", new_status: ""}
  consequences_to_track:
    - {source_event: "", expected_followup: "", urgency: ""}
  watchlist_changes:
    - {watch_id: "", action: add|clear|renew, issue: "", watch: ""}
```

---

## 3. Generation procedure

### Step 1: Extract consequences (ten-question checklist)

Use the consequence checklist from `test-catalog.md` §C5. For each question, check the accepted draft:

1. 谁知道了这件事？
2. 谁误解了这件事？
3. 谁被迫行动？
4. 哪个组织/家庭/团体/敌人/盟友需要记录此事？
5. 什么资源被消耗？
6. 什么关系被改变？
7. 什么边界被越过？
8. 什么风险被提高？
9. 什么伏笔被打开？
10. 下一场为什么不能回到原状？

Answers become `confirmed_events`, `character_state_changes`, `relationship_changes`, `world_state_changes`, `resource_changes`, `new_constraints`, `open_threads_added`, `consequences_to_track`.

### Step 2: Fill state_update

Populate each section of `state_update` from the draft's confirmed content. Every entry must be traceable to a specific passage in the draft.

### Step 3: Present diff (before/after)

Present the lockfile changes as a **diff** (before → after) for each modified section:

- `confirmed_events`: new entries only.
- `character_states`: per-character before/after for `location`, `physical_state`, `emotional_state`, `legal_or_social_status`, `resources`, `constraints`, `current_beliefs`, `false_beliefs`.
- `world_state`: changed `institutions`, `public_pressure`, `resource_changes`.
- `open_threads`: added + updated.
- `unresolved_consequences`: added.
- `watchlist`: added + cleared + renewed.

### Step 4: Apply write

Write the diff to `lockfile.yaml`. `confirmed_events` must be appended in time order.

---

## 4. Watchlist maintenance

| Action | Trigger |
|--------|---------|
| `add` | This scene's `review_report.risks` entries → new watchlist items with `watch_id: w-<increment>`, `status: open` |
| `clear` | Previous scene's open watchlist items that have been verified resolved in this scene → `status: cleared` |
| `renew` | Previous scene's open watchlist items that remain unverified or re-occur → keep `status: open`, append note |

Watchlist is mandatory-checked at the start of the next scene's review (`workflow-review.md`).

---

## 5. Synchronization

- Update `arc.yaml`: set this scene's `status: accepted`.
- `confirmed_events` entries must maintain chronological order within the array — new events appended at the end.

---

## 6. Iron rule

**Only record what the draft has confirmed as having happened.** Author plans, speculation, likelihoods, "probably will happen next" — these do NOT enter canon.

The test: for every entry in `state_update`, point to the specific passage in the draft that confirms it. If you cannot, the entry belongs in planning notes, not in the lockfile.

---

## 7. Lockfile write protocol

When writing to `lockfile.yaml`:

1. **Read-modify-write.** Never regenerate the lockfile from scratch. Read the current file, apply changes as a surgical update.
2. **ID uniqueness.** Verify every new `event_id`, `thread_id`, `watch_id` does not collide with existing IDs. Use increment from the highest existing number.
3. **Field completeness.** Every new entry in `confirmed_events`, `character_states`, `open_threads`, etc. must include ALL fields defined in the schema — empty fields are explicit `""` or `[]`, not omitted.
4. **No retroactive edits.** Never alter a `confirmed_event` from a prior scene. If a later scene reveals new information about a past event, record that as a NEW event (`event_id` distinct) with the revelation, not as a modification of the old event. The old event records what was *known at that time*; the new event records what was *learned later*.
5. **Save after every scene.** Do not batch multiple scenes' updates. Each ACCEPTED scene writes its own `state_update` before the next scene begins. This keeps the lockfile always current.

## 8. Reader index and final hashes

Confirm the accepted review/regression still matches every final source hash. NEEDS_VERIFICATION
cannot enter Gate D. After the existing canon update, commit reviewed reader disclosures under
reader-index.md only for accepted text with verified reading mapping. Disclosures record what
was presented (including inference or a lie), not additional confirmed canon. Pending author
names, intended future events and candidate revisions do not become facts through indexing.
If index commit fails, report the stale/missing coverage and retry from current sources; do not
claim the index updated. Manuscript acceptance is not rolled back merely to conceal index failure.
