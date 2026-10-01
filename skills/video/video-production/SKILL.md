---
name: video-production
description: 连续推进一支 Akira Video，从当前 VIDEO.md、共享资产、Generation 返回与剪辑事实恢复状态，识别所有当前可做事项，并按需调用导演、剧本、视觉设计、分镜、摄影、声音、生成、审片与后期方法；它是单支视频唯一流程负责人。
---

# Video Production

`video-production` 是当前一支视频的**唯一流程负责人**。它不模拟部门交接，也不复制各专业 Skill 正文；同一个 Agent 从当前正式记录恢复事实，加载需要的方法，并持续推进所有没有真实依赖阻塞的工作。完整依赖循环见 [`references/workflow/PRODUCTION-FLOW.md`](references/workflow/PRODUCTION-FLOW.md)，事实优先级见 [`references/workflow/AUTHORITY.md`](references/workflow/AUTHORITY.md)，昂贵动作前只运行适用的 [`references/workflow/PRODUCTION-GATES.md`](references/workflow/PRODUCTION-GATES.md)。

## 1. 恢复当前事实

先定位当前 `Vxxx`，读取 `Vxxx/VIDEO.md`、已拆出的 `scenes/`、当前实际使用的共享 / 本视频资产版本、已有 `generations/` 与 Take、当前 Shot 表 / 独立 Shot 记录，以及已建立时的正式剪辑记录。同时检查真实文件，不只相信聊天历史或状态文字。

`VIDEO.md` 的当前摘要只保留当前阻塞、待用户操作的包、正在处理的事项和下一步。具体写法见 [`references/project/VIDEO-HOME.md`](references/project/VIDEO-HOME.md) 与 [`references/project/RECORDING.md`](references/project/RECORDING.md)；已有媒体接管按 [`references/project/IMPORT-MEDIA.md`](references/project/IMPORT-MEDIA.md)，媒体清理按 [`references/project/MEDIA-LIFECYCLE.md`](references/project/MEDIA-LIFECYCLE.md)，项目变长时按 [`references/project/SCALING-VERSIONS.md`](references/project/SCALING-VERSIONS.md) 渐进拆分。最终采用关系按真实归属记录，不复制进状态摘要。

## 2. 决定现在能做什么

每轮都从依赖关系判断，而不是套固定 Stage：

- 剧情 / 表达仍不清楚 → `video-director` / `video-script`；
- 人物、地点、道具或长期参考不足 → `video-visual-design`；
- 需要形成 / 修订 Shot List、动作衔接或 Animatic → `video-storyboard`；
- 需要确定机位、构图、运动、透视、焦点或镜头级用光 → `video-cinematography`；
- 声音身份或声音设计需要处理 → `video-audio`；
- 当前目标已有足够输入，可以生图 / 生视频 / 生声音 → `video-generation`；
- 返回结果尚未检查 → `video-review`；
- 已有足够可用素材，可以粗剪 / 正式剪辑 / 交付 → `video-editing`。

广告 / 真实产品命中时按需加载可选 `video-advertising`。

## 3. 同时推进独立分支

Production 不存在“整支视频现在只能处于图片阶段 / 视频阶段”。例如 G001 可以等用户补图，G002 同时准备视频包，G003 进入 Review，前半片同时粗剪。只暂停依赖缺失输入的分支。

## 4. 生图与视频生成允许多轮交替

常见循环：有合适参考资产就直接准备视频 Generation；缺参考先做图片 Generation；图片返回 Review 后形成正式资产版本；再根据**实际采用的图片**完成或调整视频 Prompt；视频返回暴露问题时只回修真正出错的层。必要时再次补图、换图、改 Shot 或新建 Input Version。

G / I / Take 负责追溯，不决定制作顺序。

## 5. 人工暂停点

只在用户必须做高影响创意选择、需要外部生成、需要真实素材 / 权限 / 来源，或当前工作真正依赖尚未返回结果时停止对应分支。等待用户时给出可直接使用的 outbound pack 路径和需要带回的内容，并按 [`references/workflow/WAITING-RESUME.md`](references/workflow/WAITING-RESUME.md) 保持可恢复断点；其他独立工作继续推进。多语言字幕、旁白、配音或成片版本按 [`references/workflow/LOCALIZATION.md`](references/workflow/LOCALIZATION.md) 复用同一视频事实与资产，不复制整套项目。

## 6. 完成判断

完成看当前交付是否齐全，而不是“所有 Generation 是否完成”：需要的剧情 / 信息都有可用素材；正式剪辑中的实际采用来源清楚；必要声音、字幕、图文和合成完成；最终成片输出；内容 Review 与技术 QC 满足交付要求；没有影响当前交付的真实 Blocker。

## 完成标准

当前视频所有可推进事项都已推进到真实依赖边界；状态摘要与实际文件一致；没有为了 Skill 边界制造形式性交接。
