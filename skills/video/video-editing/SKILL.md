---
name: video-editing
description: 组织单支 Vxxx 的粗剪、正式时间线、合成、全片声音、字幕图文与最终交付；建立正式剪辑时间线后，它成为视频最终实际采用 Take、时间范围、复用和拼接关系的唯一记录来源。
---

# Video Editing

本 Skill 负责单支视频的整片后期。只有真实进入剪辑 / 后期时才创建 `Vxxx/edit/`；工程与输出组织按 [`references/EDIT-PROJECT.md`](references/EDIT-PROJECT.md) 保持最浅可读结构。

## 1. 建立时间线

已有可用素材时可尽早粗剪，不要求全片所有 Generation 先完成。剪辑节奏按 [`references/EDITING-RHYTHM.md`](references/EDITING-RHYTHM.md)，优先解决故事 / 信息、动作切点、反应时长、声音桥接和产品可读性。

## 2. 最终采用关系的唯一来源

正式剪辑时间线建立前，唯一 Shot 表可以暂记候选 / 计划采用来源；一旦建立正式时间线，最终用了哪个 `Vxxx/Gxxx takeNN`、哪个时间范围、同一 Take 是否复用、一个 Shot 是否由多个来源拼接，只由剪辑记录维护。

Shot 保留叙事意图并引用对应剪辑项，不同步维护第二份实际剪辑结果。Generation 也不维护 selected take。

## 3. 媒体与派生

正式 Generation Take 与资产版本保持原位置，不为“final”复制多套来源不清的同源媒体。裁切、调色、稳定、替换声音、多画幅适配等后期派生不创建新 Shot，也不覆盖原始 Take。

跨生成批次的色彩、曝光、稳定、降噪、放大和质感统一按 [`references/FINISHING.md`](references/FINISHING.md)。人物身份、产品结构和严重时序错误不能靠 finishing 掩盖。

## 4. 字幕、Logo 与声音

精确字幕、Logo、标题、产品文字和片尾主卡按 [`references/GRAPHICS-TITLES.md`](references/GRAPHICS-TITLES.md)；字幕与多语言按 [`references/SUBTITLES.md`](references/SUBTITLES.md)。最终声音、音乐、旁白和混音与时间线共同管理。

## 5. 最终 QC

最终内容检查按 [`references/FINAL-QC.md`](references/FINAL-QC.md)，技术参数按 [`references/TECHNICAL-QC.md`](references/TECHNICAL-QC.md)。有 FFmpeg / ffprobe 时优先使用 [`scripts/delivery_qc.py`](scripts/delivery_qc.py) 做完整解码和显式交付参数校验；期望值必须来自当前视频交付要求。

## 完成标准

正式时间线能唯一说明最终成片实际使用的 Generation / Take / 时间范围与整片资源；最终文件满足内容和技术交付要求。
