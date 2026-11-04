# WordTact

[English — WordTact](README.en.md)

两个可以独立安装的版本：中文小说完整版 **章回（Zhanghui）**，以及中英文
通用润色工具 **WordTact**。

| 版本 | 用来做什么 | 语言 | 入口 |
|---|---|---|---|
| 章回（Zhanghui） | 小说构思、规划、扩写、审稿，以及长期文风和设定管理 | 中文 | [novel/](novel/README.md) |
| WordTact 通用版 | 文本与论文润色；日常用户与 AI 对话 | 中文、英文 | [general/](general/README.md) |

小说版根据作者要求、认可的样稿和具体场景保持文风。正式汇报、私下对白和日记可以
各有口吻，不把人物都改成同一种声音。通用版直接处理已有文本，无需小说项目或
Python；论文会额外检查术语、引用、数量关系和结论强度。

## 2026-11-04 更新与下载

通用版新增独立的 `conversational-register`，与 `wordtact` 平级安装，分别负责日常
AI 对话与文本润色。小说版新增 `novel-conversation` 和 `novel-dialogue`，分别处理
作者协作沟通与人物对白，已接入讨论、规划、扩写和审稿流程。

- [下载 WordTact 通用版](https://github.com/1GggG1/WordTact/releases/download/2026-11-04/wordtact-general-20261104.zip)：包含两项技能和可选安装器，见[安装说明](general/INSTALL.md)。
- [下载章回小说版](https://github.com/1GggG1/WordTact/releases/download/2026-11-04/novel-superpower-full-20261104.zip)：保留完整小说工作流，见[使用说明](novel/README.md)。
- [本次发布说明与校验文件](https://github.com/1GggG1/WordTact/releases/tag/2026-11-04)。

## 怎么用

将对应目录放入你使用的 agent 工具所支持的技能目录：

- 章回：复制整个 `novel/`，技能 ID 沿用 `novel-superpower`，安装目录可同名。
- 通用版 WordTact：使用 [通用版安装器](general/INSTALL.md)，将 `wordtact` 与
  `conversational-register` 安装为两项平级技能。

小说版分别提供作者协作沟通与人物对白指导。通用版 `general/` 内并列放置
`wordtact/` 与 `conversational-register/`，分别负责文本润色和日常用户与 AI 对话。
通用版统一打包和安装这两项技能；普通使用不会触发部署。

保留目录结构和随附的许可文件，不要只复制 `SKILL.md`。也可以直接让 agent 读取入口：

> 使用 novel/SKILL.md 审查这一场，改善叠加修饰，保留人物的正式与私下口吻。

> 使用 general/wordtact/SKILL.md 润色这段论文，保留术语、引用和不确定性。

通用版的润色技能会先询问是否加一位独立评阅者，默认开启；不需要时回复“不开”，或在请求中
写明“只由主 agent 完成”。

## 为什么做这个

写作周期一长，有些问题就会反复出现：同一概念换了好几个说法，人物说话越来越像，
或者每段单看都通顺，连着读却总要停下来确认指代和前后关系。很多修改就是我在
实际写作和返修时遇到这些问题后加进去的。

我在中文写作和修稿中，觉得这套工具比 Humanizer 直出的稿子更可用，所以整理出来
分享。这个体会主要来自来回修改长文的过程，固定短题很难测全这些情况。

英文实际用得比较少：除了测试，只写过几篇面向水平不高的 EI 检索会议的论文。
我自己觉得比 Humanizer 直出好用，但样本很少，不保证适合你的稿子。

### 一些来自实际修稿的小问题

下面的例句根据实际遇到的问题另写，用于说明阅读差别，不含私人原稿，也不是工具对照输出。

| 问题 | 例子 |
|---|---|
| 代词让人回头找主语 | “姐姐刚坐下，她就把门关上了。”如果关门的是妹妹，直接写“妹妹”就少一次猜测。 |
| 连续动作被切碎 | “他拉开抽屉。他拿出剪刀。他关上抽屉。”普通连续动作可以合成一句；需要迟疑或特写时，再保留停顿。 |
| 读者刚看懂，又被解释一遍 | “他把最后一块饼干推给孩子”后接“这充分体现了他的关爱”，后一句往往可以删掉。 |
| “没查到”变成“不存在” | 只翻了三份档案，就写“从来没有记录”。“这三份档案里没有记录”才保留了原来的范围。 |
| 人物的脾气被修没了 | “我没迟到，是你们来早了。”可能正是在狡辩，不必为了去掉常见句式，把它改成态度端正的标准答案。 |

## 跑分

九题包含三道中文小说、三道中文通用和三道英文论文润色。书信与动作题型借鉴
[EQ-Bench Creative Writing](https://github.com/EQ-bench/creative-writing-bench)，
英文材料选自 [IteraTeR](https://huggingface.co/datasets/wanyu/IteraTeR_human_sent)，
其余题目自编。

Luna、Terra 均配置为 max、标准速度，每题跑三次，由 Astra 评阅。数字是项目 skill
相对同一模型裸用或加载 Humanizer 的**综合可用性胜／平／负**。

| 范围 | 模型 | 对裸模型 | 对 Humanizer |
|---|---|---:|---:|
| 通用润色，18 次 | Luna | 6 / 10 / 2 | 6 / 8 / 4 |
| 通用润色，18 次 | Terra | 7 / 10 / 1 | 3 / 13 / 2 |
| 书信创作，3 次 | Luna | 0 / 1 / 2 | 不适用 |
| 书信创作，3 次 | Terra | 1 / 0 / 2 | 不适用 |
| 小说修订，6 次 | Luna | 1 / 4 / 1 | 3 / 2 / 1 |
| 小说修订，6 次 | Terra | 2 / 2 / 2 | 1 / 3 / 2 |

通用润色有一些收益，小说创作还不稳定。这些分数比较首轮输出，不包含根据反馈
继续返修的效果。具体题目、原文、改稿和评分方法见[完整报告](benchmarks/nine-case/results/2026-10-16/REPORT.md)。

## 开发

自动检查使用 Python 3.10+，小说版还需要 PyYAML；修订保护脚本使用 Unix `fcntl`。
在仓库根目录运行：

```sh
python3 -m unittest discover -s novel/tests
python3 -m unittest discover -s general/tests
python3 -m unittest discover -s benchmarks/nine-case/tests
python3 novel/scripts/validate_source_package.py --skip-archive
```

小说版的源码包由 `novel/scripts/build_source_package.py` 构建，默认按当天日期命名。
通用版由 `general/scripts/build_package.py --output <外部路径.zip>` 构建，包含两项技能、
安装器、安装说明和文件哈希。对话规则以 `general/conversational-register/SKILL.md` 为准。
`general/` 是通用版，`novel/` 是中文小说版，`benchmarks/nine-case/` 保存公开测试和结果。
各版的 `tests/` 及小说版的 `design/` 契约文档用于开发，无需加载到写作上下文。

## 许可与致谢

本项目采用 [MIT 许可](LICENSE)。第三方材料沿用各自许可；测试集材料的来源与许可见
[SOURCES.md](benchmarks/nine-case/SOURCES.md)。

部分表达检查参考并改编自 [Humanizer-zh](https://github.com/op7418/Humanizer-zh) 和
[Humanizer](https://github.com/blader/humanizer)。上游版权及许可见
[小说版](novel/user/novel-expander/THIRD_PARTY_NOTICES.md)和
[通用版](general/wordtact/THIRD_PARTY_NOTICES.md)的第三方声明。

本 README 由 Codex 根据项目维护者的要求撰写并修订：模型 `gpt-6-astra`，
effort `max`，速度档位 `ultrafast`。文中的第一人称使用经历和评价由维护者提供。
