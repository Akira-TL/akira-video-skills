---
name: video-visual-design
description: 设计并维护 AI 视频可复用的视觉对象与参考资产；当需要把人物、地点、道具、虚构机械或整体视觉要求具体化，并按真实镜头需求准备生图 Prompt、四视图和长期参考版本时使用。
---

# Video Visual Design

本 Skill 统一负责**视觉设计 + 视觉参考资产准备**。人物、地点、道具和虚构机械属于同一视觉开发流程的不同对象类型，不拆成多个必经 Skill；它们都服务当前剧情与导演目标。

设计回答“它应该是什么”，Generation Prompt 回答“这次让模型生成什么”，已确认参考图回答“实际采用了什么视觉外观”。三者语义不同，任何一层都不能自动覆盖另外两层。

## 1. 读取当前表达目标

优先读取当前 `Vxxx/VIDEO.md`、必要的场景正文、已有资产记录、上游事实和用户提供的视觉参考。Director 提供的是整片级表达目标；本 Skill 负责把这些目标具体化成可辨认、可复用、适合 AI 生成的视觉设计。

项目需要统一视觉语言时按 [`references/foundation/ART-DIRECTION.md`](references/foundation/ART-DIRECTION.md)；高影响视觉分叉按 [`references/foundation/DESIGN-APPROVAL.md`](references/foundation/DESIGN-APPROVAL.md)。

## 2. 人物、地点与道具

- 人物设计按 [`references/character/CHARACTER-DESIGN.md`](references/character/CHARACTER-DESIGN.md)，人物身份图 / 全身角色图 / 状态参考的专用生图模板按 [`references/character/CHARACTER-PROMPTS.md`](references/character/CHARACTER-PROMPTS.md)；
- 地点 / 环境按 [`references/environment/SCENE-DESIGN.md`](references/environment/SCENE-DESIGN.md)，空场环境 / 环境状态 / 空间结构参考的专用生图模板按 [`references/environment/ENVIRONMENT-PROMPTS.md`](references/environment/ENVIRONMENT-PROMPTS.md)；
- 多视觉世界、复杂空间 / 机械分别按 [`references/environment/WORLD-DESIGN.md`](references/environment/WORLD-DESIGN.md) 与 [`references/environment/SPACE-MECHANISM.md`](references/environment/SPACE-MECHANISM.md)；
- 基础光源、时间状态和材质反应按 [`references/environment/LIGHTING.md`](references/environment/LIGHTING.md)。镜头级机位用光与曝光由 `video-cinematography` 处理。

人物、地点、道具都应从剧情功能和当前镜头需求推导，不为了“资产齐全”提前设计大量永远不会使用的状态或角度。

## 3. 资产归属

默认优先判断是否值得跨视频复用：

- 跨视频复用 → `video/shared/<category>/`；
- 只属于当前视频但跨镜头复用 → `Vxxx/materials/`；
- 只服务一个 Generation / Shot → 留在对应正式 Generation 或 Shot 记录，不自动提升为长期资产。

资产记录说明设计约束、每个正式参考版本的来源和当前默认版本。外部导入图片可以直接成为资产，不要求为了统一结构虚构 Generation。

## 4. 视觉参考规划

按真实生产需要判断是否需要基础身份图、严格四视图、服装 / 状态参考、地点多角度、道具结构图或其他长期参考。详细规划按 [`references/assets/ASSET-PLANNING.md`](references/assets/ASSET-PLANNING.md)、参考职责按 [`references/assets/REFERENCE-ROLES.md`](references/assets/REFERENCE-ROLES.md)、连续性按 [`references/assets/REFERENCE-CONTINUITY.md`](references/assets/REFERENCE-CONTINUITY.md)。

稳定人物 / 地点 / 道具参考的详细制作原则按 [`references/assets/REFERENCE-DESIGN.md`](references/assets/REFERENCE-DESIGN.md)，严格四视图模板按 [`references/assets/FOUR-VIEW-PROMPTS.md`](references/assets/FOUR-VIEW-PROMPTS.md)。四视图稳定已经确认的设计，不替代设计本身。

用户提供、品牌官方或第三方参考进入生成 / 交付前，按 [`references/assets/SOURCE-RIGHTS.md`](references/assets/SOURCE-RIGHTS.md) 保留必要来源与使用边界；公开可访问不自动等于可直接对外交付。

## 5. 生图 Prompt 只落 Generation / Input Version

本 Skill 可以编写生图 Prompt，但**正式送去生成的唯一正文必须保存在对应 G / I 的 Prompt 文件中**。资产记录只引用该 Prompt 来源，不在人物 / 地点 / 道具目录维护第二份相同 Prompt。

通用生图写法按 [`references/assets/IMAGE-PROMPTS.md`](references/assets/IMAGE-PROMPTS.md)。当前模型能力和输入限制在实际生成时核验，不把供应商专用 Adapter 变成长期 Skill。

## 6. 返回图片与资产版本

返回图片先由 `video-review` 检查。被正式采用为参考的二进制资产从 `v01` 起固定版本，不覆盖已投入生成的文件；新参考产生新版本。资产记录至少能查到：

- `CHR01_ref_v01` 来自哪个 `shared/Gxxx takeNN` 或哪个外部文件；
- 后续版本各自来源；
- 当前默认使用哪一版。

更新当前默认版本不会改写历史视频 / Generation 已经固定引用的具体资产版本。文本设计由 Git 保存历史；需要追溯某个 Generation 当时的设计依据时，记录真正包含该设计内容的 Git revision。

## 完成标准

当前需要的视觉对象已经具体化到足以支持 Storyboard / Cinematography / Generation；缺失参考已经被明确为具体 Generation 目标；没有为了模板完整提前制造不需要的素材。
