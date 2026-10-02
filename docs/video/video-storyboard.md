# video-storyboard

`video-storyboard` 维护 Shot List 的叙事结构：为什么切这一镜、展示什么、动作如何衔接、预计持续多久和计划连续性。简单视频可以直接在 `VIDEO.md` 维护唯一 Shot 表；长视频按需拆到场景或独立 Shot 记录。

`video-cinematography` 与它共同完善同一 Shot，不另建摄影镜头表。复杂人物站位、运动路径、道具关系和摄影轴可以先用场面调度（Blocking）专用提示词生成空间参考。建立正式剪辑时间线后，最终 Take / 时间范围 / 拼接关系以剪辑记录为准，Shot 只保留叙事意图并引用剪辑项。
