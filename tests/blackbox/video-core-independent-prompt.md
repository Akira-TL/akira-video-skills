# Akira Video 核心流程独立黑盒验收

你正在执行 Akira Video 核心工作流的**独立黑盒验收**。

这是验收任务，不是实现任务。不要修改 Akira Video Skills 源码。

## 1. 固定输入

- Video Skills repository：`<VIDEO_REPO>`
- 预期 repository HEAD：`<EXPECTED_HEAD>`
- fixture：`<FIXTURE_ROOT>`

仓内参考 fixture：

`tests/blackbox/fixtures/video-core-001`

## 2. 开始前完整性

记录：

- Video repo HEAD；
- Video repo `git status --porcelain`；
- fixture tracked input 状态；
- `akira-video` 及其实际加载的专业 Skill；
- 当前默认 dependency closure。

HEAD 不等于 `<EXPECTED_HEAD>` 时停止产品验收：

`inconclusive — fixed point mismatch`

不要自行 reset / checkout。

## 3. 只读与写入边界

禁止修改：

- Video Skills 源码；
- fixture `source/`；
- fixture 其他 tracked input。

本次所有项目产物只能写入：

`<FIXTURE_ROOT>/output/project/`

验收报告只能写入：

`<FIXTURE_ROOT>/output/report/`

`output/` 必须保持 ignored。

## 4. 用户任务

把 `<FIXTURE_ROOT>/source/brief.md` 视为用户提供的完整上游 brief。

使用实际 `akira-video` Skill 及其依赖，从零建立一个**最小可执行**视频项目。

用户将在外部图片模型中自己生成第一批角色 / 场景参考。你必须把这批一次性生成包准备好，然后在真实外部结果返回前停止依赖它们的下游。

不要调用真实图片 / 视频生成服务。

## 5. Phase A — 项目入口

在 `output/project/` 建立项目。

验证：

- 根目录有 `VIDEO.md`；
- 视频内容只进入 `video/`；
- 第一次需要生成包时项目 `.gitignore` 忽略 `.tmp/`；
- 没有默认创建 `audio/`、`delivery/`、`assets/`、数据库或复杂状态目录；
- 上游 brief 不被完整复制成第二份事实源。

## 6. Phase B — 最小脚本层

根据 brief 建立当前真正需要的视频脚本层。

本 fixture 是无对白、简单三镜头短片。

验收重点：

- 至少有清楚的镜头总览；
- 不为了模板完整强制建立无内容的 `SCRIPT.md / CHARACTERS.md / SCENES.md`；
- `SHOTS.md` 只保存镜头总览，不塞详细模型参数；
- 三个镜头的目的、主要动作和顺序能读懂；
- 总时长与 brief 目标相容。

如果 Agent 判断确实需要某个额外脚本文件，可以创建，但必须说明真实用途。

## 7. Phase C — 视觉设计

brief 已授权 Agent 在给定整体视觉方向内决定角色和地点细节。

验证：

- 不重复向用户询问已经授权的设计细节；
- 建立 CHR01 正式视觉设计；
- 建立 LOC01 正式视觉设计；
- 角色与地点设计分别保存，不复制镜头动作；
- 整体视觉方向需要长期统一时可以建立 `VISUAL_DIRECTION.md`；
- 没有把第一次随机生图结果当设计，因为本阶段尚未生成任何图片。

## 8. Phase D — 复用素材规划

brief 明确：CHR01 和 LOC01 会跨三个镜头重复使用，且用户要求在视频生成前先做严格四视图。

验证：

- 规划人物长期身份 / 四视图；
- 规划场景长期四视图；
- 不为只属于单镜头的动作提前生成公共素材；
- 不创建无用途的 expression sheet、动作库或大量状态图；
- 人物 / 场景提示词来自正式设计。

## 9. Phase E — 严格四视图

检查正式图片提示词是否使用实际 Skill 中的严格四视图规则。

人物至少满足：

- 1:1；
- 严格 2×2；
- 左上正面脸部；
- 右上 180° 后脑；
- 下方两格全身；
- 下方两格无五官；
- 同一人物、服装、比例、颜色。

