# Runway 当前模型参考

最后人工核验：2026-09-30。

精确能力会变化；当这些数值影响 Generation Pack 时重新检查官方页面。

## 当前主线

Runway 官方当前把 Gen-4.5 作为最新视频生成模型，并提供 Text to Video 与 Image to Video。

截至核验日，官方 Gen-4.5 创建指南记录：

- duration：2–10 秒；
- Text to Video：文本输入；
- Image to Video：文本 + 图片输入；
- 输出 720p；
- 24 / 25 FPS；
- Image to Video Prompt 主要描述运动；
- Text to Video Prompt 同时描述视觉与运动。

## Prompt 原则

Runway 当前 Prompt 指南反复强调：

- 从简单 Prompt 开始；
- 直接描述可见动作和摄影；
- Image to Video 不重复静态输入图已经定义的内容；
- 复杂动作可以使用自然语言顺序或粗时间戳；
- 迭代时尽量一次增加或改变一个主要元素。

## 官方来源

- https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5
- https://help.runwayml.com/hc/en-us/articles/42460036199443-Text-to-Video-Prompting-Guide
- https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide
- https://help.runwayml.com/hc/en-us/articles/47313698911891-Introduction-to-Prompting
- https://help.runwayml.com/hc/en-us/articles/46749315925395-Camera-Terms-Prompts-Examples

旧 Gen-4 / Gen-4 Turbo 的 5 / 10 秒等规则不自动代表 Gen-4.5。
