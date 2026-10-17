# Novel CI — Checks: Canon, Continuity, Information

> Loaded by: `workflow-review.md` (first cluster).
> Required context: `canon_lockfile` + `world_bible` (per blueprint §5.1).
> Modules: canon_tests, continuity_tests, information_tests.
> Test content source: `test-catalog.md` §A1–A3.

---

Apply the shared [evidence boundaries](project-context.md#evidence-boundaries-in-writing-and-review)
in all three modules. 正典相容与正文依据分别判断；大纲、后台记忆和作者解释不能补作正文中
已经发生的信息传递或状态转换。叙述者、人物与读者的信息范围分别核对；按已建立的叙事
方式保留可理解的倒叙、全知叙述、合理省略与有意悬念。

## Module 1: canon_tests（正典一致性）

### Purpose

检查 draft 是否违反已确认的正典事实（lockfile + world_bible）。这是最硬的约束——任何违反都是 P0。

### Test items

1. 是否违反 world_bible 的硬规则？
2. 是否违反 canon_lockfile 的已确认事件？
3. 是否错误改变角色状态？
4. 是否错误改变物品、资源、伤势、位置？
5. 是否错误改变组织权限或世界机制？
6. 是否提前触发尚未触发的事件？
7. 是否把未确认内容写成已确认事实？
8. 是否引入未授权的新设定？（`type: unauthorized_canon`）

### Severity guide

- **P0**: 违反硬规则；能力边界被临时改写；组织权限写错；物品/伤势/身份/关系状态与 lockfile 冲突；时间线冲突；前文明确禁止的情节被写入；擅自新增设定。
- **P1**: 软规则偏离但有合理上下文可解释（降级为 risk 更常见）。
- **RISK**: 疑似偏离但 lockfile 未明确覆盖该情况。

### Example FAIL output

```yaml
canon_tests_result:
  status: FAIL
  failures:
    - severity: P0
      type: canon_conflict
      location: {anchor: "他从怀里掏出那枚已经用掉的令牌", para: 5}
      issue: "lockfile 记录该令牌于第 2 章已被消耗（resource: 令牌，status: consumed），本场景重新出现。"
      evidence: "lockfile.character_states[角色 A].resources 中无此令牌；confirmed_events 记录 ev-003 令牌被销毁。"
      required_fix: "删除令牌相关描写，或用其他符合 lockfile 状态的方式达成该情节目的。"
  risks: []
```

---

## Module 2: continuity_tests（连续性）

### Purpose

检查本场景与前文的物理/逻辑接续。统计上这是长篇最容易翻车的模块——不是因为复杂，而是因为作者（或 LLM）容易忘记上一场结束时角色的具体状态。

### Test items

1. 当前时间是否接续上一场？
2. 当前地点是否合理接续？
3. 角色身体状态是否连续？
4. 角色情绪状态是否有过渡？
5. 角色资源是否正确继承？
6. 角色关系是否正确继承？
7. 上一场留下的后果是否没有被清空？
8. 本场是否错误跳过必要反应？
9. lockfile.watchlist 中 status=open 的条目是否逐一核查？（D7 强制项）

### High-frequency failure patterns（check these first）

- 受伤角色下一场没事。
- 被追捕者随便出门。
- 已曝光身份没人知道。
- 用掉的资源又出现。
- 上一场大事件世界毫无反应。

### Severity guide

- **P0**: 故事时间或事件先后存在已确认的硬矛盾；角色状态与 lockfile 硬冲突；上一场重大后果被完全忽略。先按正文线索还原故事时间，合法的倒叙或预叙不属此类。
- **P1**: 情绪过渡缺失；资源继承有轻微差错；必要反应被跳过。
- **RISK**: 接续合理但过渡略快；watchlist 项未完全排除但场景上下文可解释。

### Example FAIL output

```yaml
continuity_tests_result:
  status: FAIL
  failures:
    - severity: P1
      type: continuity_break
      location: {anchor: "角色 A 从床上翻身坐起，精神饱满", para: 1}
      issue: "上一场结尾角色 A 肋骨骨折且整夜未眠，本场开头无伤病过渡。"
      evidence: "lockfile.character_states[角色 A].physical_state: '肋骨骨裂，行动受限'；上一场 exit_state.changed_facts 含'角色 A 受伤'。"
      required_fix: "添加伤病状态的过渡描写，或在 entry_state 中明确时间跨度已允许恢复。"
  risks: []
```

---

## Module 3: information_tests（信息权限）

### Purpose

检查每个角色是否只知道自己有渠道知道的信息。这是叙事可信度的基石——一次信息权限泄漏就足以破坏读者信任。

### Test items

1. 每个角色是否只知道自己有渠道知道的信息？
2. 是否有人说出作者视角才知道的内容？
3. 是否有人过早推理出缺乏证据的真相？
4. 是否有人忘记自己已经知道的信息？
5. 是否有人错误误解或错误地不误解？
6. 信息传播路径是否存在？
7. 秘密是否被不合理泄露？

### Cross-module linkage with character tests

Character test item 7（"角色是否掌握了不该掌握的信息？"）的判定归属本模块：如果角色掌握未授权信息 → `type: unauthorized_knowledge`，记录在 information_tests 而不是 character tests。Character tests 只记录角色行为层面的异常，信息权限问题统一在本模块汇总。

### Severity guide

- **P0**: 角色知道 lockfile 明确记录其 `does_not_know` 的信息；秘密被无传播路径地泄露。
- **P1**: 角色推理跳跃过大但 lockfile 未明确禁止其知道；信息传播路径存在但有略过快的嫌疑。
- **RISK**: 信息传递方式在上下文中可能合理但不够显式。

### Example FAIL output

```yaml
information_tests_result:
  status: FAIL
  failures:
    - severity: P0
      type: unauthorized_knowledge
      location: {anchor: "你是不是在密室里藏了那封信", para: 12}
      issue: "角色 B 直接引用密室信件，但 lockfile 记录角色 B 不知道信件存在。"
      evidence: "lockfile.character_states[角色 B].current_beliefs 不含信件相关；character_profile[角色 B].information_access.does_not_know 含'密室内发生的事件'。"
      required_fix: "删除角色 B 对信件的认知，或补足信息传播路径（需确认路径在 canon 内合法）。"
  risks: []
```

## Reader and character knowledge

Use reader-index.md to retrieve only valid disclosures before the target unit, then read the
original anchors. A reader knowing a fact does not give every character knowledge of it. Record
hypotheses, lies and unreliable judgments as such; they are not confirmed canon. Repetition with
no contradiction is reviewed as reader_redundancy by narrative_delivery, not ignored here.
