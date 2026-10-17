# 修订工具：固定原稿、限定范围批改与版本化验收

当 auditor 直接修订正文，或 CI 执行补丁时，使用 `../scripts/revision_guard.py`。两者共用同一套机制，不要求普通审稿迁移为 scene-card 流程。工具需要 Python 3.9+，仅依赖标准库，在支持 `fcntl` 文件锁的系统上运行。

本工具验证版本、精确修改范围和检查凭据的完整性。它不判断文学质量，不从一个 `PASS` 字符串推断语义正确，也不替代作者的项目接受流程。判断方法见 [workflow-regression.md](workflow-regression.md)。

## 1. 固定范围与调用约定

所有命令显式指定 `--project-root` 和项目内相对路径 `--session`。命令名位于这两个参数之后，例如：

```sh
python3 revision_guard.py --project-root "$project_root" --session agent/audits/revision-session snapshot --input scope.json
python3 revision_guard.py --project-root "$project_root" --session agent/audits/revision-session prepare --input edits.json
python3 revision_guard.py --project-root "$project_root" --session agent/audits/revision-session apply --batch "$batch_id"
python3 revision_guard.py --project-root "$project_root" --session agent/audits/revision-session verify --batch "$batch_id"
python3 revision_guard.py --project-root "$project_root" --session agent/audits/revision-session accept --batch "$batch_id" --receipt receipt.json
python3 revision_guard.py --project-root "$project_root" --session agent/audits/revision-session rollback --batch "$batch_id"
```

`scope.json`、`edits.json`、`receipt.json` 是显式输入文件，可从调用者当前目录或绝对路径读取；其中的正文、凭据和制品路径必须相对于项目根目录。拒绝 `..`、绝对路径、非规范路径和路径中的符号链接，不扫描其他项目。审计会话不能包含被修改的正文文件。

成功时 stdout 输出 JSON、退出 0；拒绝时 stderr 输出 `{"status":"REFUSED","error":"原因"}`、退出 2。`verify` 完全只读；其他命令会修改指定会话，其中只有 `apply` 和 `rollback` 会修改正文。调用这些命令必须已经处于用户授权的修订范围。

## 2. snapshot：固定完整原稿

输入 schema：

```json
{
  "schema_version": 1,
  "files": ["manuscript/chapter-01.md", "manuscript/chapter-02.md"],
  "mapping_required": false,
  "baseline_commit": null
}
```

- `files` 是本次修订涉及的完整正文文件集合，不能重复。即使仅修改其中一句，也冻结整个文件。
- `mapping_required` 必须显式提供。若存在需重新生成并验证的发布稿映射，设为 `true`。
- `baseline_commit` 可省略或为 `null`；使用时必须是完整的 40 位或 64 位小写十六进制提交 ID，不能写 `HEAD` 或分支名。它是调用者提供的来源标签，工具不声称验证了对应 Git 历史。
- UTF-8 原始字节完整保存，不转换换行。索引文件记录 SHA-256 和文件权限。
- `original.json` 一旦建立就拒绝覆盖。历史材料没有可信原稿时应另行报告缺失，不能把当前版本冒充旧版。

同时建立独立的 `latest.json`，初始状态为 `BASELINE`：仅代表本次输入，**不是**“历史上已经验收”。后续 `accept` 才将最近接受稿推进为 `ACCEPTED`。原稿已有事实错误时可以依据有效作者决定修复；固定原稿用于比较，不是事实权威。

会话布局：

```text
revision-session/
  .lock
  original.json
  latest.json
  latest-history/<manifest-sha256>.json
  objects/<content-sha256>
  batches/<batch-id>/
    manifest.json
    changes.diff
    journal.json
    receipt.json
```

