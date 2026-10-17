# WordTact：中英文通用润色

[English](../README.en.md) · [章回与 WordTact](../README.md)

用于修改已有中文、英文文本中的套路化表达、定语堆叠、从句嵌套和措辞不一致。
普通文章与论文分别处理，保留原意、术语、引用和结论强度。

## 使用

复制整个 [wordtact/](wordtact/SKILL.md) 目录，放入你的 agent 工具支持的技能
目录即可。保留其中的 `SKILL.md`、`references/`、`LICENSE` 和 `THIRD_PARTY_NOTICES.md`。
无需小说项目或 Python，也可以直接指定入口：

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
```

`tests/` 是开发材料，无需随技能复制。本版采用 [MIT 许可](wordtact/LICENSE)。部分表达检查参考并改编自
[Humanizer-zh](https://github.com/op7418/Humanizer-zh) 和
[Humanizer](https://github.com/blader/humanizer)，上游许可见
[第三方声明](wordtact/THIRD_PARTY_NOTICES.md)。

本 README 由 Codex 根据项目维护者的要求撰写并修订：模型 `gpt-6-astra`，
effort `max`，速度档位 `ultrafast`。文中的第一人称使用经历和评价由维护者提供。
