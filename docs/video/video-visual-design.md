# video-visual-design

`video-visual-design` 统一处理人物、地点、道具 / 虚构机械、整体视觉以及参考资产准备。设计约束、Generation Prompt 和已确认参考图分别表达“应该是什么”“这次生成什么”“实际采用了什么”，不能互相自动覆盖。

跨视频参考默认进入 `video/shared/`；本视频专属复用资产进入 `Vxxx/materials/`。正式生图 Prompt 只保存在对应 G / I 中，资产记录维护版本来源、当前默认和适用用途；严格四视图仍用于稳定已经确认的设计。