场景至少满足：

- 同一个三维空间；
- 固定摄影机高度 / 等效焦段 / 地平线；
- 门窗、主要家具 / 空间关系一致；
- 反面不是镜像复制；
- 主光方向保持世界空间逻辑。

不得把四视图改写成自由多视角拼图。

## 10. Phase F — 第一批一次性生成包

只打当前已经可执行的**图片生成包**。

验证：

- 包只存在于 `output/project/.tmp/`；
- 包自包含；
- 有 README；
- 有 CHR01 与 LOC01 的任务文件；
- 任务文件包含当前正式提示词 / 四视图要求；
- 返回文件名明确；
- 不引用包外绝对路径；
- 不使用包外软链接；
- 不把整个项目复制进包。

关键：

本阶段**不得**同时打依赖 CHR01 / LOC01 生成结果的视频镜头包。

角色 / 场景四视图尚未由用户生成和审片，下游视频输入不齐全。

## 11. Phase G — 等待状态

生成包准备完成后，更新 `VIDEO.md` 当前摘要。

至少应能看出：

- 当前正在等待用户外部生成第一批角色 / 场景参考；
- 当前生成包路径；
- 预期返回文件；
- 返回后先进入 `video-review`；
- 视频镜头生成仍被上游参考结果阻塞。

不得：

- 假装图片已经生成；
- 伪造 `CHR01_identity.png / CHR01_four-view.png / LOC01_four-view.png`；
- 创建假 take；
- 宣称审片通过；
- 继续打视频生成包。

## 12. Phase H — 人类可读目录

最终 `output/project/` 应保持浅且容易浏览。

重点检查：

- `VIDEO.md`；
- `video/script/`；
- `video/materials/`；
- `video/shots/` 只在当前项目已经需要详细镜头文件时创建；
- `.tmp/` 一次性生成包。

不要求创建空 `video/edit/`。

不允许为了“规范完整”增加：

- 一级 `audio/`；
- 一级 `delivery/`；
- 一级 `assets/`；
- `STORY.md`；
- 项目状态数据库；
- 全量素材 manifest。

## 13. Phase I — 权威来源

抽查至少三条事实：

- 故事动作；
- CHR01 视觉设计；
- LOC01 空间 / 灯光设计。

确认它们分别来自 brief → 视频脚本 / 正式视觉设计，而不是：

- 临时生成包；
- 随机模型想象；
- 聊天记忆。

图片提示词和一次性包不得成为新的事实源。

## 14. Phase J — 完整性复核

结束前记录：

- Video repo HEAD / status；
- fixture tracked input status；
- `output/project/` 文件树；
- `.tmp/` 文件树。

确认：

- Skills 未修改；
- fixture tracked input 未修改；
- 所有新增产物仅在 `output/`。

## 15. Decision

### accepted

A–J 所有适用阶段通过，并且最核心的人机边界成立：第一批图片包交付后，在用户真实生成结果返回前停止依赖它的下游。

### rejected

例如：

- 创建复杂默认目录；
- 把 brief 完整复制成第二份事实源；
- 角色 / 场景职责混乱；
- 四视图弱化成自由多视角；
- 在上游参考未返回前提前生成视频包；
- 伪造图片 / 视频结果；
- `.tmp/` 变长期事实源；
- `VIDEO.md` 写成完整生成日志；
- 修改 Skill / fixture 输入。

### inconclusive

只有关键阶段因环境无法合法完成时使用，例如：

- fixed HEAD 不一致；
- ForgeRelay 工作区不允许写 fixture `output/`；
- 当前执行器无法加载实际 Skill / dependency。

环境失败不能判产品 rejected。

## 16. 最终报告

```markdown
# Decision

accepted / rejected / inconclusive

## Fixed points
- repo HEAD:
- repo clean:
- fixture clean:

## Phase results
| Phase | Result | Evidence |
| --- | --- | --- |

## Output project tree

## Findings
### Critical
### Major
### Minor

## Integrity
- Skill source modified: no
- Fixture tracked input modified: no
- All outputs under output/: yes/no

## Remaining uncertainty
```
