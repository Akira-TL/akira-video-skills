# video-init

`video-init` 只负责建立最小 Akira Video 项目骨架。新视频直接放在 `video/Vxxx_<human-label>/`，身份只认 `Vxxx`；默认只创建当前视频的 `VIDEO.md`，其他目录在真实需要时再出现。

共享人物 / 地点等对象按需放在 `video/shared/<category>/<object-id>/`；对象自己的 Generation 与 Prompt / Take 共置。外部执行批次在真实需要时由 `video-generation` 创建 `video/batches/Bxxx/`。

它不会询问或决定剧情、时长、广告策略、视觉风格、人物设计或镜头方案；创作与制作推进交给 `video-production`。
