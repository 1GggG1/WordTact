# 读者索引：顺序、来源与接受稿

本文件定义 `scripts/reader_index.py` 的运行接口。索引是已接受正文的可重建派生数据，不是正典，也不代替连续阅读。它记录“读者读到了什么”，不能把角色的推测、谎话或叙述断言自动升级为世界事实。

## 1. 使用时机与覆盖

- 写前、审前调用 `context --before <unit-id>`，根据返回的引用回读相关正文。
- 新建项目先建立本次需要的接受稿前缀；不为开始一章强制回填全书。
- 每个单元只能在项目接受流程完成后提交。待审稿可生成候选 JSON 供评审，不能提交到正式索引。
- 首次建立相关记录、每累计新增 5 个接受的发布章、旧章内容修改、用户请求多章审稿时，连续阅读最近 10 个发布章；不足 10 章读全部，不足 5 章注明限制。三章词频窗口不能替代此阅读。
- 明确连续阅读、间隔追更或读过正文后阅读番外等读者条件。检查重复解释、决定重复收口、无信息增量的确认与声音趋同，同时保留有新反应、关系变化、误解或笑点功能的复现。
- 同一信息首次和后续出现使用相同披露 ID；默认只登记规则、数值、方案、决定、重要指称、伏笔和笑点，不逐句复制整部小说。

## 2. 路径与命令

Python 3.9+，仅标准库。所有命令必须显式提供项目根目录，绝不从脚本位置推断小说项目。

```sh
python3 <skill-dir>/scripts/reader_index.py --project-root <project> status
python3 <skill-dir>/scripts/reader_index.py --project-root <project> context --before ch003
python3 <skill-dir>/scripts/reader_index.py --project-root <project> commit --input <candidate.json>
```

默认索引为 `<project>/agent/reader-index/index.json`；可在子命令前用 `--index <project-relative-path>` 指定。候选 JSON 的 `--input` 路径是调用方显式提供的文件；候选内的正文、证据、清单及索引路径都必须位于项目内部，拒绝绝对路径、`..` 和逃出项目的符号链接。

`status`、`context` 不创建目录，不写入索引或正文。`commit` 只写索引和同目录临时锁，不修改清单、正文、接受记录或作者决定。

输出为 JSON。状态为 `UNINITIALIZED`、`VALID` 或 `NEEDS_VERIFICATION`；缺失、过期是可报告结果，进程退出码为 0。输入无效、锁冲突、过期提交等操作错误退出码为 2，错误 JSON 写到 stderr。

## 3. 阅读清单

### 3.1 共用的整文件形式

每个实际发布单元对应一个文件时，与语言扫描器共用同一份显式有序清单：

```json
{
  "schema_version": 1,
  "units": [
    {"unit_id": "ch001", "path": "published/ch001.md", "complete_chapter": true},
    {"unit_id": "ch002", "path": "published/ch002.md", "complete_chapter": true},
    {"unit_id": "ch003", "path": "published/ch003.md", "complete_chapter": true}
  ]
}
```

数组顺序就是阅读顺序。`complete_chapter` 供语言统计使用，读者索引不会从 ID 或文件名猜测顺序。`unit_id` 为规范键；旧输入的 `id` 可作为兼容别名，写出的索引统一使用 `unit_id`。

整文件形式会派生 `[0, 字符数)` 的阅读片段及其覆盖范围。正文必须是已存在的非空 UTF-8 文件。清单不能把逻辑稿及其发布副本作为两个阅读单元重复计入；工具只能验证路径及片段重叠，不能凭相似正文推断哪个副本更权威。

### 3.2 拆分、合并与权威正文映射

有发布章与逻辑稿映射时使用片段形式。以下文本长度和边界仅用于说明：

