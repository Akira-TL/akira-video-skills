# 可选视频模型适配器

模型适配器不进入 `akira-video` 默认依赖闭包。只有当前任务明确使用对应视频模型时才加载 / 安装。

## 当前 in-progress 适配器

### Runway

Package：`akira-tl/akira-video-skills/video-model-runway`

当前重点：Runway Gen-4.5 Text to Video / Image to Video 提示词编译。

### Google Veo

Package：`akira-tl/akira-video-skills/video-model-veo`

当前重点：Veo 3.1，并严格区分具体 Google 使用入口、stable / preview model 与当前能力。

### Seedance

Package：`akira-tl/akira-video-skills/video-model-seedance`

当前重点：Seedance 2.5 多模态参考、时间线、同步声音、编辑与延长。

同一镜头需要比较多个模型时，生成侧按 `video-generation/references/MODEL-COMPARISON.md` 保持单一镜头身份和可追溯的模型专用提示词，不为每个模型复制项目结构。

## 使用方式

1. 当前会话已经加载对应适配器时直接使用；
2. 缺失时，`akira-video` 只确定最小 Package coordinate；
3. 安装 / 候选计划（Candidate plan）仍交给 `akira` Router 与 Skiloom；
4. 精确 duration、分辨率、输入上限和 endpoint 由适配器在实际使用时核验当前官方资料。

## 图片模型

目前不建立图片模型专用适配器。长期生图提示词、角色 / 场景设计和严格四视图由 `video-design` + `video-materials` 负责；只有未来真实生产反复证明某图片模型存在稳定且不可由通用提示词覆盖的差异时再拆。

## 边界

模型适配器只能编译当前镜头 / 素材意图，不能重新决定剧情、角色设计、产品事实或镜头目的。