所有原稿、补丁输入、候选稿及已接受凭据的证据和制品保存在 `objects`。`latest-history` 保留每一份最近接受稿索引，使多轮回归能够取回当时的版本，而不依赖会移动的当前文件或 Git 引用。JSON 索引采用 `{"payload":...,"sha256":...}` 封装，对 canonical JSON 计算 SHA-256，并在读取时检查；这用于发现意外损坏，不是防止持有写权限者同时重写全部内容的密码学签名。

## 3. prepare：先检查整批，再生成候选

输入 schema：

```json
{
  "schema_version": 1,
  "files": [
    {
      "path": "manuscript/chapter-01.md",
      "sha256": "当前完整正文文件的 SHA-256",
      "allowed_ranges": [[0, 12]],
      "edits": [
        {"old": "门还开着", "new": "门敞着", "start": 0, "end": 4}
      ]
    }
  ]
}
```

上例说明字段形状；使用实际正文的哈希和范围，不能直接照抄示例数值。

- `path` 必须属于固定会话范围，`sha256` 必须匹配当下完整文件。
- `allowed_ranges` 必填，以本次输入原文的 Unicode 字符位置计算，起点含、终点不含，不是 UTF-8 字节位置。调用者从审稿问题及已授权范围确定这些区间，工具验证修改没有越界，不替调用者判断授权本身。
- `start`、`end` 可以一起省略，此时 `old` 必须在整个文件中精确且唯一出现。重复引用必须提供明确位置。
- 删除使用空的 `new`；插入使用空的 `old`，但必须提供相等的 `start`、`end`。拒绝无变化修改、重叠修改及同位置的多次插入。
- 所有位置针对同一个修改前版本，按照倒序应用，不能把前一条补丁造成的偏移写入后一条位置。
- 所有文件全部预检通过，才创建批次候选、差异和清单。预检失败不修改任何正文，不生成半批候选。

输出 `PREPARED`、`batch_id`、`manifest_sha256`、`original_manifest_sha256`、`latest_manifest_sha256`、`files` 和可审查的 diff 路径。`files` 是**完整会话范围**的预期最终哈希，包含未被本批修改的文件。

清单保存完整输入和候选稿哈希、解决后的精确位置、授权区间、原稿/最近接受稿版本和 diff 哈希。每次加载批次都会从保存的输入重新应用补丁，检查候选及 diff 确实等于声明的范围内修改。

`prepare` 允许从尚未接受的上轮候选继续小范围修复，但每轮仍同时记录固定原稿、最近接受稿及本轮输入，不能把候选偷偷升级为接受稿。改稿的保护项、目标和文学判断保存在审稿/回归证据中。

## 4. apply、verify、rollback：安全写入与恢复

`apply` 先检查整个会话范围的当前哈希，确认仍是本批输入或本批精确候选，然后逐个文件写入：

1. 读取已保存的候选稿，写入同目录临时文件并刷盘。
2. 紧邻替换前再次核对正文哈希。
3. 原子替换一个文件，保留其权限并刷盘目录。
4. 更新该文件日志为 `WRITTEN`。

日志状态为 `PREPARED → APPLYING → APPLIED`；失败为 `PARTIAL`，每个文件明确标记 `PENDING` 或 `WRITTEN`。这不是跨文件事务，不声称多个文件整体原子完成。

进程在替换后、日志更新前中断时，再运行同一 `apply` 会比较实际文件和保存候选的哈希，识别已完成文件，继续剩余文件。若任何位置出现不同版本，拒绝继续，不覆盖外部修改。不要在恢复之前手动把日志改成成功。

会话使用非阻塞 `fcntl` 锁，同一会话不能并发运行修改命令。它不控制其他编辑器或其他会话；逐文件的紧邻哈希复核会拒绝已观察到的冲突，但普通文件系统不提供跨所有文件的比较并交换事务。批改期间不要让其他程序同时写同一组正文。

`verify` 重新验证清单、保存对象、声明的补丁范围和完整会话当前哈希，成功结果叫 `VERIFIED_BYTES`，不是文学验收通过。

