# akira-video

`akira-video` 是 Akira Video 的 Primary Router。它只负责定位已有的 `Vxxx` 或初始化新的独立视频，然后把连续制作交给 `video-production`；Router 不维护第二份流程状态。

## 项目目录

视频项目采用共享资产层 + 单支视频层：

```text
video/
├── INDEX.md                    # 多视频时按需
├── shared/                     # 跨视频复用资产与 shared generations
└── videos/
    └── V001_<human-label>/
        ├── VIDEO.md            # 当前视频唯一主要制作稿
        ├── scenes/             # 长视频按需
        ├── materials/          # 当前视频专属复用资产
        ├── generations/
        ├── shots/              # 个别复杂 Shot 按需
        └── edit/               # 正式后期按需

.tmp/V001/G003_I02/           # 一次性交付包
.tmp/shared/G003_I02/
```

小说、章节、世界观、品牌资料等上游事实继续由原体系拥有；视频目录只保存采用范围、改编结果与当前制作需要的信息。

## 进入制作

已有 `video/videos/Vxxx_*` 时，Router 根据用户明确目标、`video/INDEX.md` 当前指针或唯一可确定的视频选择目标 V；无法可靠判断时才询问。没有视频结构或用户明确创建新视频时，交给 `video-init` 建立最小骨架。

目标 V 确定后立即进入 `video-production`。Production 根据 `VIDEO.md`、共享资产、Generation、Take、Shot 与剪辑事实持续推进，并按真实需要调用 Script、Visual Design、Storyboard、Cinematography、Audio、Generation、Review 和 Editing。

## 外部生成

正式生成以 G / I / Take 组织。一次性交付包只从正式项目内容复制当前执行所需 Prompt、参考素材与说明到项目内 `.tmp/`；返回候选由 Receive 保存回对应 Generation，再进入 Review。包本身不是事实源。

## 可选领域能力

真实品牌 / 产品 / 广告项目按需使用 `video-advertising`。具体模型不维护长期供应商适配 Package；执行当前 G/I 时由 `video-generation` 根据当前官方资料核验真实入口、能力和设置。
