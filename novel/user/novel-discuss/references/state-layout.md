# Novel Discuss — State Layout

> Canonical source: `design/novel-discuss/contracts.md` §3, §4.1, §4.4, §4.5, §10.
> This file defines the `agent/discuss/` memory directory contract and state schemas.
> It does NOT contain fanout choreography, lens charters, meeting material, handoff, or sketch schemas.

---

## 1. Memory directory tree

All files below live under `<project>/`, the user's novel project directory.

```text
<project>/agent/discuss/
  digest.md            # 上下文摘要(§4.1);唯一被扇出默认引用的上下文文件
  decisions.md         # 决议台账,追加写(§4.5)
  sessions/
    <session_id>/
      minutes.md       # 纪要(§4.4)
      sketches/        # expander 试写草样(仅当发生委托;永不迁出)
  harness/             # 用户 register 插槽;skill 只读,永不写
```

`session_id` format: `YYYYMMDD-<slug>`. The slug is 2-4 topic words in kebab-case, for
example `20260708-double-timeline`.

### Readers & writers

| Path | Readers | Writer | Write timing |
|------|---------|--------|--------------|
| `agent/discuss/digest.md` | moderator, lens fanout, session workflow | state-layout logic | Consent initialization; startup freshness refresh; open-question merge |
| `agent/discuss/decisions.md` | moderator, session workflow, digest refresh | session workflow | Session close; append new decisions; only supersede update may edit an old entry |
| `agent/discuss/sessions/<session_id>/minutes.md` | user, moderator, future novel-ci planning if handed off | session workflow | Session close |
| `agent/discuss/sessions/<session_id>/sketches/` | user, moderator | novel-expander sketch delegate or moderator fallback | Only when a sketch is requested; never moved into `manuscript/` |
| `agent/discuss/harness/*.md` | moderator, register stack | user only | Skill never writes here |

---

## 2. Consent protocol

When `<project>/agent/discuss/` is absent, ask once before creating it. If `<project>/agent/`
is also absent, create it only as the parent for `agent/discuss/` after consent. Show the
directory tree and explain in one sentence that it avoids reloading the whole project on every
discussion.

Consent outcomes:

- Agree: create `agent/discuss/`, build `digest.md`, and continue in stateful mode.
- Refuse: run stateless. Pull context for this session only; at close, output minutes and
  decisions in chat for the user to save manually. Do not ask again inside the same session.
- Existing `agent/discuss/`: treat as already consented; do not ask again.

If the user says "别再问了" after refusing, respect that for the current conversation. Without
`agent/discuss/`, there is no durable storage location for that preference.

---

## 3. Digest build and freshness

With a novel-ci project, detected by the presence of `canon/`, build `digest.md` from:

- `canon/lockfile.yaml`
- `canon/project-brief.yaml`
- world bible files
- `canon/characters/` or `characters/`
- latest arc material

These sources are already compressed state; compile and compress them again for discussion.

Without a novel-ci project, scan only user-identified setting, outline, and draft files, then
record the source list in the digest header.

Freshness rules:

- Record a fingerprint for each source file in `## sources`: mtime or content hash, whichever
  is available in the environment.
- On startup, compare stored fingerprints to current fingerprints.
- Refresh only stale sections when possible.
- Include one-line summaries of active `decisions.md` entries in `## decisions-active`; this
  closes the memory loop.
- Append parked open questions from session minutes into `## open-questions`.

Stateless mode has no persisted digest. Before fanout, assemble a one-session equivalent in
memory and pass that as the digest substitute.

---

## 4. digest.md schema

Markdown file with exactly these five top-level sections:

```markdown
# Discuss Digest
## sources          <!-- 表:path | fingerprint | digested_at -->
## canon-summary    <!-- 正典要点:世界规则/角色声音红线/时间线位置/open threads;对话中冲突指认的依据 -->
## story-state      <!-- 叙事进度:写到哪、当前 arc 目标、近期场景梗概 -->
## decisions-active <!-- decisions.md 中 status: active 条目的一行摘要列表(id + 一句话) -->
## open-questions   <!-- 历次纪要沉淀的未决问题(id + 一句话 + 来源 session_id) -->
```

`digest.md` is the only context file that fanout references by default. If a lens needs source
detail, the moderator may add up to three targeted source files in that lens input package;
the fanout protocol owns that selection.

---

## 5. session_minutes schema

Stored as `agent/discuss/sessions/<session_id>/minutes.md`.

```markdown
# <topic>(<session_id>)
## verdicts       <!-- 达成的决议:引用 decisions.md 条目 id -->
## meeting-material  <!-- 4.3 的 YAML 归档 -->
## key-turns      <!-- 对话中改变走向的 3—5 个节点,一行一个 -->
## parked         <!-- 搁置的开放问题(汇入 digest.open-questions) -->
## handoff        <!-- 4.6 的副本;未移交则写 none -->
```

`meeting-material` and `handoff` schemas are owned by `workflow-session.md`; this file only
defines the minutes container.

---

## 6. decision entry schema

Append entries to `agent/discuss/decisions.md`.

```yaml
id: D-20260708-01          # D-<YYYYMMDD>-<seq>
topic: ...
decision: ...              # 可执行的一句话
because: ...               # 当时理由,1—3 句
status: active             # active | superseded
superseded_by: null        # 被替代时填新条目 id;同时旧条目 status 改 superseded(唯一允许的回改)
session: 20260708-double-timeline
```

Conflict-pointing duty: when a new direction conflicts with an active decision, the moderator
must name that decision, restate its `because`, and ask whether to supersede it. Not pointing
out the conflict violates D10.

The only allowed edit to an existing decision is supersession: set old `status` to
`superseded` and `superseded_by` to the new decision id. All other decision changes append a
new entry.

---

## 7. Naming and write modes

- Directories and filenames use lowercase kebab-case.
- `session_id`: `YYYYMMDD-<slug>`, where slug is 2-4 topic words in kebab-case.
- Decision id: `D-<YYYYMMDD>-<seq>`.
- YAML keys use snake_case and must match the owning schema exactly.
- Digest, decisions, and minutes are markdown-first files with YAML blocks where needed.
- Append writes: `decisions.md` and `digest.open-questions`.
- Overwrite writes: all `digest.md` sections except `## open-questions`.
- Session writes are one directory at a time under `agent/discuss/sessions/<session_id>/`.
- `agent/discuss/harness/` is always read-only for this skill.
