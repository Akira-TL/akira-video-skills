---
name: video-storyboard
description: 把当前剧情和导演意图组织成可制作的 Shot List；当需要决定为什么切这一镜、展示什么、动作如何衔接、预计持续多久、计划连续性、Storyboard 或 Animatic 时使用，并与 Cinematography 共同完善同一 Shot 记录。
---

# Video Storyboard

本 Skill 负责**镜头的叙事结构与时间设计**。它不拥有第二套摄影表，也不要求每个 Shot 建独立目录。

## 1. 先判断镜头是否必要

从当前 `VIDEO.md` / 场景正文和 Director 意图拆镜头。建立镜头、反应、插入、产品特写等是否真实有用按 [`references/planning/COVERAGE.md`](references/planning/COVERAGE.md)；不机械生成 coverage 套餐。

一个 Shot 至少回答：为什么存在、展示什么、主要动作 / 信息是什么、从什么状态进入、结束时留下什么、预计持续多久。

## 2. Shot 记录按规模出现

默认使用留空式编号，例如 `SH010`、`SH020`；需要场景前缀时可以使用 `SC01_SH010`。

简单视频可以直接在 `VIDEO.md` 的唯一正式 Shot 表中维护全部镜头；长视频拆到 `SCxx.md` 后就在场景文件维护。只有某个 Shot 真的需要大量独立资料时才创建 `Vxxx/shots/<shot-id>/` 或独立 Shot 文件。

一旦正文或最终采用关系迁到更具体的正式记录，原位置只留概要与导航，不同步维护第二份。

复杂 Shot 的字段边界可参考 [`references/planning/SHOT-TEMPLATE.md`](references/planning/SHOT-TEMPLATE.md)，但模板不是必填表。

## 3. 与 Cinematography 共同完善

Storyboard 负责：为什么切、展示什么、动作如何衔接、持续多久。`video-cinematography` 负责：从哪里看、怎样构图 / 运动、透视 / 焦点和镜头级用光。二者共同修改同一 Shot，不是严格前后两个阶段。

多人接触、递物、手部操作、复杂遮挡或机械交互按 [`references/direction/INTERACTION.md`](references/direction/INTERACTION.md)，先明确主动作角色、手、接触点和动作前后状态。

## 4. 连续性与实际出口

计划连续性按 [`references/continuity/CONTINUITY-HANDOFF.md`](references/continuity/CONTINUITY-HANDOFF.md)：区分世界空间、屏幕方向、角色自身左右、物体状态和计划出口。

生成返回后的实际出口不是 Storyboard 自己维护的另一套事实；Review 负责检查，正式采用来源在尚未建立剪辑时可以写入唯一 Shot 表。建立正式剪辑时间线后，最终用了哪条 Take、哪个时间范围和拼接关系以剪辑记录为准，Shot 保留叙事意图并引用对应剪辑项。

## 5. Storyboard / Animatic 按需

需要在昂贵生成前验证镜头顺序、动作、对白、节奏或产品可读性时，按 [`references/planning/PREVIS.md`](references/planning/PREVIS.md) 做最小必要 Storyboard / Animatic。Animatic 需要基本画面和时间设计后才有意义，不能只在“镜头拆分”完成后机械生成。

多画幅按 [`references/planning/MULTI-FORMAT.md`](references/planning/MULTI-FORMAT.md)；镜头后期派生与新 Shot 的边界按 [`references/continuity/SHOT-DERIVATIVES.md`](references/continuity/SHOT-DERIVATIVES.md)。

## 完成标准

当前视频 / 场景已有一份唯一、可读的 Shot List；每个镜头的叙事目的、动作衔接、预计时长和必要连续性足够清楚，并能与 Cinematography / Generation 继续迭代。
