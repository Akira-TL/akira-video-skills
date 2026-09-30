# Changelog

## Unreleased

- 初始化 Akira Video Skills 独立产品仓。
- 建立面向人的浅层视频项目目录、`VIDEO.md`、一次性生成包与 Shot 归档边界。
- 建立 `akira-video` Primary Router。
- 增加视频脚本、复用素材、镜头、生成包、审片、整片后期六个稳定核心 Skill。
- 增加品牌与产品项目的可选 `video-advertising` Skill。
- 将剧情因果与对白、多视角/机械参考、镜头导演与连续性、Take QA、最终成片 QC、产品事实等详细规范下沉为按需 references，避免稳定 Skill 主入口膨胀。
- 增加 `video-model-runway`、`video-model-veo`、`video-model-seedance` 三个 in-progress 模型适配 Package；模型专用 Prompt 方法与动态 capability 核验从稳定核心隔离。
- 增加稳定 `video-design` Skill，专门负责角色与场景视觉设计；恢复人物、衣物角色、普通衣物、道具、场景五套严格 1:1、2×2 四视图生图模板，并由 `video-materials` 按需使用。
- 增加稳定 `video-audio` Skill，管理角色跨镜头声音身份与声音参考，不新增独立 `audio/` 项目目录；补齐多世界、空间 / 机械设计与一次性 Generation Pack 的详细契约，并要求临时包只存在于当前 ForgeRelay 项目 `.tmp/`。
- 补齐整体视觉方向、复用素材规划、通用生图 Prompt 与通用视频 Prompt 编译契约：四视图从已确认设计生成，`SHOT.md` 与最终模型 Prompt 明确分层，不为素材数量或 Prompt 长度制造复杂度。
- 扩展 `VIDEO.md` 为整片级项目定义 / 来源限制 / 当前制作首页，新增统一对象与文件命名契约，并补齐剧情 / Shot 生成前 readiness gate 与广告落版约束。
- 补齐 Take 采用记录、实际出口连续性、轻量 `video/edit/` 工程 / 成片命名，以及 `akira-video` 对 Runway / Veo / Seedance 可选模型适配器的按需发现；明确当前不维护图片模型适配器。
- 增加小说 / 长文本到视频的改编协议、脚本层四类文件职责，以及按 Shot 拆分、生成模式选择和持续失败时拆镜头的生成策略。
- 收紧 Generation Pack 往返：目标项目 `.gitignore` 必须忽略 `.tmp/`，zip、返回暂存与候选图片均留在当前 ForgeRelay 项目内；多图片候选以 `*_takeNN.png` 暂存，只有选中结果进入长期稳定素材名。
- 恢复复杂镜头的 `SHOT.md` 可直接套用模板，以及陌生机械的固定 / 活动结构、允许与禁止运动、操作链和使用姿势 Prompt 模板。
- 补齐可选 `video-advertising` 的安装回路：广告分支命中但当前 Target 缺失时，由 `akira-video` 交给 `akira` / Skiloom 对明确 Package coordinate 执行 Candidate plan，而不是复制广告规则回核心。
