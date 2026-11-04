# WordTact 通用版：文本润色与日常对话

[English](../README.en.md) · [章回与 WordTact](../README.md)

用于修改已有中文、英文文本中的套路化表达、定语堆叠、从句嵌套和措辞不一致。
普通文章与论文分别处理，保留原意、术语、引用和结论强度。

## 使用

`general/` 通用版内有两项并列技能：

| 目录 | 用途 |
|---|---|
| [wordtact/](wordtact/SKILL.md) | 编辑已有中英文文本与论文，保留含义和作者文风 |
| [conversational-register/](conversational-register/SKILL.md) | 日常用户与 AI 对话，包括解释、讨论和任务反馈 |

它们与 `novel/` 小说版分开维护和分发。将这两个目录一起复制到客户端技能目录，或在
仓库根目录运行通用版安装器：

```sh
python3 general/install.py --dest /path/to/client/skills
```

安装后仍是两个平级目录，不将对话技能嵌入润色技能，也不套用到论文、小说正文或人物
台词。安装器只需 Python 3.10+ 标准库，不联网，不修改客户端配置。相同内容直接复用；
不同版本先报告冲突，明确更新时加 `--replace` 并保留备份。完整用法见 [INSTALL.md](INSTALL.md)。

只复制 `wordtact/` 也能润色且无需 Python；它带有从对话技能生成的交流指导回退。
要让对话技能在日常交流中独立发现，需要同时安装 `conversational-register/`。
普通润色和日常对话不会自行执行安装。

> 用 general/wordtact/SKILL.md 润色这段中文论文，保留专业术语、引用和结论强度。

> Use general/wordtact/SKILL.md to edit this English passage. Keep the house style and all factual limits.

有作者规则、样稿或术语表时一并提供。长文可以指定只改某一节，并提供相关上下文。
主 agent 会询问是否加一位独立评阅者，默认开启；回复“不开”或写明“只由主 agent
完成”即可省去这一步。

## 使用体验与测试

这套工具的许多调整来自实际写作和多轮返修。我个人觉得中文修稿比 Humanizer 直出更可用，
尤其在意代词是否清楚、动作读起来是否连贯，以及润色有没有改变原意。
[这里有几个另写的例子](../README.md#一些来自实际修稿的小问题)。

英文除了测试，只用来写过几篇面向水平不高的 EI 检索会议的论文。我自己觉得比
Humanizer 直出好用，但使用样本很少，不保证适合你的稿子。

六道通用题包含三道自编中文题和三段 IteraTeR 英文学术文本。Luna、Terra 均配置为
max、标准速度，每题三次，由 Astra 评阅。以下为综合可用性的胜／平／负：

| 模型 | 对裸模型 | 对 Humanizer |
|---|---:|---:|
| Luna | 6 / 10 / 2 | 6 / 8 / 4 |
| Terra | 7 / 10 / 1 | 3 / 13 / 2 |

每组共 18 次比较，只看首轮输出。题目、改稿和评分方法见[完整报告](../benchmarks/nine-case/results/2026-10-16/REPORT.md)。

## 开发

在仓库根目录运行：

```sh
python3 -m unittest discover -s general/tests
python3 -m unittest discover -s novel/tests
python3 general/scripts/build_package.py --output /tmp/wordtact-general-YYYYMMDD.zip
```

`tests/` 是开发材料，无需随技能复制。本版采用 [MIT 许可](wordtact/LICENSE)。部分表达检查参考并改编自
[Humanizer-zh](https://github.com/op7418/Humanizer-zh) 和
[Humanizer](https://github.com/blader/humanizer)，上游许可见
[第三方声明](wordtact/THIRD_PARTY_NOTICES.md)。

本 README 由 Codex 根据项目维护者的要求撰写并修订：模型 `gpt-6-astra`，
effort `max`，速度档位 `ultrafast`。文中的第一人称使用经历和评价由维护者提供。
