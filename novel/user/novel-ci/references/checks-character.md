# Novel CI — Checks: Character

> Loaded by: `workflow-review.md` (second cluster).
> Required context: `character_profile` files for all appearing characters (per blueprint §5.1).
> Modules: general_character_tests, character_specific_tests.
> Test content source: `test-catalog.md` §B1–B2.

---

## Module 1: general_character_tests（所有出场角色通用）

### Purpose

检查所有出场角色的行为是否符合角色档案（character_profile）的基本约束。此模块侧重"角色作为个体是否自洽"，不检测信息权限问题（归 information 模块）。

### Test items

1. 角色是否按照自己的 default_strategy 行动？
2. 角色是否违反自己的 moral_boundary？
3. 角色是否因为剧情需要突然变聪明？
4. 角色是否因为剧情需要突然变蠢？
5. 角色是否说了只有作者才会说的话？
6. 角色是否承担了不属于自己的主题表达？
7. 角色是否掌握了不该掌握的信息？（联动 information 模块——failure 归 information，本模块只记录指向）
8. 角色声音是否能与其他角色区分？（`type: voice_drift`）
9. 角色在压力下的反应是否符合 stress_response？

### Severity guide

- **P0**: 违反 `must_not`；越过 `moral_boundary`；严重 OOC 破坏剧情因果。
- **P1**: `default_strategy` 轻微偏移；stress_response 不符合档案但可通过上下文解释；voice_drift。
- **RISK**: 行为在边缘，档案未明确覆盖该情境。

### Example FAIL output

```yaml
general_character_tests_result:
  status: FAIL
  failures:
    - severity: P0
      type: character_ooc
      location: {anchor: "角色 A 毫不犹豫地出卖了同伴的位置", para: 23}
      issue: "角色 A 的 moral_boundary 明确记录'绝不背叛同伴'，本场景中无过渡、无内心挣扎即出卖同伴。"
      evidence: "character_profile[角色 A].moral_boundary: '绝不背叛同伴，即使付出个人代价'；behavior_rules.must_not 含'出卖同伴信息'。"
      required_fix: "添加出卖前的内心冲突和被迫理由；或改为角色 A 用假信息误导对方从而保护同伴（符合其 default_strategy）。"
  risks: []
```

---

## Module 2: character_specific_tests（逐角色专属）

### Purpose

为每个出场角色**动态生成**专属测试，基于其 `character_profile` 的完整字段。本模块不能写成固定清单——每个角色的测试条目不同。

### Dynamic test generation

For each appearing character, read their `character_profile` and generate:

```yaml
character_specific_tests:
  character_id: ""     # the character being tested
  tests:
    - 是否保持该角色的默认行动策略？（对照 default_strategy）
    - 是否保持该角色的语言节奏？（对照 voice.rhythm）
    - 是否没有越过该角色的道德边界？（对照 moral_boundary）
    - 是否没有说出 voice.forbidden_lines 类台词？
    - 是否没有让该角色替作者讲道理？
    - 是否没有为推进剧情而失真？
```

Test items 1-6 are the base template. Additionally, for each `behavior_rules.must` / `behavior_rules.must_not`, generate a specific check.

### Stress response verification

When a scene puts a character under pressure (conflict, threat, cornered), verify the character's response matches their `stress_response` profile:

- `under_pressure`: 角色在一般压力下的典型反应。
- `when_confused`: 角色在困惑/信息不足时的典型反应。
- `when_cornered`: 角色在被逼到绝境时的典型反应。

If the scene creates one of these situations but the character's response does not match the profile, flag as RISK (context may justify the deviation) or FAIL (no contextual justification visible).

### Relationship dynamics verification

For each `relationship_dynamics` entry where the paired character also appears in this scene:

- Does the interaction pattern match `default_pattern`?
- Is `tension` level consistent (unless the scene explicitly changes it)?

### Core philosophy

**稳定优先于讨喜。** 角色测试的重点不是"角色是否迷人/有趣/让读者喜欢"，而是"角色是否在自身规则内稳定运行"。一个始终如一但不出彩的角色优于一个时而惊艳时而崩溃的角色。读者对角色 OOC 的敏感度远超对"角色不够讨喜"的敏感度。

### Severity guide

- **P0**: 违反 `voice.forbidden_lines`（该角色绝不该说的话）；违反 `must_not`；为推进剧情而严重失真（如关键决策与其 internal_need 完全矛盾且无解释）。
- **P1**: `voice.rhythm` 偏离；`typical_subtext` 风格不一致；轻微"替作者讲道理"。
- **RISK**: 某句台词在档案边界上；某行为在新情境下看起来偏离但可能合理。

### Example FAIL output

```yaml
character_specific_tests_result:
  status: FAIL
  failures:
    - severity: P0
      type: voice_drift
      location: {anchor: "没关系的，过去的都过去了，我们要向前看", para: 34}
      issue: "角色 C 说出了典型的'原谅与释怀'台词，命中其 voice.forbidden_lines 中的'鸡汤式和解语言'。"
      evidence: "character_profile[角色 C].voice.forbidden_lines: '鸡汤式和解语言 / 道德说教 / 释怀与原谅的劝解句式'。"
      required_fix: "改为符合角色 C 语言风格的反应：不直接表达原谅，而是通过一个具体行动（如默默递东西/转身做事）暗示不追究。"
  risks: []
```

## Unnamed speakers and missing profiles

通用检查覆盖全部出场者，包括没有独立档案的临时人物：指代能否定位、对白能否区分、
身份与场景中的语言是否可信。没有专属 profile 只限制该档案的比对，不免除通用阅读。
不强迫临时人物获得姓名，也不把正式报告、军事对白和口头禅设为永久豁免。
