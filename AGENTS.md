# Repository instructions

本仓库是 `Akira-TL/akira-video-skills` 的 canonical source，维护 Akira 的 AI 视频制作 Skill 产品族。

## 产品边界

- `akira-video` 是视频制作 Primary Router，拥有 `VIDEO.md`、视频制作入口、当前制作状态恢复、专业 Skill 路由与一次性生成包总边界；它不复制各专业 Skill 正文。
- 视频 Skill 只拥有项目根目录 `VIDEO.md` 与 `video/` 下的视频制作内容。小说、漫画、游戏、品牌资料库或其他上游内容仍由各自 Skill / 项目结构拥有；视频 Skill 只读取并转换当前制作真正需要的信息。
- 稳定 Skill 位于 `skills/video/<name>/`；尚未稳定的模型适配或实验能力位于 `skills/in-progress/`；弃用能力位于 `skills/deprecated/`。
- 稳定 Skill 的人类说明位于 `docs/video/<name>.md`。
- 长流程、低频分支和详细契约放在对应归属 Skill 的 sibling `references/`；Skill 之间通过名称和能力契约协作，不复制彼此正文。

## 视频项目存储原则

视频项目默认采用浅层、面向人的目录：

- 根目录 `VIDEO.md`：当前视频制作首页和导航。
- `video/script/`：视频脚本层，只保存视频化后的 `SCRIPT.md`、`CHARACTERS.md`、`SCENES.md`、`SHOTS.md` 等实际需要文件。
- `video/materials/`：跨镜头复用的提示词、图片、官方素材、道具、产品、角色声音定义 / 声音参考与其他素材；按真实内容再创建子目录，不预生成空分类。
- `video/shots/<shot-id>/`：单镜头自己的 `SHOT.md`、提示词版本、生成图片/视频、镜头专属音频和其他产物。
- `video/edit/`：只有进入整片后期时才创建，保存 Premiere Pro、After Effects、DaVinci Resolve 等整片工程、全片音频和最终成片。
- `.tmp/`：一次性生成包；从正式项目资料复制或编译而来，不进入 Git，导回生成结果并归档后删除。

项目复杂度增加时允许在 `video/shots/` 内增加章节等组织层，但默认保持最浅可读层级。

## 版本与命名

- Git 保存长期文本与规则演化，不在目录中复制 `final`、`final2`、`new_final` 等伪版本。
- 同一镜头的提示词允许保留少量明确版本，例如 `prompt_v01.md`、`prompt_v02.md`。
- 同一镜头的生成结果使用清楚的生成结果编号，例如 `take01.mp4`、`take02.mp4`；如果文件离开镜头目录，再使用完整镜头 ID 保持可识别性。
- 镜头 ID 默认使用留空式编号，例如 `SC01_SH010`、`SC01_SH020`，便于中间插入镜头；没有场次的简单项目可以直接使用 `SH010`。
- 文件名只编码人真正需要区分的信息，不把模型、供应商、全部参数或状态机塞入文件名。

## 调用与安装

每个 Skill 维护标准 `SKILL.md`、`skiloom-package.toml` 与适用的 `agents/openai.yaml`。仓库发现范围由根目录 `skiloom-repo.toml` 定义。调用边界见 `.agents/invocation.md`。

运行时安装、依赖解析、Source、Registry / Store / Target 与 install/update/remove/sync/repair/recovery 统一由 Skiloom public CLI 负责；本仓不维护私有安装器或执行器目录链接。

## 修改与检查

- 修改稳定 Skill 时同步更新 `docs/video/<name>.md`。
- 改变用户可达 Skill、路由关系或项目目录契约时同步检查 `README.md`、`CONTEXT.md` 与 `akira-video`。
- 同一规则只保留一个唯一权威来源。
- 正式提交前运行 `skiloom validate . --json`、`./scripts/check.sh` 与适用 targeted tests。
