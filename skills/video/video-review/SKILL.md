---
name: video-review
description: 审核 AI 生成的图片、视频、声音或音乐候选，依据当前 Generation 目标、正式输入和项目事实判断 usable、revision-needed 或 rejected，并定位应返修的资产、镜头、Prompt、模型执行或后期层。
---

# Video Review

本 Skill 负责**检查真实生成结果并定位问题**。它不拥有最终采用关系，也不因为结果已经生成就降低原有约束。

## 1. 基于真实 artifact

必须查看 / 播放真实返回内容，不能根据 Prompt、文件名或模型预期推断。视频至少覆盖开始、主要动作过程和结束；只能观察部分维度时明确保留未验收项。

媒体元数据、抽帧和严格 2×2 分格可按需使用 [`scripts/media_review.py`](scripts/media_review.py)，但这些只是辅助定位，不能替代完整播放、听音、口型或视觉语义检查。

## 2. 固定审查依据

先读取当前 Take 对应的 G / I、实际参考版本、相关资产 / Shot / 场景和必要上游事实。广告 / 真实产品还必须有 `video-advertising` 的产品事实依据。临时 pack 只帮助定位往返，不高于正式记录。

详细质量检查按 [`references/TAKE-QA.md`](references/TAKE-QA.md)，多候选比较按 [`references/CANDIDATE-SELECTION.md`](references/CANDIDATE-SELECTION.md)，失败分类与修复分别按 [`references/FAILURE-MODES.md`](references/FAILURE-MODES.md) 和 [`references/REPAIR-DECISIONS.md`](references/REPAIR-DECISIONS.md)。

## 3. Review 结论

Generation Review 保持小而明确：

- `unchecked`；
- `usable`：满足当前生成目标，可由消费方决定如何使用；
- `revision-needed`：部分可用或需要修 Prompt / 参考 / 设计 / Shot / 后期；
- `rejected`：不满足当前生成目标。

必要时记录问题范围，例如“6.2 秒后身份漂移”。这些分类针对当前 G 目标，不表示一条 Take 每一帧都可用或都不可用。

## 4. 修哪里

优先定位第一个真正错误的层：视觉资产 / 设计、Script / Storyboard、Cinematography、Generation Prompt / Input、随机模型执行，或确定性后期。目标不变的重生成通常建立新 I；目标改变才新建 G。

## 5. 不维护 selected take

Review 可以判断某个 Take usable，但不写“当前采用 take02”。参考图采用由资产记录维护；视频实际采用在未进入正式剪辑时可记唯一 Shot 表，建立正式剪辑时间线后由剪辑记录唯一维护；声音 / 音乐同理归消费记录。

失败候选也是生产记录，Receive 后先正式保留再 Review；后续媒体清理是独立策略，不在接收 / 审片时偷偷丢结果。

## 完成标准

被审 Take 有清楚的质量判断、问题范围和返修方向；没有把 Review 结论误写成最终采用事实。