`rollback` 只恢复这批修改的输入，不能自动清除原来的问题：

- 回滚前检查整个范围，每次替换前再次核对。
- 当前文件必须仍是本批候选；已经等于本批输入的文件视为已恢复。
- 有其他版本时停止，不覆盖并发工作。
- 中断状态为 `ROLLBACK_PARTIAL`，重复同一命令可继续恢复。
- 恢复完为 `ROLLED_BACK`；不能重用旧批次再次 apply，需要新的 prepare。
- 已接受批次不能直接 rollback。撤销已接受内容应形成新批次、重新评审，并保留接受历史。

## 5. accept：所有检查绑定同一个最终版本

在完成标点统一、词频复算、语义回归和适用的发布映射检查，并满足项目自身的接受条件后，提交凭据：

```json
{
  "schema_version": 1,
  "batch_id": "prepare 返回的批次 ID",
  "manifest_sha256": "prepare 返回值",
  "original_manifest_sha256": "prepare 返回值",
  "latest_manifest_sha256": "prepare 返回值",
  "files": {"manuscript/chapter-01.md": "最终 SHA-256", "manuscript/chapter-02.md": "最终 SHA-256"},
  "checks": {
    "semantics": {"status": "PASS", "evidence": "agent/audits/review-01.json", "sha256": "证据文件 SHA-256"},
    "frequency": {"status": "RETAINED", "reason": "具体位置和整体密度的保留理由见证据", "evidence": "agent/audits/frequency-01.json", "sha256": "证据文件 SHA-256"},
    "punctuation": {"status": "PASS", "evidence": "agent/audits/punctuation-01.json", "sha256": "证据文件 SHA-256"},
    "mapping": {"status": "NOT_APPLICABLE", "reason": "本次范围无派生发布稿", "evidence": "agent/audits/scope-01.json", "sha256": "证据文件 SHA-256"}
  }
}
```

凭据要求：

- `files` 必须与 prepare 返回的完整范围和最终哈希完全一致。
- `semantics`、`punctuation` 只接受 `PASS`。
- `frequency` 接受 `PASS` 或有具体理由的 `RETAINED`。保留不改变实际计数，不删除超线记录；证据必须包含逐处分类和整体密度判断。
- `mapping_required=true` 时 mapping 必须为 `PASS`，并包含非空 `artifacts`，记录映射文件和所有相关派生稿的相对路径与 SHA-256；工具会在接受前重新核对。
- `mapping_required=false` 时才允许有理由的 `NOT_APPLICABLE`，仍须提供范围证据。
- 任一检查可附 `artifacts` 保存其依赖文件哈希，例如固定版本的语言档案和扫描结果。
- 缺失、`SKIPPED`、`FAIL`、`UNRESOLVED` 或 `NEEDS_VERIFICATION` 均不允许接受。应补充验证或修订，不伪造 `PASS`。

证据文件内部应注明相同的正文版本、检查范围、检查者/方法、结论和限制。语义证据还要对照固定原稿与最近接受稿，记录是否有否定、确定性、数量、施事、动作状态、知情、声音及节奏变化。工具只验证提供的文件和哈希，不理解这些判断是否正确；调用者负责执行检查，而不是只创建空洞凭据。

接受前再次核对当前全文、凭据及制品版本，保存证据的内容快照，然后推进 `latest.json` 并归档旧索引。后续新稿或重新生成的发布稿不会抹去历史接受证据。使用每批独立证据文件名以便人工追溯。

若写入 latest 后、日志更新前中断，使用完全相同的凭据再次 accept 可恢复。凭据被改动、候选有进一步修改、旧批次基于过时的最近接受稿，均须重新验证，不复用旧通过状态。

成功返回 `ACCEPTED` 只表示工具接受了这份完整且版本一致的凭据。随后按项目工作流更新读者索引；索引记录必须使用这些最终哈希。任何再次改字、改标点或重建派生稿，都要对受影响的检查重新验证。
