# Novel CI — State Layout

> Canonical source: `design/novel-ci/contracts.md` §7–§9, §8.1–§8.4.
> This file defines the project-state directory contract and state-object schemas.
> It does NOT contain workflow steps, test entries, or scene_card/review/patch schemas.

---

## 1. Project state directory tree

All files below live under `<project>/` (the novel project directory, user-specified). The skill itself contains only methodology.

```text
<project>/
  canon/
    project-brief.yaml
    world-bible.yaml
    characters/<character_id>.yaml     # one file per character
    lockfile.yaml                       # includes timeline_position / open_threads / watchlist
    style/                              # optional
      style-guide.md                    # project prose conventions
      prose-benchmark.md                # prose benchmark samples
      voice-samples.md                  # character voice samples
  manuscript/
    ch<NNN>/
      arc.yaml                          # chapter_arc: plan + progress + integration result
      <NNN>-<SS>.card.yaml
      <NNN>-<SS>.draft.md               # sole prose file; patches applied directly here
      <NNN>-<SS>.review.yaml            # most recent review_report (overwrite)
      <NNN>-<SS>.patches.md             # patch history (append)
```

### Readers & writers

| File | Readers | Writer | Write timing |
|------|---------|--------|-------------|
| project-brief.yaml | All modules (read-only) | workflow-setup | Initialization |
| world-bible.yaml | All modules (read-only) | workflow-setup; workflow-state-update (incremental) | Initialization; scene accepted |
| characters/*.yaml | Review (checks-character) | workflow-setup | Initialization; incremental on first appearance |
| lockfile.yaml | All modules (read-only); workflow-state-update (write) | workflow-state-update | After each scene ACCEPTED (Gate D) |
| arc.yaml | workflow-planning, workflow-chapter | workflow-planning; workflow-chapter (integration_result) | Planning; chapter end |
| *.card.yaml | workflow-draft, workflow-review | workflow-planning | Planning |
| *.draft.md | workflow-draft, workflow-review, workflow-patch, workflow-regression | workflow-draft; workflow-patch | Drafting; patching |
| *.review.yaml | workflow-patch, workflow-regression | workflow-review | Review |
| *.patches.md | workflow-regression | workflow-patch | Each patch applied |

---

## 2. Necessity tiers (lite mode contract, D9)

| File | Full | Lite minimum |
|------|------|-------------|
| project-brief.yaml | All fields | Only `genre.primary`, `narrative_mode.pov`, `tone.primary`, `core_premise` |
| world-bible.yaml | All fields | May be absent; created incrementally when first world rule appears in draft |
| characters/*.yaml | Full profile for every appearing character | Only `external_goal`, `voice.diction`, `must_not` for appearing characters |
| lockfile.yaml | Complete | Empty skeleton (all fields present, content empty); filled incrementally |
| style/ | Optional | May be absent |

**Lite mode rule:** First determine whether the missing state field is needed to verify this
scene's actual claims. An unused optional field is a coverage note, not a required-check `RISK`;
perform the applicable check against the available prose and evidence. If a necessary fact
cannot be verified because the field and supporting evidence are missing, output `RISK` with the
specific missing evidence and `NEEDS_VERIFICATION`, never invent a `FAIL` or `PASS`. Optional
full-mode fields do not need to be populated merely to accept the first lite-mode scene.

---

## 3. State schemas

English keys, Chinese values. Omitted fields are allowed. Lists may be empty.

### 3.1 project_brief (owner: this file)

```yaml
project_brief:
  title: ""                       # 作品标题
  genre: {primary: "", secondary: []}
  tone: {primary: "", avoid: []}
  target_reader_experience: []    # 目标读者体验（如"紧张感""好奇心驱动"等）
  narrative_mode: {pov: "", tense: "", narrator_distance: ""}
  core_premise: ""                # 核心设定一句话
  central_conflict: ""            # 核心冲突
  thematic_pressure: []           # 主题压力方向
  structural_preference: {chapter_length: "", scene_length: "", pacing: ""}
```

### 3.2 world_bible (owner: this file)

```yaml
world_bible:
  hard_rules:
    - {rule: "", consequence_if_broken: ""}
  soft_rules:
    - {rule: "", allowed_variation: ""}
  power_limits:
    - {entity: "", capability: "", limitation: ""}
  institutions:
    - {name: "", function: "", authority_limit: "", usual_behavior: ""}
  forbidden_world_moves: []       # 不允许出现的世界观操作
```

### 3.3 character_profile (owner: this file; one file per character)

```yaml
character_profile:
  character_id: ""                # ASCII pinyin slug, stable forever; display name in display_name
  display_name: ""
  role_in_story: ""
  external_goal: ""               # 角色想要什么（外部目标）
  internal_need: ""               # 角色真正需要什么（内部需求）
  default_strategy: ""            # 默认行动策略
  fear_or_avoidance: ""           # 恐惧/回避
  moral_boundary: ""              # 道德底线
  information_access: {knows: [], does_not_know: [], may_infer: []}
  voice: {diction: "", rhythm: "", typical_subtext: "", forbidden_lines: []}
  behavior_rules: {must: [], should: [], must_not: []}
  stress_response: {under_pressure: "", when_confused: "", when_cornered: ""}
  relationship_dynamics:
    - {with: "", default_pattern: "", tension: ""}
```

### 3.4 canon_lockfile (owner: this file; timeline & open_threads merged in)

```yaml
canon_lockfile:
  current_time: ""                # 当前叙事时间
  current_location: ""            # 当前地点
  timeline_position: ""           # 叙事时间点描述；confirmed_events 保持时间序即隐含时间线
  confirmed_events:
    - {event_id: "", summary: "", participants: [], public_knowledge: "", private_knowledge: ""}
  character_states:
    - character_id: ""
      location: ""
      physical_state: ""
      emotional_state: ""
      legal_or_social_status: ""
      resources: []
      constraints: []
      current_beliefs: []
      false_beliefs: []
  world_state:
    institutions:
      - {name: "", current_awareness: "", current_action: ""}
    public_pressure: ""
    resource_changes: []
  open_threads:
    - {thread_id: "", description: "", introduced_in: "", current_status: "", owner: "", urgency: ""}
  unresolved_consequences:
    - {source_event: "", expected_followup: "", deadline_or_trigger: ""}
  watchlist:                       # D7: RISK destination; mandatory review next scene, then clear or renew
    - {watch_id: "", from_scene: "", issue: "", watch: "", status: open|cleared}
```

---

## 4. Naming conventions

- `scene_id`: `ch<NNN>-s<SS>` (zero-padded, e.g. `ch003-s02`).
- `event_id`: `ev-<increment>`.
- `thread_id`: `th-<increment>`.
- `watch_id`: `w-<increment>`.
- `patch_id`: `<scene_id>-p<N>`.
- `character_id`: ASCII pinyin slug, created once, never changed. Chinese name stored in `display_name`.
- YAML: English keys, Chinese values. `anchor` fields must be verbatim quotes.
- Review files (`*.review.yaml`): overwrite (keep only latest).
- Patches files (`*.patches.md`): append (keep full history).

---

## 5. Incremental completion rules

For projects starting in lite mode, state thickens organically:

- **World rules:** When a world rule first appears in a draft (e.g. a power limitation is demonstrated), add it to `world_bible.yaml` during state_update — only if confirmed in the accepted draft.
- **Character profiles:** When a character first appears, create their `characters/<character_id>.yaml` with at minimum the lite fields (`external_goal`, `voice.diction`, `must_not`). Fill remaining fields incrementally as the draft confirms them.
- **Lockfile:** Starts as empty skeleton. `confirmed_events`, `character_states`, `open_threads`, `unresolved_consequences`, and `watchlist` entries are added only by `state_update` after a scene reaches `accepted`.
- **style/:** Optional at all times. If the user provides style guidance, create the files; otherwise absent is fine.

## 5. Optional shared editorial state

The following state lives in the explicitly selected novel project, never in the skill bundle:

- `agent/audits/language-profile.json`: optional project calibration; schema in sibling auditor's
  language-tools.md. Missing profile uses generic checks plus LLM discovery, not skipped checking.
- `agent/reader-index/index.json`: derived accepted disclosures; sole schema owner reader-index.md.
- A caller-selected audit session: frozen originals, latest accepted text, candidate edits,
  evidence and journal; sole schema owner revision-tools.md.

Existing projects may keep their current manuscript and context layout. These methods do not
require migrating canon, memories or publication scripts. Historical records lacking new fields
stay readable, but absent evidence cannot be interpreted as completed verification.
