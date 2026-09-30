---
name: video-editing
description: 组织整片级剪辑、合成、全片声音和最终成片；当多个已采用镜头需要进入 Premiere Pro、After Effects、DaVinci Resolve 等后期工程，或需要整片字幕、Logo、音乐、混音、比例版本和最终导出时使用。
---

# Video Editing

本 Skill 只拥有整片级后期。单镜头自己的视频、图片、对白或声音继续留在对应 `video/shots/<shot-id>/`；跨镜头复用素材继续留在 `video/materials/`。

## 1. 按需创建 edit

整片后期目录与导出命名按 [`references/EDIT-PROJECT.md`](references/EDIT-PROJECT.md) 保持最浅结构。


只有项目真实进入整片后期时才创建 `video/edit/`。目录可以直接保存：

- Premiere Pro、After Effects、DaVinci Resolve 或其他后期工程；
- 全片级音乐、旁白、混音；
- 字幕、Logo、标题或合成所需资源；
- 审片导出和最终成片。

不为了目录整齐再拆 `audio/`、`delivery/` 等一级目录；只有真实文件数量已经影响阅读时才增加子目录。

## 2. 组装当前采用镜头

已有多个采用镜头进入粗剪时，读取 [`references/EDITING-RHYTHM.md`](references/EDITING-RHYTHM.md)，先解决故事 / 信息、动作切点、反应时长、声音桥接和产品可读性，再考虑装饰性转场。


从各镜头当前采用的生成结果进入时间线。镜头文件仍以原位置为长期来源；后期工程可以引用、代理或按软件需要管理媒体，但不要为“最终版”在项目中复制多套难以追踪的同源视频。

## 3. 确定性后期

能由后期工具精确完成的任务优先留给确定性后期，例如剪切与时间线、字幕与标题、Logo 和精确排版、画幅适配、简单合成、音量与混音、音视频同步、最终编码和导出。

不要因为生成模型可以尝试，就让它重做本可稳定后期解决的问题。

准备最终导出或整片验收时，先按 [`references/FINAL-QC.md`](references/FINAL-QC.md) 检查整片内容，再按 [`references/TECHNICAL-QC.md`](references/TECHNICAL-QC.md) 检查每个正式交付文件能否正常解码以及时长、画幅、分辨率、音轨等明确交付要求。

## 4. 整片检查

最终成片从头到尾检查剧情/信息连续性、镜头衔接、音乐与对白、字幕/Logo、产品型号或其他交付要求。整片问题要回到 owning 镜头、素材或脚本修改，不在后期工程里静默篡改上游事实。

## 完成标准

整片工程能明确找到当前采用镜头和全片级资源；最终成片满足当前 `VIDEO.md` 的交付要求，且没有产生多套无法判断来源的“final”文件。
