---
name: akira-video
description: 进入 Akira Video 项目，定位当前视频或初始化新的 Vxxx，然后交给 video-production 连续推进；它是 Primary Router，不复制专业制作方法或维护第二份流程状态。
---

# Akira Video

`akira-video` 是 Akira Video Skills 的 Primary Router。它只负责**找到正确的视频项目与目标 V，并进入 Production**；整支视频的持续推进由 `video-production` 唯一负责。

## 1. 进入项目

先检查当前项目是否已有 `video/`：

- 没有视频结构，或用户明确要创建新的独立视频 → 加载 `video-init`；
- 已有 `video/Vxxx_*` → 根据用户明确目标、`video/INDEX.md` 当前指针或唯一可确定的视频选择 V；
- 多个 V 都可能是目标且现有事实无法判断时，才向用户确认。

V 的正式身份只认 `Vxxx`，不依赖目录助记后缀。小说、世界观、品牌资料等上游事实继续沿原体系读取，不搬进视频目录建立第二份来源。

## 2. 交给 Production

目标 V 确定后，加载 `video-production`。Router 不再按 Director / Script / Visual Design / Storyboard / Generation / Review 等阶段反复接回控制权，也不在自己这里维护一份当前流程状态。

`video-production` 根据 `VIDEO.md`、共享资产、Generation、Take、Shot 与剪辑事实决定下一步，并按需加载默认核心方法 Skill。

## 3. 可选领域能力

品牌、真实产品或广告项目需要 `video-advertising` 时，由 Production / 当前专业方法按需加载。若当前 Target 未安装，使用明确 coordinate `akira-tl/akira-video-skills/video-advertising` 交给 `akira` Router / Skiloom 生成候选计划并由用户授权安装。

具体图片 / 视频模型不建立长期 Adapter Skill。执行某个模型时，由 `video-generation` 根据当前官方资料核验真实入口、能力和设置；模型限制不能反向改写剧情、资产或 Shot 事实。

## 4. 停止边界

Router 自身只在项目 / 目标 V 无法可靠确定时停止。进入 Production 后，由 Production 判断用户限定范围是否完成、哪个分支需要等待人工外部生成或是否存在真实 Blocker。

## 完成标准

已经可靠定位或创建当前 `Vxxx`，并把后续连续制作交给 `video-production`；Router 没有复制专业规则或形成第二套状态。
