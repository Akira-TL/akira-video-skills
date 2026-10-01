# AI 视频 Production 流程

本文件描述 `video-production` 的依赖驱动循环，不是固定阶段表。单个 Agent 连贯推进一支 V，专业 Skill 是方法，不是部门交接。

## 1. 恢复

读取当前 `Vxxx/VIDEO.md`、场景正文、共享 / 本视频资产版本、Generations / Takes、唯一 Shot 表和已有正式剪辑记录，并核对真实文件。

## 2. 当前缺口决定下一步

- 整片表达 / 改编策略不清 → Director / Script；
- 人物 / 地点 / 道具 / 参考不足 → Visual Design；
- Shot 结构 / 动作衔接不足 → Storyboard；
- 机位 / 构图 / 运动 / 用光不足 → Cinematography；
- 声音身份 / 声音层设计不足 → Audio；
- 输入齐全 → Generation；
- Take 返回 → Review；
- 已有可用素材 → Editing 可随时粗剪。

不同 G 可以同时处于不同进度。不要因为一个分支等用户生图就停止另一个已经 ready 的视频包或粗剪。

## 3. 常见循环

已有参考 → 直接视频 G；缺参考 → 图片 G → 用户生成 → Receive → Review → 固定资产版本 → 根据真实图片写 / 调整视频 I → 用户生成视频 → Receive → Review。

图片 / 视频结果暴露问题时只回修真实根因：设计 / 资产版本、Script / Storyboard、Cinematography、Prompt / I、模型能力或确定性后期。生图和视频生成可以多轮交替。

## 4. Generation 与 Shot 解耦

一个 G 可以计划覆盖多个 Shot，一个 Shot 可以由多个 G / Take 拼接。G 记录计划覆盖范围；真正实际采用在无正式时间线时可暂记唯一 Shot 表，建立正式剪辑后以剪辑记录为唯一来源。

## 5. 人工外部生成

生成由用户外部执行时，Agent 交付自包含 `.tmp/<scope>/Gxxx_Iyy/`。只暂停依赖该结果的分支，其他独立工作继续。恢复规则见 [`WAITING-RESUME.md`](WAITING-RESUME.md)。

## 6. 结束

一轮 Production 在用户限定范围完成、当前可做事项都推进到真实依赖边界、或需要等待用户 / 真实资料时自然结束。不要因为某个 Skill 调用完成就机械停下。
