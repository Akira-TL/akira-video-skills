# akira-video

`akira-video` 是 Akira Video 的 Primary Router。它只负责定位已有的 `Vxxx` 或初始化新的独立视频，然后把连续制作交给 `video-production`；Router 不维护第二份流程状态。

## 项目目录

```text
video/
├── INDEX.md
├── shared/
│   ├── characters/CHR01/G001/
│   └── locations/LOC01/G001/
├── V001_<human-label>/
│   ├── VIDEO.md
│   ├── scenes/
│   ├── materials/
│   ├── generations/
│   ├── shots/
│   └── edit/
└── batches/B001/
    ├── README.md
    ├── tasks/
    ├── references/
    ├── returns/
    └── B001.tar.gz
```

小说、章节、世界观、品牌资料等上游事实继续由原体系拥有；视频目录只保存采用范围、改编结果与当前制作需要的信息。

## 进入制作

已有 `video/Vxxx_*` 时，Router 根据用户明确目标、`video/INDEX.md` 当前指针或唯一可确定的视频选择目标 V；无法可靠判断时才询问。没有视频结构或用户明确创建新视频时，交给 `video-init` 建立最小骨架。

目标 V 确定后立即进入 `video-production`。Production 根据 `VIDEO.md`、共享对象、Generation、Take、Shot 与剪辑事实持续推进，并按真实需要调用 Script、Visual Design、Storyboard、Cinematography、Audio、Generation、Review 和 Editing。

## 外部生成

正式生成以 G / I / Take 组织。Generated Take 与 Prompt 共置于原 G。一次实际外部执行按 `video/batches/Bxxx/` 组织，可同时包含多个 G/I；同一参考只复制一次，并就地生成保留的 `Bxxx.tar.gz`。返回候选由 Receive 保存回原 Generation，再进入 Review。

## 可选领域能力

真实品牌 / 产品 / 广告项目按需使用 `video-advertising`。具体模型不维护长期供应商适配 Package；执行当前 G/I 时由 `video-generation` 根据当前官方资料核验真实入口、能力和设置。
