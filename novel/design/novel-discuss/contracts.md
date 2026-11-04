# Novel Discuss — 规范契约(单一事实源)

> 全部 WP 以本文件为接口基准。schema 键名、目录名、lens_id、档位名、格式一律以此为准。
> 各 schema 标注 owner(转写落地的 reference 文件);消费方引用 owner 文件名+节号,不复制。
> 发现契约缺陷:停下报告维护者,不得就地修改本文件。

---

## §1 术语与讨论生命周期

| 术语 | 定义 |
|------|------|
| 议题 (topic) | 一次讨论要解决的问题,一句话可陈述 |
| 主持人 (moderator) | 主 agent 在本 skill 中的角色:选 lens、汇总、带对话、收口;**带立场的与会者,不是记录员** |
| lens | 一个固定视角的子代理配置(章程+取材范围+笔记义务) |
| 笔记 (lens_note) | 单个 lens 的独立产出,电报体 |
| 会议材料 (meeting_material) | 主持人对全部笔记的汇总,对话阶段的底稿 |
| 纪要 (session_minutes) | 一次讨论收口时的存档 |
| 决议 (decision) | 讨论达成的可执行结论,写入 decisions.md,带状态机 |
| handoff | 移交给 novel-ci planning 的结构化简报 |
| digest | 项目上下文压缩摘要,扇出与对话的默认取材源 |

生命周期:`路由 → 记忆检查 → 议题澄清 → [扇出 → 汇总] → 对话 → 收口(纪要+决议[+handoff])`。
light 档跳过方括号段。一次生命周期称为一个 **session**。

---

## §2 模式 × 变体 × 强度

三轴正交,路由时各定一档,主持人在开场白中声明三者。

### 2.1 模式 mode(定默认 lens 组合与取材重点)

| mode | 议题类型 | 默认 lens | 取材重点 |
|------|---------|----------|---------|
| `outline` | 大纲/结构/走向/人物弧 | structure + character + culture + reader | digest 全部 + arc/brief 原文件 |
| `writing` | 具体场景怎么写/文体/开头 | structure + character + language + reader | digest + scene_card/相邻场景/style 原文件 |
| `free` | 其余一切 | 主持人自选 3—4 个并报告理由 | 按议题定向 |

### 2.2 变体 variant(定扇出 prompt 姿态)

| variant | 触发 | 各 lens 的任务姿态 |
|---------|------|-------------------|
| `explore` | 用户开放提问("怎么写好""帮我想") | 从本视角提出 2—4 条独立想法/方案要素 |
| `stress` | 用户带方案来("我想 X,帮我检验") | 对方案输出:支持点 / 反驳点 / 修正建议,三节均必填 |

### 2.3 强度 intensity

| intensity | 行为 | 触发 |
|-----------|------|------|
| `light` | 不扇出,主持人单人带 digest 聊 | 用户说"快速聊聊/简单讨论",或议题明显轻量 |
| `standard` | 默认。模式默认 lens 组合,一轮扇出 | 缺省 |
| `deep` | 全 lens(含 contrarian 也仅在点名时)+ 第二轮:汇总回传,每 lens 限 1 条反驳或补强(Delphi 式) | 用户说"深入/全面讨论/重大决定" |

用户可随时显式覆盖任何一轴("只让文化那位看" = 自定义 lens 集)。

---

## §3 记忆目录契约

### 3.1 目录树(全部位于用户项目根下)

```text
<project>/agent/discuss/
  digest.md            # 上下文摘要(§4.1);唯一被扇出默认引用的上下文文件
  decisions.md         # 决议台账,追加写(§4.5)
  sessions/
    <session_id>/
      minutes.md       # 纪要(§4.4)
      sketches/        # expander 试写草样(仅当发生委托;永不迁出)
  harness/             # 用户 register 插槽;skill 只读,永不写(§8)
```

`session_id` 格式:`YYYYMMDD-<slug>`,slug 为议题 2—4 词 kebab-case(如 `20260708-double-timeline`)。

### 3.2 Consent 协议

- 项目根无 `agent/discuss/` 时,首次进入 skill 必须询问一次:是否允许创建上述目录(展示目录树,
  一句话解释用途:避免每次全仓重拉)。若 `agent/` 也不存在,同意后仅作为 `agent/discuss/`
  的父目录创建。
- **同意** → 创建 `agent/discuss/` + 构建 digest → 有状态模式。
- **拒绝** → stateless 模式:本次现拉上下文,收口时纪要/决议全文输出在对话中由用户自行保存;
  本 session 内不再追问。下次启动可再问,用户若说"别再问了"则在对话中尊重(无处持久化,
  属已知限制,写进 conventions 即可)。