```json
{
  "schema_version": 1,
  "units": [
    {
      "unit_id": "ch001",
      "reading": [{"path": "published/ch001.md", "start": 0, "end": 1200}],
      "canonical": [{"path": "logical/part01.md", "start": 0, "end": 1200}]
    },
    {
      "unit_id": "ch002",
      "reading": [{"path": "published/ch002.md", "start": 0, "end": 800}],
      "canonical": [{"path": "logical/part01.md", "start": 1200, "end": 2000}]
    }
  ],
  "coverage": {
    "reading": [
      {"path": "published/ch001.md", "start": 0, "end": 1200},
      {"path": "published/ch002.md", "start": 0, "end": 800}
    ],
    "canonical": [{"path": "logical/part01.md", "start": 0, "end": 2000}]
  }
}
```

`reading` 按读者实际看到的顺序排列；`canonical` 可选，表示对应权威正文片段。每个单元各自按数组拼接，两边必须逐字相同。标题或发布平台附加文字应由明确片段边界排除，不通过隐式清洗掩盖差异。

`coverage` 明确声明本清单负责的正文范围。每一角色内的单元片段必须恰好覆盖声明范围，不能有遗漏、重叠、重复或范围外内容；合并相邻片段不会视为重复。工具不宣称验证声明范围之外的全书完整性。

同一个文件可拆成多个互不重叠的单元，一个单元也可由多个片段合并。语言扫描器第一版只接受整文件形式；需要扫描映射清单时，调用项目现有发布构建流程生成每个发布单元的实际文件，再显式生成对应整文件清单。不能把每个逻辑片段都扩成整份逻辑稿重复统计。

映射清单本身有路径和 SHA-256，是索引追踪的映射版本。它必须由项目现有发布映射可靠转换；本工具不解析或改造项目的发布系统。

## 4. 候选与存储 schema

候选是本次明确复核并接受的单元增量，旧有效前缀可保留，失效后缀不能默认为已重新审过。

```json
{
  "schema_version": 1,
  "expected_revision": 0,
  "manifest": {"path": "agent/reading-order.json", "sha256": "<whole-file-sha256>"},
  "units": [
    {
      "unit_id": "ch001",
      "reading": [{
        "path": "published/ch001.md", "start": 0, "end": 1200,
        "sha256": "<whole-file-sha256>", "slice_sha256": "<slice-sha256>"
      }],
      "canonical": [],
      "acceptance": {
        "status": "accepted",
        "content_sha256": "<concatenated-reading-slices-sha256>",
        "evidence": {
          "path": "agent/acceptances.md", "sha256": "<whole-file-sha256>",
          "start": 20, "end": 32, "quote": "<exact-acceptance-record>"
        }
      },
      "review": {"base_revision": 0, "confirmed": true},
      "disclosures": [{
        "id": "bridge-status", "summary": "人物认为桥可能仍未开放。",
        "epistemic": "inference", "speaker": "守桥人", "pov": "旅人",
        "first_in": "ch001",
        "anchors": [{"slice": 0, "start": 100, "end": 111, "quote": "<exact-prose-quote>"}]
      }],
      "protected": [{
        "reason": "作者要求保留不确定性，不能改成确定事实。",
        "source": {
          "path": "agent/decisions.md", "sha256": "<whole-file-sha256>",
          "start": 0, "end": 20, "quote": "<exact-author-direction>"
        }
      }]
    }
  ]
}
```

所有示例中的哈希、边界与尖括号占位必须用实际文件计算，不能原样提交。规则如下：

