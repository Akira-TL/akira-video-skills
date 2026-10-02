# video-visual-design

`video-visual-design` 统一处理人物、地点、道具 / 虚构机械、整体视觉以及参考资产准备。设计约束、Generation Prompt 和已确认参考图分别表达“应该是什么”“这次生成什么”“实际采用了什么”，不能互相自动覆盖。

跨视频对象默认进入 `video/shared/<category>/<object-id>/`；本视频专属复用对象进入 `Vxxx/materials/`。对象自己的 G 直接放在对象目录内，正式生图 Prompt 与 Generated Take 共置，资产记录直接引用对应 G/take。人物身份 / 全身角色、环境 / 场景、严格四视图都有专用 Prompt 模板；场面调度站位由 Storyboard 的 Blocking 模板处理。
