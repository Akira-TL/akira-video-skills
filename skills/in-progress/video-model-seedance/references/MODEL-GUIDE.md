# Seedance 当前模型参考

最后人工核验：2026-09-30。

## 当前重点

BytePlus / ModelArk 当前公开 Dreamina Seedance 2.5 的视频生成与 Prompt 指南。

截至核验日，官方教程记录：

- 普通生成时长（duration）：4–30 秒，或使用智能 duration；
- 图片最多 30；
- 视频最多 10，合计参考时长不超过 30 秒；
- 音频最多 10，合计参考时长不超过 30 秒；
- 官方仍建议参考数量保持克制，较少主体和较短参考通常更稳定；
- video editing、extension、storyboard 等任务模式有各自输入和参数规则。

这些是上限，不是推荐目标。

## Prompt 方法

官方 2.5 Prompt 指南强调：

- 每份 reference 先说明用途；
- 抽象情绪转成可见动作；
- 复杂任务可以使用 Main Idea + Timeline；
- Camera / Action / Sound / Atmosphere 保持同一方向；
- 最重要的 consistency 和 constraints 清楚写出；
- 简单任务不需要为了结构写长 Prompt。

## Video editing

官方文档要求编辑任务包含明确编辑意图，例如 add / remove / replace / modify 等，并有与输入视频时长、ratio、output format 相关的专门规则；使用时必须按所选使用入口当前文档复核。

## 官方来源

- https://docs.byteplus.com/en/docs/modelark/seedance-2-5-prompt-guide
- https://docs.byteplus.com/en/docs/modelark/video-generation-tutorial
- https://ai.byteplus.com/resources/how-to-write-better-seedance-2-5-prompts
- https://docs.byteplus.com/en/docs/ModelArk/ark-document-skills

BytePlus 还提供官方 `sd25-pe` Prompt 优化 Skill；本仓不复制其正文，本适配器只吸收可由官方文档核验的模型约束与 Prompt 方法。
