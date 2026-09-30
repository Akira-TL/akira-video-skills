---
name: video-model-veo
description: 为 Google Veo 视频生成编译和检查 Prompt；当 video-generation 需要使用 Veo 的 Text to Video、Image to Video、首尾帧、参考元素或同步声音能力时使用，并先核验具体 Google 使用入口与 model 的当前支持范围。
---

# Video Model Veo

本 Skill 是 Google Veo 模型适配层。它把既有 `SHOT.md` 和复用素材编译成 Veo 当前入口可执行的 Prompt；它不拥有镜头创意、人物事实或产品事实。

## 1. 先确定使用入口和 model

先明确用户实际使用的 Google 入口，例如 Vertex AI、Google 的创作产品或其他明确使用入口，并记录具体 model / mode。

Google 不同使用入口以及 stable / preview model 的能力可能不同。涉及参考图、首尾帧、延长视频、同步声音、分辨率、时长或输入数量时，必须先按 [`references/MODEL-GUIDE.md`](references/MODEL-GUIDE.md) 核验当前官方资料，不能只凭“Veo 3.1”这个家族名称推断。

## 2. 基础 Prompt

当前 Veo 创作指南的通用结构可以压缩为：

摄影语言 → 主体 → 动作 → 环境 / 上下文 → 风格与氛围。

只写当前 Shot 真正需要的部分。动作和表演尽量写成可见行为，而不是抽象心理词。

## 3. Image to Video

输入图已经固定主体和起始构图时，Prompt 重点描述从这个起点发生的动作、摄影和环境变化。

如果当前使用入口支持首尾帧，把首帧 / 尾帧当成两个明确端点，Prompt 主要描述二者之间怎样移动、转变以及声音如何连续；不要让 Prompt 与两张端点图相互矛盾。

## 4. 参考元素 / Ingredients

只有所选使用入口和 model 当前明确支持时，才使用角色、场景、物体或风格参考图。每份参考说明用途，不让多个素材竞争同一个身份。

如果当前官方使用入口不支持该模式，回到可用的 Image to Video、首帧 / 尾帧或普通 Text to Video 路径，不以历史 preview 能力代替当前事实。

## 5. 声音

当前模式明确支持音频生成时，可以在 Prompt 中加入对白、环境声、具体音效和声音出现时机。

声音要求仍服从视频脚本和 Shot，而不是为了展示模型能力增加多余对白或音效。

## 6. 返回 video-generation

输出所选使用入口 / model / mode、当前 Prompt、输入图或参考用途、需要用户在界面确认的时长 / 比例 / 分辨率 / 声音选项；某项能力存在入口差异时明确标注。

长期 Prompt 和一次性 Generation Pack 仍由 `video-generation` 管理。

## 完成标准

没有把不同 Google 使用入口的能力混为一谈；Prompt 与当前 Veo 模式匹配；首尾帧、参考元素和声音只在官方当前支持时启用。