- `start/end` 是解码后的 Unicode 字符下标、零起点、左闭右开；不是 UTF-8 字节位置。保留原始换行，不使用自动换行或 Unicode 归一化。
- `sha256` 对原始文件字节计算；`slice_sha256` 对选取字符片段重新编码为 UTF-8 后计算。接受稿哈希对顺序拼接的阅读片段计算。
- 候选 `reading/canonical` 边界和顺序必须与当前清单相同，全部来源哈希必须是当前版本。
- `review.base_revision` 必须等于 `expected_revision`。`confirmed:true` 是执行者对本次重新审读的明确声明；脚本验证版本及证据，不能证明 LLM 确实理解了文字。
- `acceptance` 必须是明确接受状态，带绑定阅读正文的哈希和真实原文接受记录。脚本不能单靠出现“接受”二字判断作者是否授权；调用方须先完成项目接受流程，不能自行伪造证据。
- `disclosures` 必须提供数组，允许显式空数组。每条有稳定 ID、摘要、至少一个原文锚点，及 `speaker/pov` 至少一个。
- `epistemic` 为 `fact|assertion|inference|lie|unresolved`。标签由 LLM 依上下文判定；`fact` 不会自动写入正典。
- `anchors[].slice` 指向该单元 `reading` 数组下标，`start/end` 仍是源文件绝对字符下标，必须完全落在该片段内。
- `first_in` 必须指向该披露在当前已覆盖前缀内的首次出现；重复记录使用同一 ID。不能指向未来、缺失单元或另一个披露。
- `protected` 可为空；非空条目必须带具体理由及作者来源引用。保留一次不是全书同类表达自动豁免。

落盘索引保存 `schema_version`、递增 `revision`、`manifest`、全阅读 `order`、规范化片段 `definitions`、`coverage_definition`、连续接受前缀 `units` 和最近候选指纹 `last_candidate_sha256`。调用方不要手工更新这些派生字段。

## 5. 失效、并发和可重复提交

- `status` 每次重读清单与实际来源，按阅读顺序检查。旧章正文、披露证据、源映射或阅读顺序变化时，从最早受影响单元起停止信任。
- 同一逻辑文件后段变化时，前段的边界、字面内容和映射均未变化即可保留。文件整体哈希变化不会独自毁掉可证明未变的前段；下一次合法提交刷新该前段的来源哈希。
- 新增末尾单元保留旧前缀；删除或重排使受影响后缀失效。只有 JSON 空白或键顺序变化、语义清单完全相同时，不制造无意义失效。
- 重新提交旧单元的披露解释也会使未重新审读的后缀失效，即使正文未变。
- `commit` 只保留当前有效前缀，再合并本次明确复核的单元；遇到缺口停止覆盖。显式提交跨过缺口的后文会报错，不能跳过中间单元。
- 失效后缀不会通过更新哈希自动复活；必须提交与当前索引版本一致的 `review`、接受稿证明及逐条可核对的记录。可以分批恢复前缀。
- 比较并交换使用 `expected_revision`。同目录排他锁防止两个写入者同时修改；持锁期间预检并再次验证来源，临时文件写入和 fsync 完成后原子替换索引。
- 同一个候选在相同有效来源上重复提交是幂等的，不增加 revision。来源已变时拒绝把旧候选作为重试接受。
- 活跃锁不自动清除。确认无写入者运行且是异常遗留锁后，调用方才可另行处理；正文编辑器不共享此锁，不能声称索引与多个外部正文文件构成跨文件事务。

## 6. 查询结果与局限

结果包含 `revision`、`valid_prefix`、当前 `order`、`missing`、`invalidated` 和 `issues`。`context` 另含目标之前的有效 `units` 及 `uncovered_before_target`。

若同一源文件的后段已修改而前段仍有效，`context` 在重新核对片段哈希后，将返回副本中的
整文件 `sha256` 更新为当前值；片段哈希保持不变，磁盘索引和接受证据不被改写。

查询只返回目标之前的正文定位与披露，不返回目标及以后章节的摘要、引文。接受报告和作者决定属于编辑元数据，可能包含后文信息，因此不作为“读者已知”返回。需要作者保护项时，编辑流程单独按授权范围读取相关决定。

全索引状态为 `NEEDS_VERIFICATION` 不代表所有前缀都不可用；必须根据 `uncovered_before_target` 判断本次查询缺口。不能把缺口外推为“全书没有重复”。

脚本证明来源可定位、版本一致、映射完整和读者前缀边界；不能证明摘要正确、文本已发表、作者声明真实或信息首次出现没有被 LLM 漏记。这些仍是审读与接受流程的责任。