- `agent/discuss/` 已存在 → 视为已 consent,不重复询问。

### 3.3 digest 构建与新鲜度

- **有 novel-ci 项目**(存在 `canon/`):digest 从 lockfile + project-brief + world-bible +
  characters/ + 最新 arc 提炼;它们本来就是压缩态,只做汇编与再压缩。
- **无 CI 项目**:主持人扫描用户指认的设定/大纲/草稿文件后提炼,并在 digest 头部记录取材清单。
- 新鲜度:digest 头部记录每个源文件的指纹(mtime 或内容 hash 任一,由实现挑可用者)。
  启动时校验,过期只增量刷新对应节。
- decisions.md 的 active 条目摘要是 digest 固定组成部分(记忆闭环)。

### 3.4 stateless 模式行为差异

无 digest → 扇出前主持人现场做一次性上下文汇编(等价 digest,不落盘);无决议台账 → 跳过
冲突指认与回捡;其余流程一致。

---

## §4 Schema 全集

### 4.1 digest.md(owner: state-layout.md)

markdown 文件,固定五节:

```markdown
# Discuss Digest
## sources          <!-- 表:path | fingerprint | digested_at -->
## canon-summary    <!-- 正典要点:世界规则/角色声音红线/时间线位置/open threads;对话中冲突指认的依据 -->
## story-state      <!-- 叙事进度:写到哪、当前 arc 目标、近期场景梗概 -->
## decisions-active <!-- decisions.md 中 status: active 条目的一行摘要列表(id + 一句话) -->
## open-questions   <!-- 历次纪要沉淀的未决问题(id + 一句话 + 来源 session_id) -->
```

### 4.2 lens_note(owner: lens-catalog.md;扇出产物,子代理返回体)

```yaml
lens: structure            # lens_id,§5.1 枚举
variant: explore           # explore | stress
stance: |                  # 一句话立场(explore: 本视角最重要的一个判断;stress: 总体支持/反对/有条件支持)
points:                    # explore: 2—4 条想法;stress: 按 support/objection/amendment 分组
  - claim: ...             # 主张,一句话
    why: ...               # 依据,电报体 1—3 句
    evidence: ...          # 指向 digest 节或原文件锚点;无实据写 "推断"
open_question: ...         # 本视角最想问用户的一个问题(可省)
```

电报体豁免:笔记不适用对话 register,高密度、不修辞、不寒暄(§8)。

### 4.3 meeting_material(owner: workflow-session.md;主持人汇总,对话底稿)

```yaml
topic: ...
mode: outline | writing | free
variant: explore | stress
intensity: light | standard | deep
lenses: [structure, character, ...]
convergence:               # 收敛点:≥2 个 lens 独立同向的判断
  - point: ...
    backed_by: [structure, reader]
disagreements:             # 署名分歧节。standard/deep 档下为空 = 汇总不合格(§6)
  - question: ...          # 分歧聚焦为一个问题
    positions:
      - lens: structure
        position: ...
      - lens: language
        position: ...
options:                   # 可选方案 2—3 个(explore),或 方案修正稿(stress)
  - label: ...
    gist: ...
    tradeoff: ...
moderator_take:            # 主持人推荐 + 理由,必填(§6)
  pick: ...
  because: ...
open_questions: [...]
canon_flags: [...]         # 与 canon-summary 冲突的点子预警(可空)
```

对话开场时以自然语言呈现给用户,YAML 仅为归档格式(存入纪要)。

### 4.4 session_minutes(owner: state-layout.md;`sessions/<session_id>/minutes.md`)

```markdown
# <topic>(<session_id>)
## verdicts       <!-- 达成的决议:引用 decisions.md 条目 id -->
## meeting-material  <!-- 4.3 的 YAML 归档 -->
## key-turns      <!-- 对话中改变走向的 3—5 个节点,一行一个 -->
## parked         <!-- 搁置的开放问题(汇入 digest.open-questions) -->
## handoff        <!-- 4.6 的副本;未移交则写 none -->
```

### 4.5 decision 条目(owner: state-layout.md;decisions.md 内追加)

```yaml
id: D-20260708-01          # D-<YYYYMMDD>-<seq>
topic: ...
decision: ...              # 可执行的一句话
because: ...               # 当时理由,1—3 句
status: active             # active | superseded
superseded_by: null        # 被替代时填新条目 id;同时旧条目 status 改 superseded(唯一允许的回改)
session: 20260708-double-timeline
```

冲突指认义务:对话中出现与某 active 决议相悖的新方向时,主持人必须指出该条目、复述其
because、询问是否 supersede。不指认 = 违反 D10。

