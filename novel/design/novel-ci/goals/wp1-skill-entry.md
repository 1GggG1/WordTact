# WP1 Goal Brief — SKILL.md(入口)

> Historical implementation brief. The current contracts.md and runtime owners supersede conflicting original instructions; follow NEEDS_VERIFICATION, shared rule ownership and proportional regression.

## Mission

编写 `novel-superpower/user/novel-ci/SKILL.md`:novel-ci 的唯一入口,负责触发、路由、流程总图、门禁与模块加载,**不含任何具体测试条目、schema 全文或语言规则**。

## Deliverables

| 文件 | 说明 |
|------|------|
| `user/novel-ci/SKILL.md` | 新建,≤150 行 |

## Required reading(按序)

1. `design/novel-ci/blueprint.md` 全文(重点 §5.3、§6、§7)
2. `design/novel-ci/contracts.md` §1、§5、§6、§10
3. `user/novel-expander/SKILL.md` 与 `user/novel-auditor/SKILL.md` 的 frontmatter——模仿其 description 写法(长触发词表 + 路由边界声明)与 "Reference files | When to load" 表格式

## Content requirements

1. **Frontmatter**:`name: novel-ci`;description 需包含——
   - 中文触发词:新建小说项目、初始化设定库、规划章节、设计场景、scene card、写下一场、跑 review、自审、修补、打 patch、回归检查、更新正典、更新 lockfile、连续写、章节收口等;附英文等价词。
   - 路由边界三句:输入自由大纲求正文且无 CI 项目状态 → novel-expander;仅求成稿诊断 → novel-auditor;涉及项目状态、规格、测试、patch、lockfile 的一切 → 本 skill。
2. **核心原则**(10 条,改写自下列语义,禁止加入评分制):先规格后正文;先 card 后 draft;正文后必测;测试只输出 PASS/FAIL/RISK;failure 必标 P0—P3;默认局部 patch;语言打磨不破坏角色声音;修改后必回归;通过后才更新 lockfile;P0/P1 未清不进下一场景。
3. **流程总图**:转写 blueprint §6(文字版即可,mermaid 可选)。
4. **门禁表**:Gate A—E,转写 contracts §5(压缩为表格,语义不变)。
5. **交互点与 auto 模式**:转写 contracts §6。
6. **模块加载路由表**:转写 blueprint §5.3,注明"任一时刻加载的 reference ≤3 个"。
7. **Reference files 表**:14 个 references/ 文件 × 加载时机(文件名以 blueprint §4 为准)。
8. **Maintainer notes**(英文):语言分层惯例;schema 单一归属(指向 blueprint §5.2);sibling 依赖与 fallback(指向 conventions.md);禁止把 P2/P3 升级为硬门禁。

## Conventions(红线,验收必查)

- blueprint §9 全部适用。meta 层英文、content 层中文。
- 不复制:测试条目(在 checks-*)、schema 全文(在 owner 文件)、语言规则(在 expander)。
- description 写在 frontmatter 单行字符串内,风格对齐现有两个 skill。

## Acceptance checklist

- [ ] ≤150 行;frontmatter 可被 skill 系统解析
- [ ] 触发词覆盖流水线全部 8 个阶段;路由边界与 expander/auditor 的 description 无冲突
- [ ] 门禁表、交互点、加载路由与 contracts/blueprint 语义一致
- [ ] 文中引用的 14 个 reference 文件名与 blueprint §4 完全一致
- [ ] 无测试条目、无 schema 全文、无语言规则条目

## Out of scope

不写任何 references/ 文件;不修改 expander/auditor;不定义新门禁或新交互点。
