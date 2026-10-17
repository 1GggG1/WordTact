# Novel CI — Workflow: Project Setup

> Loaded during: initialization phase.
> Depends on: `conventions.md`, `state-layout.md`.

---

## 1. Three initialization modes

### Mode 1: Full (interview-driven)

Build each state object through structured interviews, one object per round:

1. **project_brief** → 2. **world_bible** → 3. **main characters** (one at a time) → 4. **lockfile skeleton**

Each round: ask questions → user answers → write to file → confirm → next object.

### Mode 2: Lite (minimum viable start)

Create only the lite minimum set per `state-layout.md` §2:
- `project-brief.yaml`: only `genre.primary`, `narrative_mode.pov`, `tone.primary`, `core_premise`.
- `characters/*.yaml`: only `external_goal`, `voice.diction`, `must_not` for initially known characters.
- `lockfile.yaml`: full-skeleton (all keys present, content empty).
- `world-bible.yaml`: may be absent.

Declare at the end: remaining fields will be filled incrementally as writing confirms them. See `state-layout.md` §5.

### Mode 3: Cold-start from existing draft

When the user already has written chapters and wants to adopt the CI workflow:

1. **Read** the existing manuscript chapters.
2. **Reverse-extract** draft versions of `project_brief`, `world_bible`, character profiles, and `lockfile` (confirmed_events, character_states, open_threads).
3. **Present each extracted object as a proposal** — the user must confirm every entry before it is written to canon.
4. **Mark uncertain extractions explicitly** ("从第 X 章推断，需确认").
5. **Iron rule:** Nothing enters canon without user confirmation. LLM-proposed inferences must be labeled as proposals, not facts.

---

## 2. Interview questions (Full mode)

Ask one object's questions at a time. Each question maps to a schema field.

### project_brief

1. 这部小说叫什么名字？（`title`）
2. 核心类型是什么？有没有次要类型？（`genre.primary` / `genre.secondary`）
3. 整体基调是什么？有没有绝对不能出现的调性？（`tone.primary` / `tone.avoid`）
4. 你希望读者读完一章后有什么感受？（`target_reader_experience`）
5. 叙事视角和时态？叙述距离是贴近主角内心还是旁观？（`narrative_mode`）
6. 用一句话概括这部小说的核心设定。（`core_premise`）
7. 核心冲突是什么？（`central_conflict`）
8. 章节长度偏好和节奏偏好？（`structural_preference`）

### world_bible

1. 这个世界有什么不可打破的硬规则？打破后会发生什么？（`hard_rules`）
2. 有什么软规则——通常会遵守但允许变通？（`soft_rules`）
3. 这个世界的能力体系有什么？上限是什么？代价是什么？（`power_limits`）
4. 有什么重要的组织/机构？它们的职能、权限边界、通常行为方式是什么？（`institutions`）
5. 有什么绝对不能出现的世界观操作？（`forbidden_world_moves`）

### Character (per character)

1. 角色名称？拼音 slug？（`character_id` / `display_name`）
2. 角色在故事中的定位？（`role_in_story`）
3. 角色想要什么？（`external_goal`）
4. 角色真正需要什么？（`internal_need`）
5. 角色的默认行动策略——面对问题时的第一反应？（`default_strategy`）
6. 角色恐惧或回避什么？（`fear_or_avoidance`）
7. 角色的道德底线在哪里？（`moral_boundary`）
8. 角色知道什么、不知道什么、可能推断出什么？（`information_access`）
9. 角色的说话方式——用词习惯、节奏、潜台词风格、绝不会说的台词类型？（`voice`）
10. 角色的行为规则——必须做什么、应该做什么、绝不能做什么？（`behavior_rules`）
11. 角色在压力下、困惑时、被逼到角落时的反应？（`stress_response`）
12. 角色与其他关键人物的关系模式？（`relationship_dynamics`）

---

## 3. Iron rules

1. **Setup phase never invents settings.** Every piece of content written to state files MUST come from user input or user-confirmed proposals. LLM suggestions MUST be labeled as proposals and require user confirmation before writing.
2. **Character IDs are permanent.** Once a `character_id` (pinyin slug) is created, it is never changed. The `display_name` may be refined.
3. **Lockfile starts as skeleton.** In full and lite modes, `lockfile.yaml` is created with all schema keys present and content fields empty. Content is filled incrementally by `workflow-state-update`.
4. **One object per round in full mode.** Don't bombard the user with all questions at once.

---

## 4. Completion checklist

After setup, verify:

- [ ] Directory structure matches `state-layout.md` §1.
- [ ] `lockfile.yaml` has all top-level keys from the schema, even if values are empty.
- [ ] Every created character has a `character_id` (ASCII pinyin slug).
- [ ] No invented settings exist without user confirmation.
- [ ] Lite mode: user is informed which fields remain to be filled and how incremental completion works (`state-layout.md` §5).

---

## 5. Mode selection guide

How to choose the right initialization mode:

| User's situation | Recommended mode | Rationale |
|-----------------|-----------------|-----------|
| New project, wants full preparation | Full | Builds complete state foundation before first draft |
| New project, wants to start writing immediately | Lite | Minimum viable state; thicken as you write |
| Has existing chapters (any length) | Cold-start | Reverse-extract from existing text; don't discard written work |
| Has existing chapters + wants to keep writing | Cold-start then Lite | Extract what's confirmed, mark gaps for incremental fill |

If uncertain, default to **Lite** for new projects and **Cold-start** for projects with existing manuscript. Full mode can always be reached incrementally from Lite.

---

## 6. Common cold-start pitfalls

When reverse-extracting from existing drafts:

1. **Don't assume character knowledge from narration.** If the narrator says "角色 A 不知道的是……", that tells you what A *doesn't* know — but the narration itself may be omniscient. Extract `information_access` only from what the character directly demonstrates knowing.
2. **Don't invent character motivations not in the text.** If the draft shows a character acting but never explains why, mark `internal_need` and `default_strategy` as "待补充" — don't infer.
3. **Timeline gaps are OK.** If chapters skip days/weeks, record `timeline_position` as best-guess with "approx" marker. Exact dating can be refined later.
4. **Watch for early-installment weirdness.** First chapters often contain worldbuilding the author later revised. Flag contradictions between early and late chapters — the author decides which version is canon.
5. **Extract lockfile events in chronological order.** Read all chapters before writing any lockfile entry. A chapter 3 reveal may retroactively change how chapter 1 events should be recorded.
