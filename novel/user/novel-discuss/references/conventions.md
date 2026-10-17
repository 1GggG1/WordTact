# Novel Discuss — Conventions

> Canonical source: `design/novel-discuss/contracts.md` §1, §2, §6, §7, §8.
> This file is the terminology and behavioral baseline for novel-discuss.
> State schemas live in `state-layout.md`; lens and fanout details live in WP3 files.

---

## 1. Glossary & lifecycle

| Term | Definition |
|------|------------|
| 议题 (topic) | 一次讨论要解决的问题,一句话可陈述。 |
| 主持人 (moderator) | 主 agent 在本 skill 中的角色:选 lens、汇总、带对话、收口;**带立场的与会者,不是记录员**。 |
| lens | 一个固定视角的子代理配置,包含章程、取材范围、笔记义务。 |
| 笔记 (lens_note) | 单个 lens 的独立产出,电报体。格式归 `lens-catalog.md` 管。 |
| 会议材料 (meeting_material) | 主持人对全部笔记的汇总,对话阶段的底稿。格式归 `workflow-session.md` 管。 |
| 纪要 (session_minutes) | 一次讨论收口时的存档。格式归 `state-layout.md` 管。 |
| 决议 (decision) | 讨论达成的可执行结论,写入 `decisions.md`,带状态机。格式归 `state-layout.md` 管。 |
| handoff | 移交给 novel-ci planning 的结构化简报。格式归 `workflow-session.md` 管。 |
| digest | 项目上下文压缩摘要,扇出与对话的默认取材源。格式归 `state-layout.md` 管。 |

Lifecycle:

```text
路由 → 记忆检查 → 议题澄清 → [扇出 → 汇总] → 对话 → 收口(纪要+决议[+handoff])
```

`light` intensity skips the bracketed fanout and synthesis segment. One full lifecycle is a
`session`.

---

## 2. Routing axes

The three axes are orthogonal. At the opening of each session, declare `mode`, `variant`,
and `intensity` before proceeding.

### 2.1 mode

| mode | 议题类型 | 默认 lens | 取材重点 |
|------|----------|-----------|----------|
| `outline` | 大纲/结构/走向/人物弧 | structure + character + culture + reader | digest 全部 + arc/brief 原文件 |
| `writing` | 具体场景怎么写/文体/开头 | structure + character + language + reader | digest + scene_card/相邻场景/style 原文件 |
| `free` | 其余一切 | 主持人自选 3—4 个并报告理由 | 按议题定向 |

### 2.2 variant

| variant | 触发 | 各 lens 的任务姿态 |
|---------|------|-------------------|
| `explore` | 用户开放提问("怎么写好""帮我想") | 从本视角提出 2—4 条独立想法/方案要素 |
| `stress` | 用户带方案来("我想 X,帮我检验") | 对方案输出:支持点 / 反驳点 / 修正建议,三节均必填 |

### 2.3 intensity

| intensity | 行为 | 触发 |
|-----------|------|------|
| `light` | 不扇出,主持人单人带 digest 聊 | 用户说"快速聊聊/简单讨论",或议题明显轻量 |
| `standard` | 默认。模式默认 lens 组合,一轮扇出 | 缺省 |
| `deep` | 全 lens(含 contrarian 也仅在点名时)+ 第二轮:汇总回传,每 lens 限 1 条反驳或补强(Delphi 式) | 用户说"深入/全面讨论/重大决定" |

User overrides always win for any axis or lens set. For example, "只让文化那位看" means a
custom lens set and should be acknowledged in the opening declaration.

---

## 3. Anti-mush iron rules

These rules have system-wide priority inside novel-discuss.

1. **独立首轮**:首轮笔记生成期间 lens 互不可见。首轮输入包不得包含其他 lens 的笔记或主持人的预判。串行降级时也一样。
2. **署名分歧强制**:`standard`/`deep` 档的 `meeting_material.disagreements` 为空 = 汇总不合格。主持人必须回去挖 lens 立场差异、stance 冲突、evidence 强度差。确无分歧时,必须写明"各 lens 从不同路径到达同一结论"并列出各自路径;路径差异本身就是信息。`light` 档豁免。
3. **主持人立场强制**:`meeting_material.moderator_take` 必填。主持人是带立场的与会者;只罗列各方观点不给推荐 = 汇总不合格。对话中用户问"你怎么看"时同样适用。

Do not soften these rules in downstream references. Especially do not turn signed
disagreement into an optional nuance section, and do not let the moderator become only a
recorder.

---

## 4. Write boundaries

| Target | Default | Exception |
|--------|---------|-----------|
| `agent/discuss/` 全目录 | 可写(consent 后) | - |
| 项目其他文件(arc/card/draft/设定文档...) | **零写入**,结论走 handoff | 用户明确要求直改时,逐文件向用户确认后可写 |
| `canon/lockfile.yaml`、`canon/*-bible*`、`characters/` | 零写入 | **无例外**;需要改正典 → handoff 给 novel-ci 走 Gate D |
| `manuscript/` | 零写入 | 无例外(含 sketch 草样) |
| `agent/discuss/harness/` | skill 只读 | 无例外(用户自留地) |

The default posture is discussion-only. Novel-discuss produces consensus, disagreement,
decisions, minutes, and handoff material; it does not write canon or manuscript.

---

## 5. Consent and stateless behavior

If `<project>/agent/discuss/` exists, treat consent as already granted.

If it does not exist, ask once before creating it. If `<project>/agent/` is also absent,
create it only as the parent for `agent/discuss/` after consent. When the user agrees,
initialize `agent/discuss/`, build `digest.md`, and run statefully. When the user refuses,
run stateless: assemble one-session context before fanout, do not write minutes or decisions,
and output the final minutes/decision text in chat for the user to save manually.

In stateless mode there is no durable decisions ledger. Skip active-decision conflict
pointing and open-question pickup; the rest of the workflow remains the same. If the user
says "别再问了", respect that for the current conversation, while noting there is no durable
place to store that preference without `agent/discuss/`.

---

## 6. Register stack

The register stack applies only during the conversational discussion phase.

1. `agent/discuss/harness/*.md`: user register slots. Load all of them when entering the
   discussion phase. They are read-only for this skill. If slot files conflict, report the
   conflict and ask the user to decide.
2. `references/register-discussion.md`: novel-discuss specific register for presenting
   disagreement, giving recommendations, avoiding mush, and the generic conversational baseline.
   See that file for targets and evaluation signals.

Exempt products: lens notes, digest, minutes, decisions, and handoff are structured work
products. They may use telegraphic or schema-shaped language instead of conversational
register.
