---
name: akira-video
description: 进入并持续推进一个 AI 视频制作项目；读取或建立 VIDEO.md，根据当前视频脚本、复用素材、镜头、生成结果和整片后期状态，按需路由到 canonical 视频专业 Skill，而不是把所有制作规则塞进一个总提示词。
---

# Akira Video

`akira-video` 是 Akira Video Skills 的 Primary Router。它拥有视频制作入口、`VIDEO.md`、当前制作任务判断、专业 Skill 路由与停止边界；具体视频脚本、复用素材、镜头、生成包、审片和整片后期方法由对应专业 Skill 负责。完整项目的依赖与人机交接按 [`references/workflow/PRODUCTION-FLOW.md`](references/workflow/PRODUCTION-FLOW.md)；已有项目直接从当前实际工作续，不机械重跑上游步骤。

整个制作始终优先保护：用户与来源事实 → 剧情 / 镜头意图（适用时）→ 人物 / 物体身份与结构 → 产品事实（广告时）→ 空间与时间连续性 → 画面美感 → 炫技。后面的目标不能以破坏前面的约束为代价。

## 1. 进入或接管项目

先读取项目根目录 `VIDEO.md`。不存在时按 [`references/project/PROJECT-LAYOUT.md`](references/project/PROJECT-LAYOUT.md) 建立最小视频项目；项目定义与当前状态按 [`references/project/VIDEO-HOME.md`](references/project/VIDEO-HOME.md)，命名按 [`references/project/NAMING.md`](references/project/NAMING.md)。只创建当前真实需要的目录和文件，不预生成空分类；第一次需要一次性生成包时再确保目标项目 `.gitignore` 忽略 `.tmp/`。

用户已经提供现成图片、视频、音频、粗剪或参考成片时，先按 [`references/project/IMPORT-MEDIA.md`](references/project/IMPORT-MEDIA.md) 判断它在当前项目里的真实用途；可直接复用的成果不强制重走设计或生成流程。

然后按当前任务读取最小必要内容：

- 视频脚本与镜头总览：`video/script/`；
- 跨镜头复用内容：`video/materials/`；
- 当前镜头：`video/shots/<shot-id>/`；
- 已进入整片后期时：`video/edit/`；
- 上游小说、章节、品牌资料或其他来源：沿当前项目真实 pointer 读取，不复制成第二份上游事实源。

完成标准：能够说明当前视频目标、交付要求、正在推进的制作内容、已有可复用素材、当前镜头/后期状态和真实 blocker。

进入下一项昂贵制作前，按 [`references/workflow/PRODUCTION-GATES.md`](references/workflow/PRODUCTION-GATES.md) 只运行当前项目适用的轻量门禁；门禁不产生额外项目状态文件。当前项目已经大到平铺影响阅读，或确实需要同时比较创意版本时，再读取 [`references/project/SCALING-VERSIONS.md`](references/project/SCALING-VERSIONS.md)，不要预设长片目录。需要清理失败结果、一次性包、缓存或旧媒体时，按 [`references/project/MEDIA-LIFECYCLE.md`](references/project/MEDIA-LIFECYCLE.md) 先确认文件不是唯一输入、当前采用结果或后期工程唯一依赖。

## 2. 维护 VIDEO.md

`VIDEO.md` 是给人和下一位 Agent 直接阅读的视频制作首页，只保存当前仍有用的信息。固定关注：

- 项目与视频目标；
- 交付要求；
- 当前制作进度；
- 当前正在推进的工作；
- blocker；
- 仍然影响后续的关键决定；
- 到视频脚本、复用素材、镜头和整片后期的导航。

普通提示词历史、所有生成结果、生成日志和已经被 Git 历史取代的旧决定不进入 `VIDEO.md`。

详细写法见 [`references/project/VIDEO-HOME.md`](references/project/VIDEO-HOME.md)。

## 3. 路由专业工作

根据用户当前目标和已有项目内容选择下一项实际制作工作。完整项目不要求机械经过所有能力；已经有脚本时可以直接进入镜头，已经有镜头与素材时可以直接准备生成包，返回生成结果后直接进入审片。

按当前任务加载 canonical Skill：

- 从小说、章节、brief 或其他上游内容形成/修订视频脚本、人物表演、场景或镜头总览 → `video-script`；
- 角色或场景只有功能描述、尚未形成具体外形 / 服装 / 材质 / 空间 / 光线设计 → `video-design`；
- 角色需要跨镜头稳定音色、声音参考，或项目需要规划对白声音、环境声、音效与整片声音边界 → `video-audio`；
- 规划或维护跨镜头复用的人物、场景、道具、产品提示词与参考素材 → `video-materials`；
- 把镜头总览展开成 `SHOT.md`，处理动作、摄影、声音与相邻镜头连续性 → `video-shot`；
- 编写当前生成提示词、选择最小参考集、整理一次性生成包、导回用户生成结果 → `video-generation`；
- 用户带回图片或生成结果后判断采用、调整后续、后期修复、重生成或重写 → `video-review`；
- 多个采用镜头进入 Premiere Pro、After Effects、DaVinci Resolve 等整片后期 → `video-editing`；
- 品牌、产品植入或广告需要核验产品功能、结构、官方素材与广告表达边界 → 按需加载可选 `video-advertising`；当前 Target 未安装时使用明确 coordinate `akira-tl/akira-video-skills/video-advertising`，交给 `akira` Router / Skiloom 生成候选计划（Candidate plan）并在授权后安装。

Router 只保存上述职责摘要；进入任一分支后，以实际加载的权威 Skill 为该专业方法的唯一权威来源。

若目标需要视频模型专用适配，先读取 [`references/workflow/MODEL-ADAPTERS.md`](references/workflow/MODEL-ADAPTERS.md) 选择当前仓已有的最小适配 Package；尚未安装时把明确 coordinate 交给 `akira` Router / Skiloom 正常生成候选计划（Candidate plan）并安装。不要把模型参数或供应商细节硬编码进 `akira-video`。图片生图目前使用 `video-design` + `video-materials` 的通用规则，不单独维护图片模型适配器。

## 4. 外部生成的人机边界

默认允许用户在外部图片/视频模型中完成实际生成。需要外部生成时，专业生成 Skill 从正式项目内容整理一次性生成包：

正式项目内容 → `.tmp/` 一次性生成包 → 用户外部生成 → 结果返回 → 归档正式目录 → 删除临时包。

一次性生成包是派生物，不成为长期项目事实源；长期提示词留在 owning 素材或镜头目录，临时包只复制当前生成真正需要的内容。

## 5. 重新路由与停止边界

每次专业 Skill 完成一个有边界动作后：

1. 把返回的正式素材、生成结果、镜头决定或整片工程归档到 owning 目录；
2. 更新仍影响当前制作的 `VIDEO.md`；
3. 根据用户目标与当前产物决定下一项制作工作。

只有用户限定范围完成、下一步必须等待用户外部生成或提供素材、存在真实 blocker，或当前交付已经完成时停止。等待用户外部生成时明确给出一次性生成包和返回命名要求，不继续假装已产生素材。
