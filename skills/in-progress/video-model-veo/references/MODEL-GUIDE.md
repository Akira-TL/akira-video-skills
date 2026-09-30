# Veo 当前模型参考

最后人工核验：2026-09-30。

## 重要：不同使用入口的能力不等价

Google 的 Veo 能力会随使用入口、stable / preview endpoint 和产品形态变化。不要把一篇创作指南中展示的能力自动视为所有 Vertex AI stable endpoint 都支持。

2026-03 的 Vertex AI release notes 已要求把 Veo 3.1 preview endpoint 迁移到 stable `veo-3.1-generate-001` / fast 对应 endpoint，因此旧 preview 文档不能直接作为当前 API 契约。

## Vertex AI stable 参考

截至核验日，Google Cloud 的 Veo 3.1 stable 资料明确记录：

- Text to Video；
- Image to Video；
- first + last frame；
- 4 / 6 / 8 秒；
- 16:9 / 9:16；
- 720p / 1080p；
- 24 FPS。

参考图 / ingredients、extension 等能力在不同 Google 页面 / 使用入口上存在差异，因此使用前必须核验所选入口的当前文档。

## Prompt 方法

Google Cloud 的 Veo 3.1 创作指南建议从以下五类信息组织 Prompt：

摄影语言 + 主体 + 动作 + 环境 / 上下文 + 风格 / 氛围。

首尾帧工作流中，让图片负责端点视觉，Prompt 负责二者之间的运动、转变与声音。

## 官方来源

- https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes

如果用户使用的不是 Vertex AI stable endpoint，再查对应 Google 使用入口的官方资料，不从本文件猜。
