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


从各镜头当前采用的生成结果进入时间线。镜头文件仍以原位置为长期来源；后期工程可以引用、代理或按软件需要管理媒体，但不要为“最终版”在项目中复制多套难以追踪的同源视频。裁切、调色、稳定、替换声音等后期派生不创建新的镜头身份，也不得覆盖原始生成结果；当前项目使用 `video-shot` 时，其镜头身份规则继续由该 Skill 负责。

## 3. 确定性后期

能由后期工具精确完成的任务优先留给确定性后期，例如剪切与时间线、字幕与标题、Logo 和精确排版、画幅适配、简单合成、音量与混音、音视频同步、最终编码和导出。跨模型 / 批次的色彩、曝光、稳定、降噪、放大和质感统一按 [`references/FINISHING.md`](references/FINISHING.md)；能确定性修的差异不重生，但人物身份、产品结构和严重时序错误不能靠 finishing 掩盖。字幕、Logo、标题、产品文字和片尾主卡按 [`references/GRAPHICS-TITLES.md`](references/GRAPHICS-TITLES.md) 处理，不依赖生成模型准确画字。项目需要对白 / 旁白字幕、外挂字幕、烧录字幕、无障碍字幕或多语言字幕时，再读取 [`references/SUBTITLES.md`](references/SUBTITLES.md)，从最终声音 / 文本生成并逐语言、逐画幅检查时序与安全区。

不要因为生成模型可以尝试，就让它重做本可稳定后期解决的问题。

准备最终导出或整片验收时，先按 [`references/FINAL-QC.md`](references/FINAL-QC.md) 检查整片内容，再按 [`references/TECHNICAL-QC.md`](references/TECHNICAL-QC.md) 检查每个正式交付文件能否正常解码以及时长、画幅、分辨率、音轨等明确交付要求。当前环境有 `ffprobe` / FFmpeg 时，优先复用本 Skill 自带 [`scripts/delivery_qc.py`](scripts/delivery_qc.py) 对正式文件执行完整解码和显式参数校验；期望值必须来自 `VIDEO.md` / 客户 / 比赛 / 平台要求，脚本不提供通用交付默认值，也不替代整片内容审查。

## 4. 整片检查

最终成片从头到尾检查剧情/信息连续性、镜头衔接、音乐与对白、字幕/Logo、产品型号或其他交付要求。整片问题要回到对应归属镜头、素材或脚本修改，不在后期工程里静默篡改上游事实。

## 完成标准

整片工程能明确找到当前采用镜头和全片级资源；最终成片满足当前 `VIDEO.md` 的交付要求，且没有产生多套无法判断来源的“final”文件。
