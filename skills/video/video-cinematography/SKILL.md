---
name: video-cinematography
description: 设计 AI 视频 Shot 的摄影实现；当需要决定机位、构图、景别、焦段/透视、摄影运动、轴线、视线、景深、焦点、曝光或镜头级用光时使用，并与 Storyboard 共同完善同一 Shot 记录。
---

# Video Cinematography

本 Skill 负责回答：**这一镜从哪里看、怎样构图、如何运动、怎样用光。** 它与 `video-storyboard` 共同完善同一份 Shot 记录，不建立第二份摄影镜头表。

## 1. 从镜头意图出发

先读取当前 Shot 的叙事目的、动作、空间与已有视觉设计。摄影必须服务信息、关系、空间和情绪，不为了“电影感”机械增加复杂术语或运镜。景别、焦段 / 透视、推拉与变焦、机位高度、景深 / 焦点和产品摄影按 [`references/CAMERA-LANGUAGE.md`](references/CAMERA-LANGUAGE.md)。

## 2. 轴线、视线与运动方向

多人物、反打、越轴、动作匹配和屏幕运动方向按 [`references/DIRECTION.md`](references/DIRECTION.md)。角色自身左右、世界空间方向和屏幕方向必须区分；反打不是简单水平镜像。

## 3. 镜头级灯光

Visual Design 可以定义地点 / 世界的基础光源、时间状态和材质逻辑；本 Skill 负责当前 Shot 如何利用这些条件，包括主体可读性、阴影、曝光、临时光效和反射。不要用后期调色替代错误光线几何，也不要为了单镜头效果破坏已建立的地点光源连续性。

## 4. 与 Storyboard 共同迭代

如果摄影方案使原 Shot 的动作、时长或空间关系无法成立，直接回到同一 Shot 调整，而不是先把 Storyboard “交付完成”再另起摄影版本。Animatic 需要基本画面 / 时间设计后才有验证意义。

## 完成标准

当前 Shot 的观察位置、构图、运动、透视、焦点和必要用光足以支持后续生成 / 预演，且与叙事目的和既有视觉世界一致。
