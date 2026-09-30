---
name: video-model-runway
description: 为 Runway 当前视频模型编译和检查生成 Prompt；当 video-generation 需要使用 Runway（当前主线 Gen-4.5）的 Text to Video 或 Image to Video，并需要 Runway 专用动作、摄影和时序表达时使用。
---

# Video Model Runway

本 Skill 是 Runway 模型适配层。它只负责把已经明确的素材 / `SHOT.md` 创作意图编译成 Runway 当前模型更容易执行的 Prompt，并核验所选 Runway 模型的真实输入与时长能力；它不重新决定镜头目的、人物、剧情或产品事实。

## 1. 固定具体模型与生成模式

先明确用户实际使用的 Runway 模型和模式，例如当前主线 Gen-4.5 的 Text to Video 或 Image to Video。

如果用户使用旧 Gen-4 / Gen-4 Turbo、Apps、Agent、Workflows 或其他 Runway 工具，不把 Gen-4.5 的参数直接套用；按 [`references/MODEL-GUIDE.md`](references/MODEL-GUIDE.md) 核验当前官方资料。

涉及精确时长、画幅比例、帧率（Frames Per Second, FPS）、分辨率或输入类型时，必须以当前官方页面为准。

## 2. Image to Video

输入图片已经提供主体、构图、光线和风格时，Prompt 主要描述摄影机运动、主体动作、环境运动、运动方式、方向、速度、时序和当前镜头确实需要发生的变化。

不要把输入图已经清楚表达的静态视觉细节重新长篇描述。只有需要引入新元素、明显变形、交互或改变起始画面时再补视觉说明。

默认从简单、直接的动作描述开始，再按失败模式增加一个主要约束。

## 3. Text to Video

没有输入图片时同时描述视觉与运动。实用结构：

摄影 / 构图 → 主体 → 动作 → 环境 → 必要光线 / 风格 → 时序。

不要求每项都出现。保留必要创作自由度，避免为了“完整”堆出相互矛盾的长 Prompt。

## 4. 时间顺序

复杂动作可以使用自然语言顺序或粗时间戳。时间分配必须符合动作真实所需时间，不为了逐秒控制把简单 Shot 拆成过密指令。

## 5. 正向、直接描述

优先描述想发生什么，而不是列大量否定项。需要静止摄影机时写成明确正向状态，例如“锁定机位，摄影机全程保持不动”。

Hard Constraints 仍由 `SHOT.md` 保存；最终 Prompt 只保留模型当前真正需要执行的表达。

## 6. 返回 video-generation

输出当前 Runway Prompt、建议输入图 / 参考和需要在生成界面确认的参数；长期 Prompt 保存到 owning Shot 的 `prompt_vNN.md`，并行比较多个模型时可以使用清楚的模型后缀。

一次性 Generation Pack 的复制、文件命名和结果导回仍由 `video-generation` 负责。

## 完成标准

Prompt 与具体 Runway 模式匹配；Image to Video 没有重复描述输入图，Text to Video 同时覆盖必要视觉与运动；精确能力已经按当前官方资料核验。
