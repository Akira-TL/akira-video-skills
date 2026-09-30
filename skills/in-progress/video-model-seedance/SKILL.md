---
name: video-model-seedance
description: 为 ByteDance / BytePlus Seedance 当前视频模型编译和检查提示词；当 video-generation 需要使用 Seedance 2.5 的参考素材、时间线、同步声音、视频编辑、延长或多镜头能力时使用。
---

# Video Model Seedance

本 Skill 是 Seedance 模型适配层。开始前遵守依赖 `video-generation` 的统一模型适配器契约；本文件只保存 Seedance 专用差异。它从既有 `SHOT.md`、复用素材和声音要求编译 Seedance 当前模型提示词，不重新决定镜头创意或长期项目事实。

## 1. 固定具体模型 / 使用入口 / 任务模式

先确认用户实际使用的 Seedance 版本、使用入口和任务类型。当前重点适配 Seedance 2.5；若用户使用 2.0、1.5 或第三方 Router，不把 2.5 的参数直接套用。

常见任务模式：

- reference-based generation；
- 普通视频生成；
- storyboard / keyframe；
- video editing；
- extension；
- audio / voice reference。

精确时长和参考素材限制按 [`references/MODEL-GUIDE.md`](references/MODEL-GUIDE.md) 当前核验。

## 2. 先映射参考素材

Seedance 参考生成首先把每份输入说明清楚：

- 哪个是人物 / 主体；
- 哪个是场景；
- 哪个负责产品或道具结构；
- 哪段视频只参考动作 / 摄影；
- 哪段音频负责声音或音色。

不要让一个参考视频默认同时传递人物身份、服装、环境和动作。只声明当前希望迁移的部分。

## 3. 结构化提示词

复杂 reference-based 镜头可以按需要组织为：

1. reference mapping；
2. main idea；
3. timeline；
4. consistency；
5. essential constraints。

简单镜头不要求机械写满五段。结构只用于减少歧义，不用于把提示词拉长。

## 4. Timeline

Seedance 适合在较长生成中使用清楚时间线。时间段描述当前看到什么、谁做什么、摄影机怎样移动、对白 / 声音何时发生以及下一段怎样承接。

动作数量必须和所选 duration 匹配。多个内部硬切只有在当前镜头设计本来就需要时使用。

## 5. 一致性

只锁真正需要持续的内容，例如人物身份、产品结构、场景、服装、摄影风格或声音。与 reference 映射重复的信息不要在提示词中无休止复述。

## 6. 编辑 / 延长

Video editing 模式下明确使用编辑动作词，并只修改用户指定内容；未要求变化的内容尽量保持。

Extension 任务优先保持输入 / 输出格式和视听连续性；精确格式要求按当前官方使用入口复核。

## 7. 返回 video-generation

输出 Seedance model / 使用入口 / 任务模式、按上传顺序写清的 reference mapping、当前提示词、duration / ratio / output format 等用户需要确认的设置，以及每份参考的明确用途。

一次性生成包和结果导回仍由 `video-generation` 负责。

## 完成标准

每份 Seedance 参考都有明确职责；提示词结构与任务模式匹配；时间线没有超过实际 duration；精确能力来自当前官方资料而不是模型记忆。
