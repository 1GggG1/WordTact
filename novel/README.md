# 章回（Zhanghui）：中文小说写作与审稿

从构思、规划、扩写到审稿和修订，用同一套工作流持续写一部小说。
[SKILL.md](SKILL.md) 是统一入口，会按任务选择子技能。

| 子技能 | 用途 |
|---|---|
| [novel-conversation](user/novel-conversation/SKILL.md) | 创作过程中 AI 与作者的沟通，随写作工作流自动加载 |
| [novel-dialogue](user/novel-dialogue/SKILL.md) | 人物台词、言语互动与场景中的声音差异，写作和审稿时按需加载 |
| [novel-discuss](user/novel-discuss/SKILL.md) | 讨论方向、构思和质疑方案，形成交接材料 |
| [novel-ci](user/novel-ci/SKILL.md) | 场景规划、草稿、审阅、补丁、回归检查和正典更新 |
| [novel-expander](user/novel-expander/SKILL.md) | 将大纲、人物与世界观笔记、片段扩成正文 |
| [novel-auditor](user/novel-auditor/SKILL.md) | 审查语言、含义、重复和文风，按指定范围修订 |
| [file-tagging](user/file-tagging/SKILL.md) | 维护写作资料库的元数据、标签和关联 |
| [vault-organizer](user/vault-organizer/SKILL.md) | 整理资料库的目录、版本与链接 |

文风依据作者要求、认可的样稿和具体场景。正式汇报、私下对白和日记可以有不同口吻，
人物的习惯、笑话和有意重复也应保留。语言审校会处理定语堆叠、指代不清、套路化
表达等问题，同时检查有没有改动原意、人物动机和知情范围。

作者沟通、人物对白和小说叙述分别处理：讨论方案与解释反馈使用作者沟通指导；实际
台词使用人物对白指导；叙述仍按作者要求、视角和场景选择文风。短对白请求可以直接
使用 novel-dialogue，无需初始化完整项目。

本版只面向中文小说。一般文本与中英文论文使用同仓库 `general/` 下的 WordTact。

## 使用

复制整个本目录，技能 ID 沿用 `novel-superpower`，安装目录可同名。保持 `SKILL.md` 与 `user/`
的相对位置，并保留许可文件，不要只复制入口文件。已有的项目说明、作者约定或样稿可以直接提供。

> 使用这个目录的 SKILL.md，先讨论下一场的冲突和人物选择，不写正文。

> 按给定场景卡扩写这一场，保留角色的口吻和已知信息边界。

> 审查这一章的定语堆叠和措辞漂移，保留正式与私下对白的差别。先定位问题，再按
> 我授权的范围修订。

审稿时会先确定范围和审阅方式；已有安排时沿用。小说稿件、设定和运行记录保存在
写作项目里，与技能源码分开。

## 使用体验

这套工具是我在写小说和反复修稿时逐渐改出来的。我个人觉得比 Humanizer 直出更可用，
所以整理出来分享。

有时体感差别只来自一个代词或一句多余的解释。“姐姐刚坐下，她就把门关上了”，
如果关门的是妹妹，直接写“妹妹”就少一次回读。“我没迟到，是你们来早了”如果是
人物在狡辩，就应该保留这点脾气。这里的例句是根据实际修稿中的问题另写的，不含私人原稿。

## 跑分

三道中文题分别测书信创作、对白修订和动作场景；书信与动作题型借鉴 EQ-Bench
Creative Writing，具体中文材料自编。Luna、Terra 均配置为 max、标准速度，每题三次，
由 Astra 评阅。以下为综合可用性的胜／平／负：

| 模型 | 对裸模型，9 次 | 对 Humanizer，仅修订题 6 次 |
|---|---:|---:|
| Luna | 1 / 5 / 3 | 3 / 2 / 1 |
| Terra | 3 / 2 / 4 | 1 / 3 / 2 |

这些是首轮正文的比较，不包含长期项目管理和多轮返修。完整题目、改稿和评分见仓库
`benchmarks/nine-case/results/2026-10-16/REPORT.md`。

## 开发与构建

自动检查使用 Python 3.10+ 和 PyYAML；修订保护脚本使用 Unix `fcntl`。在本目录运行：

```sh
python3 -m unittest discover -s tests
python3 scripts/validate_source_package.py --skip-archive
```

`scripts/build_source_package.py` 构建小说版源码包，默认按当天日期命名；`--output`
可以指定输出文件，`--replace-existing` 用于替换旧日期包。当前功能以源码为准。

本版采用 [MIT 许可](LICENSE)。部分表达检查参考并改编自 [Humanizer-zh](https://github.com/op7418/Humanizer-zh) 和
[Humanizer](https://github.com/blader/humanizer)，上游许可见
[第三方声明](user/novel-expander/THIRD_PARTY_NOTICES.md)。

本 README 由 Codex 根据项目维护者的要求撰写并修订：模型 `gpt-6-astra`，
effort `max`，速度档位 `ultrafast`。文中的第一人称使用经历和评价由维护者提供。
