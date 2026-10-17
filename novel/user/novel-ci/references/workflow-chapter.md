# Novel CI — Workflow: Chapter

> Loaded during: chapter-end phase (Gate E).
> Depends on: `conventions.md` §3, §5 Gate E.
> Related: `test-catalog.md` §E1, §E2.

---

## 1. Trigger

When `arc.scene_sequence` shows all scenes as `accepted`, the chapter is complete. Trigger the chapter integration workflow.

## 2. chapter_integration_tests

Run these against the full chapter (all scene drafts + arc). Format per `conventions.md` §3.

> Source: `test-catalog.md` §E1. Semantic mapping preserved.

| # | Test | What to check |
|---|------|---------------|
| 1 | 各场是否有可说明的作用？ | 区分重复任务与有增量的再访；场景功能可以相关。 |
| 2 | 接续和因果是否清楚？ | 读者能否跟随地点、行动、反应与有意留白？ |
| 3 | 节奏是否服务本章目标？ | 允许舒缓、安静和持续压力；不得机械要求峰谷数量。 |
| 4 | 关键变化是否落实？ | 检查计划中适用的发现、选择、关系或理解变化，不强制中段转折。 |
| 5 | 后果是否保留？ | 已发生的重要行动，其适用后果能否在本章或后续追踪？ |
| 6 | 关系与声音是否可信？ | 稳定关系同样可以成立，不要求每章改变关系。 |
| 7 | 信息状态是否清楚？ | 分开读者已知、角色已知、推测、误解与事实。 |
| 8 | 资源、风险和动作状态是否一致？ | 有变化则核对，无变化无需制造。 |
| 9 | 未回收线索是否可追踪？ | 有意悬置与遗漏分开，关联 open_threads。 |
| 10 | 章尾是否完成适合的停顿？ | 保留余味、笑点或过渡，排查无增量的重复收口。 |
| 11 | 本章提供什么阅读价值？ | 行动、体验、人物、理解或铺垫；不能因删除后主线仍通就判废章。 |
| 12 | 是否重复已完成的叙事功能？ | 读取相关前文，区别追更提醒、新听众反应与无增量复述。 |
| 13 | 词频、标点与实际修改是否完成验证？ | 共享语言规则、读者范围和语义回归都绑定本章最终版本。 |

Output each performed test with `status: PASS | FAIL | RISK`. Missing mandatory verification means NEEDS_VERIFICATION, never an inferred PASS. FAIL items use the failure entry format from `conventions.md` §3.

---

## 3. Chapter three questions

Answer these (Chinese prose) and append to `arc.integration_result`:

1. **本章开始时是什么局面？**（引用 arc.opening_state 并对照实际正文验证）
2. **本章让读者经历、理解或见证了什么？**（引用具体位置；不强制不可逆事件）
3. **这些内容怎样接入后文？**（后果、关系、知识、期待或有意停留；列出适用项）

> Source: `test-catalog.md` §E2.

---

## 4. Write integration_result

The schema owner is `workflow-planning.md` §2; do not reproduce or extend it here. Write these
owner-defined fields into `arc.yaml`: `integration_result.status`, `integration_result.failures`,
and all five children of `integration_result.emergent_patterns`. Also append the three-question
answers as a prose note block.

### emergent_patterns discipline

After the integration tests, observe patterns across the completed chapter:

- repeated choices and their costs;
- objects that recur, change, transfer, break, or disappear;
- repeated relationship movements;
- theme questions the text currently raises;
- evidence that contradicts the planned `thematic_pressure`.

This block discovers; it does not decide. Do not announce an object as a symbol, turn a theme into a
thesis, or alter Gate E because a pattern is absent. Only author-confirmed observations may influence
future planning; this workflow does not create a motif ledger.

---

## 5. Gate E: On FAIL

If any integration test FAILs:

1. **Locate** the problem scene(s) from the failure entries.
2. **Recommend** reflow action for each:
   - Scene-level issue (function duplicate, flat emotion, missing consequence) → return to that scene's `review` or `patch`.
   - Arc-level issue (no causal chain, flat rhythm, no chapter-level change) → return to `planning` for chapter re-plan.
3. **Present** to user: which scenes, what failed, recommended action.
4. Only execute revisions within existing authorization. Request a new decision when the proposed re-plan changes established creative choices outside that authorization.

---

## 6. Chapter-end report format (interaction point)

Present to user:

```
## 第 N 章收口报告

### 三问

1. 本章开始时：[局面描述]
2. 阅读所得：[具体位置与作用]
3. 后文接续：[后果、理解或期待]

### 伏笔与线程

| 线程 ID | 状态 | 说明 |
|---------|------|------|
| th-001  | 推进 | ... |
| th-002  | 新增 | ... |

### 下一章可用钩子

- [钩子 1：来自 unresolved_consequences]
- [钩子 2：来自 open_threads]
- [钩子 3：来自 exit_state 未处理的后果]

### 非门禁模式观察

- 反复选择与代价：[观察或“未发现”]
- 物件变化：[观察或“未发现”]
- 关系模式：[观察或“未发现”]
- 主题问题与反例：[观察或“未发现”]
```

---

## 7. Integration test FAIL patterns & diagnosis

Common chapter-level failures and their root causes:

| FAIL pattern | Typical root cause | Fix direction |
|-------------|-------------------|---------------|
| Repeated scene work adds no intended reading value | Earlier work is repeated without new reaction, understanding, payoff or reader need | Compare actual functions and retain useful revisits; compress or re-plan only the redundant work |
| No causal chain across scenes | Each scene was planned in isolation without lockfile continuity | Check each scene's entry_state against prior scene's exit_state |
| Sustained intensity undermines the chapter's intended experience | The reader lacks needed processing, anticipation or meaningful progression | Adjust the specific pacing problem; add a reaction scene only when it has work to do, and preserve purposeful sustained pressure or calm |
| Repeated explanation or conclusion without new function | Previously disclosed content treated as new | Read earlier anchors; compress only the redundant function, preserving new reactions and reader reminders |
| Last scene ends in vague cliffhanger | Scene writer defaulted to formulaic suspense | Rewrite the last scene's final paragraphs to land on a concrete changed fact |

---

## 8. Cross-chapter continuity check

After integration tests pass, run a quick cross-chapter continuity:

1. Does this chapter's `ending_state` supply the correct `opening_state` for the next chapter? (Verify against `arc.yaml` of the next chapter if it exists.)
2. Are `unresolved_consequences` from this chapter carried into the next chapter's planning input?
3. Are any `open_threads` from this chapter referenced in the next chapter's scene_cards?

This is a lightweight verification — it does not generate new failures, it flags things the planner should check before starting the next chapter's scene_cards.

## 9. Reader continuity and final acceptance

Use project-context.md and reader-index.md. Statistical windows cover the chapter and preceding
two units; continuous review normally reads the latest ten published chapters and covers the
whole requested range in overlapping windows. Initial prefix indexing, five newly accepted units,
and content changes to earlier units trigger continuous review. Fewer than five units is a stated
coverage limit. Track who can identify unnamed speakers and what each audience knows.

Index summaries guide retrieval, never replace reading key original passages. When earlier text
changes, re-read the affected suffix. No future disclosures may justify an earlier character's
knowledge. Final chapter verification is punctuation → recount → semantic regression → mapping,
then project acceptance and index commit. A failed or incomplete step keeps the relevant result
FAIL or NEEDS_VERIFICATION; three statistical units do not certify a ten-chapter reading window.
