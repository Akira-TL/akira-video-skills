# video-editing

`video-editing` 只在项目进入整片后期时工作，并按需创建 `video/edit/`。

单镜头内容仍留在对应镜头；整片剪辑工程、全片音乐/旁白/混音、字幕、Logo 和最终成片直接放在 `video/edit/`；字幕、Logo、标题、产品文字与片尾主卡按 `references/GRAPHICS-TITLES.md` 使用确定性后期完成，默认不再拆 `audio/` / `delivery/`。工程与成片命名按 `references/EDIT-PROJECT.md`；粗剪与节奏按 `references/EDITING-RHYTHM.md` 先保证故事 / 信息、动作切点、声音和产品可读性；能由 Premiere Pro、After Effects、DaVinci Resolve 或其他确定性工具准确完成的工作优先在后期处理；跨模型 / 批次的色彩、曝光、稳定、降噪、放大和质感统一按 `references/FINISHING.md`，但不允许用 finishing 掩盖身份、产品结构或严重连续性错误；最终整片内容验收按 `references/FINAL-QC.md` 展开；正式导出文件再按 `references/TECHNICAL-QC.md` 分别检查可解码性、时长、画幅 / 分辨率、音轨和当前交付要求。
