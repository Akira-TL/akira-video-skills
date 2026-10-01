# Repository instructions

本仓库是 `Akira-TL/akira-video-skills` 的 canonical source，维护 Akira 的 AI 视频制作 Skill 产品族。

## 产品边界

- `akira-video` 是 user-invoked Primary Router，只负责定位 / 初始化目标 `Vxxx` 并进入 `video-production`；它不维护第二份流程状态。
- `video-production` 是单支视频唯一流程负责人；Director、Script、Visual Design、Storyboard、Cinematography、Audio、Generation、Review、Editing 是同一 Agent 按需调用的方法。
- 视频 Skill 只拥有 `video/` 下的视频制作内容与当前视频记录。小说、漫画、游戏、品牌资料等上游事实继续由原项目结构拥有；视频只保存 pointer、改编结果和当前制作需要的信息。
- 稳定 Skill 位于 `skills/video/<name>/`；实验能力可放 `skills/in-progress/`；稳定 Skill 人类说明位于 `docs/video/<name>.md`。
- 不维护 Runway / Veo / Seedance 等供应商 Adapter Package；动态模型能力在实际 Generation 执行时核验当前官方资料。

## 项目存储原则

- 多视频导航按需使用 `video/INDEX.md`。
- 每支视频始终位于 `video/videos/Vxxx_<human-label>/VIDEO.md`；正式身份只认 `Vxxx`，助记后缀不参与引用。
- 跨视频复用人物 / 地点 / 道具 / 声音 / 参考放 `video/shared/`；本视频专属复用内容放 `Vxxx/materials/`。
- 正式 Generation 放 `Vxxx/generations/Gxxx*/` 或 `video/shared/generations/Gxxx*/`；Prompt 正文只属于对应 `Ixx`，Take 在 G 内单调递增。
- Shot 与 Generation 多对多。简单视频可以只在 `VIDEO.md` / 场景文件维护唯一 Shot 表；复杂 Shot 才建立独立记录。
- 建立正式剪辑时间线后，最终视频实际采用 Take / 时间范围 / 复用 / 拼接关系只由剪辑记录维护。
- `.tmp/<scope>/Gxxx_Iyy/` 只是可重建 outbound pack；Receive 正式保存真实输入 / Take 后自动精确清理。

## 版本与命名

- Git 保存文本历史；正式投入生成的二进制参考使用 `v01` 起的不可覆盖版本。
- 核心 ID 为 `Vxxx`、`Gxxx`、`Ixx`、`takeNN`、`SCxx`、`SHxxx`、`CHRxx`、`LOCxx`、`PROPxx`、`PRODxx`。
- 文件名不默认编码供应商、模型、seed、FPS、全部参数或 Prompt hash。
- 禁止 `final2` / `new_final` 等伪版本链。

## Skill 编写与依赖

- 每个 Skill 只有一个 canonical `SKILL.md`，目录名与 frontmatter `name` 一致。
- Package metadata 使用 `skiloom-package.toml`；调用策略在 `agents/openai.yaml`。
- Skill 之间通过能力名和明确 pointer 协作，不复制正文；跨 Package direct reference 必须有真实 required dependency。
- 同一正式正文 / Prompt / 最终采用关系只维护一处。

## 修改与检查

- 修改稳定 Skill 时同步更新 `docs/video/<name>.md`。
- 改变用户可达 Skill、路由关系或项目目录契约时同步检查 `README.md`、`CONTEXT.md`、相关 ADR 与 `akira-video`。
- 正式提交前运行 `skiloom validate . --json`、`./scripts/check.sh` 与适用 targeted tests。
