# video-shot

`video-shot` 把镜头总览展开成单镜头 `SHOT.md`。镜头数量与景别覆盖按 `references/COVERAGE.md` 从故事、动作、表演、产品可读性和剪辑需要决定，不固定生成大全景 / 中景 / 近景套餐。每个镜头目录集中保存自己的镜头定义、提示词版本、生成结果、镜头专属图片和声音。

默认使用 `SC01_SH010` 这类留空式编号；简单项目也可以直接使用 `SH010`。复杂镜头可以按 `references/SHOT-TEMPLATE.md` 直接建立完整 `SHOT.md`；连续性只记录相邻镜头真正需要继承的内容，不建立全局复杂状态机。复杂摄影、动作和跨世界转场按 `references/DIRECTION.md` 展开；多角色走位、产品 / 机械交互、复杂机位或首尾帧控制确实需要时，再按 `references/PREVIS.md` 做最小预演，不默认创建额外分镜目录；存在多个交付画幅时按 `references/MULTI-FORMAT.md` 判断是否可安全裁切，只有构图语义确实变化时才建立画幅专属生成版本。