### 4.6 handoff 简报(owner: workflow-session.md;移交 novel-ci planning 的输入)

```yaml
from: novel-discuss
session: <session_id>
decisions: [D-20260708-01, ...]
summary: ...               # 3—5 句:定了什么、为什么
impact:                    # 影响范围,novel-ci 侧的落点
  - target: chapter-arc | scene-card | character | world-rule | style
    what: ...
suggested_actions:         # 建议动作,planning 可直接消化
  - ...
unresolved: [...]          # 明知未决、留给 planning 的
```

移交方式:写入纪要 handoff 节,并在对话中提议"要把这份简报交给 novel-ci 的 planning 吗"。
用户同意后,后续 novel-ci 会话以该纪要文件路径为输入。

### 4.7 sketch 委托(owner: workflow-session.md;发给 novel-expander 的调用参数)

```yaml
caller: novel-discuss
budget: sketch             # expander Invocation contract 的档位(§9.2)
variants: 2                # 2—3
length: ≤500字/变体
input: ...                 # 节拍/开头意图,自由文本;可附 digest 相关节
constraints: ...           # 视角/文体约束,来自讨论现场
output_dir: agent/discuss/sessions/<session_id>/sketches/
```

铁则:草样**永不写入 manuscript/**,永不作为正式稿移交;仅供讨论感受质感。

---

## §5 扇出协议

### 5.1 lens_id 枚举(冻结)

`structure` | `character` | `culture` | `language` | `reader` | `contrarian`

各 lens 章程(视角定义、必答问题、取材倾向)是内容层材料,owner: lens-catalog.md,
设计原料见 `lens-catalog.md`(design 包同名文件)。contrarian 不进任何默认组合,仅点名出场。

### 5.2 单 lens 输入包

扇出时每个子代理收到且仅收到:

1. 议题陈述 + variant + mode(以及 stress 变体下的用户方案原文)
2. digest 全文(stateless 模式为现场汇编等价物)
3. ≤3 个定向原文件(主持人按 lens 取材倾向挑选;可为零)
4. 本 lens 章程(lens-catalog 对应节)
5. lens_note 格式(§4.2)

**独立性铁则:任何其他 lens 的笔记、主持人的预判,不得进入输入包。** 串行降级(D12)时
同样适用:逐 lens 自问自答,前一笔记不进后一 lens 的工作上下文;实现手段由 harness 能力
决定,原则不变。

### 5.3 deep 档第二轮

第一轮汇总(§4.3 草稿)回传各 lens,每 lens 限输出 **1 条**:反驳某收敛点/分歧立场,或
补强自己第一轮的主张。超过 1 条,主持人只取第一条。第二轮后主持人定稿 meeting_material。

### 5.4 model-hint(可选)

lens-catalog 可为各 lens 标注 `model_hint`(如 reasoning 强/文风感知强)。harness 支持
选模型则参考,不支持则忽略。仅为提示,非依赖。

### 5.5 按需点名咨询

对话阶段用户或主持人点名某 lens 追问:单发该 lens,输入包 = §5.2 + 当前争论焦点摘要
(此时**允许**携带相关分歧立场——独立性铁则只约束首轮)。返回仍为 lens_note 格式。

---

## §6 防和稀泥三铁则(全系统最高优先级)

1. **独立首轮**:首轮笔记生成期间 lens 互不可见(§5.2)。
2. **署名分歧强制**:standard/deep 档的 meeting_material 中 `disagreements` 为空 = 汇总
   不合格,主持人必须回去挖(lens 立场差异、stance 冲突、evidence 强度差都算原料)。
   确无分歧时,必须写明"各 lens 从不同路径到达同一结论"并列出各自路径——路径差异本身
   就是信息。light 档豁免。
3. **主持人立场强制**:`moderator_take` 必填。主持人是带立场的与会者;只罗列各方观点
   不给推荐 = 汇总不合格。对话中用户问"你怎么看"时同样适用。

任何 WP 产物不得弱化三铁则(blueprint §8 红线 3)。

---

## §7 写边界

| 目标 | 默认态 | 例外 |
|------|--------|------|
| `agent/discuss/` 全目录 | 可写(consent 后) | — |
| 项目其他文件(arc/card/draft/设定文档…) | **零写入**,结论走 handoff | 用户明确要求直改时,逐文件向用户确认后可写 |
| `canon/lockfile.yaml`、`canon/*-bible*`、`characters/` | 零写入 | **无例外**;需要改正典 → handoff 给 novel-ci 走 Gate D |
| `manuscript/` | 零写入 | 无例外(含 sketch 草样,见 §4.7) |
| `agent/discuss/harness/` | skill 只读 | 无例外(用户自留地) |

---

## §8 Register 栈契约

对话阶段生效,优先级自上而下:

1. **用户插槽** `agent/discuss/harness/*.md`:进入对话阶段时全部加载,视为用户对语气风格的直接
   指示,优先级最高。文件间冲突 → 向用户报告并请裁决。
2. **本 skill 讨论 register** `references/register-discussion.md`:讨论场景专属——如何呈现
   分歧(报立场与依据,不表演冲突)、如何给推荐(亮出 because,欢迎被推翻)、如何不和稀泥
   (禁"都有道理"式收束)。内容层原料见 design 包 `register-material.md`。
3. **作者协作对话基座**:由包内 `user/novel-conversation/SKILL.md` 统一提供，供讨论、
   规划、扩写和审稿的作者沟通共用。个人偏好只进入项目侧只读 harness 插槽。
   人物对白由 `user/novel-dialogue/SKILL.md` 指导，不继承作者沟通语气。

红线(继承已验证教训,blueprint §8 红线 4/8):全栈禁 persona 指令("你是/扮演 X");禁
好/坏示例句,只写 register 目标与评估信号;register 材料描述"输出该像什么",不描述
"你是谁"。**安全层零内容**:拒答/身份声明/心理安全指引归 API 供应商,栈内任何一层
(含用户插槽的蒸馏建议)都不承载。

**豁免区**:lens 笔记、digest、纪要、决议、handoff 均为工作产物,电报体/结构化,不适用
对话 register。

---

## §9 Sibling 委托契约与 delta 义务

### 9.1 讨论 register 基座

§8.3 所述。共用基座由包内 novel-conversation 维护，不依赖个人 skill 或个人 memory。
本 skill 的 register-discussion.md 只维护主持讨论的增量。

### 9.2 → novel-expander(sketch 试写)

按 §4.7 参数调用。依赖 expander 侧改造(§9.4-c):Invocation contract 增加 `budget: sketch`
档——2—3 个短变体、探索性、自查从轻(仅硬禁止层)、输出到 caller 指定目录。
expander 不可用时的 fallback:主持人自写单变体粗样,显式标注"未过 expander 语言层,仅供
讨论",同样只落 sketches/。

### 9.3 → novel-ci(handoff 移交)

单向:discuss 产简报(§4.6),novel-ci planning 消费。novel-ci 侧无需新增机制——纪要
文件作为 planning 的用户输入即可,但其 description 需路由句(§9.4-a)。

### 9.4 Delta 义务(WP5 交付)

**a) novel-ci/SKILL.md description 追加一句**(语义,措辞 WP5 定):
"用户想讨论、头脑风暴、纠结大纲或写法而非直接产出 → 路由 novel-discuss;discuss 的
handoff 简报是 planning 的合法输入。"

**b) novel-expander/SKILL.md description 追加一句**:
"用户想讨论怎么写而非要正文 → 路由 novel-discuss。"

**c) novel-expander 适配改造**(独立于 discuss 也成立的健康化,一并交付):

| # | 改造 | 内容 |
|---|------|------|
| c1 | 路径修复 | Step 5 的 `/mnt/user-data/outputs/` 是 claude.ai 容器遗留。改为环境中立:caller 指定 > 用户指定 > 当前目录下合理默认。全文件核查同类路径 |
| c2 | Invocation contract | 把 "## CI mode" 一节泛化为 "## Invocation contract":caller 提供 {input_spec, constraints_priority, output_path, budget}。budget 枚举:`full`(现状整章)/ `scene`(CI 单场景)/ `sketch`(§9.2)。CI mode 改写为契约实例,行为零变化;discuss sketch 为第二实例 |
| c3 | standalone 项目感知 | standalone 且 cwd 或用户项目内存在 `canon/style/` → 询问是否沿用项目文风/voice-samples,替代默认参数 |
| c4 | diff 自查 | maintainer notes 的 anti-ai-patterns 同步段追加一行 diff 自查命令(两份拷贝现已同仓) |

Delta 红线:expander/auditor **standalone 行为零变化**(c1 的路径行为除外——那是 bug 修复);
改动对照 git diff 审查,范围仅限上述条目。

---

## §10 命名与格式约定

- 目录/文件名:全小写 kebab-case。session_id、decision id 格式见 §3.1、§4.5。
- YAML 键名:snake_case,与本文件逐字一致。
- 纪要/decisions/digest:markdown 为体、YAML 块为骨,人读优先。
- 追加写:decisions.md、digest.open-questions;覆盖写:digest 其余节;一次一目录:sessions/。
- 语言分配:meta 层英文、content 层中文(blueprint §8 红线 1)。
