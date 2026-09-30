---
name: video-materials
description: 规划、创建、整理和维护多个镜头会重复使用的视频复用素材；当需要人物/场景/道具/产品提示词、参考图、官方素材、身份与状态参考或其他可重复引用内容时使用。
---

# Video Materials

本 Skill 只拥有 `video/materials/` 下跨镜头复用的内容。镜头专属图片、声音和生成结果跟随对应 Shot，不为了分类把同一素材复制到多个目录。

批量生成复用素材前先读取 [`references/MATERIAL-PLANNING.md`](references/MATERIAL-PLANNING.md)，从实际脚本 / Shot 反推需要哪些长期素材，避免为了数量预生成。

## 1. 判断是否值得成为复用素材

只有多个镜头会重复引用，或者稳定身份/结构必须被后续持续保持的内容才进入 `video/materials/`。

常见类别包括人物、场景、道具、产品和视觉参考。类别目录只在真实需要时创建；Prompt 与对应图片可以放在一起，优先让人打开目录就能理解这个对象。

如果人物或场景还没有形成具体视觉设计，先加载 `video-design`，不要直接把泛化描述写成生图 Prompt。

需要建立人物 / 衣物 / 道具 / 场景四视图、陌生机械或产品结构参考时，读取 [`references/REFERENCE-DESIGN.md`](references/REFERENCE-DESIGN.md)。其中严格四视图模板见 [`references/FOUR-VIEW-PROMPTS.md`](references/FOUR-VIEW-PROMPTS.md)。

## 2. 身份与状态分开

同一个人物、道具或产品先保持稳定身份，再为真实需要区分的状态单独命名，例如服装 A / B、完整 / 损坏、干燥 / 湿润。不要用一个模糊“final”素材代表所有状态。

文件名使用稳定对象 ID 与人能理解的用途，例如：

`CHR01_prompt.md`
`CHR01_identity.png`
`CHR01_costume-a.png`
`LOC01_kitchen.png`
`PROP01_damaged.png`

具体状态只在当前项目真的需要同时区分时才写进文件名。

## 3. Prompt 与参考图

编写长期图片 Prompt 时读取 [`references/IMAGE-PROMPTS.md`](references/IMAGE-PROMPTS.md)；需要四视图时继续叠加 [`references/FOUR-VIEW-PROMPTS.md`](references/FOUR-VIEW-PROMPTS.md) 对应严格模板。


长期可复用的图片 Prompt 与对应素材共同保存在 owning 目录。Prompt 描述稳定身份、结构、材质、视角或世界规则，不承担某一个镜头独有的动作和摄影。

人物、衣物、道具和场景四视图属于按需制作配方，不是所有项目的固定要求；一旦当前对象需要四视图，就使用对应严格模板，不自行改成自由多视角。模型不理解的机械或装置可在素材旁增加简洁机制说明，明确固定部件、活动部件、运动方向和角色使用方式。

## 4. 产品与官方素材

产品或品牌对象必须区分官方来源与 AI 生成/辅助参考。官方图片、Logo、结构资料和经过核验的产品事实优先作为结构与真实性依据；AI 生成图不能反向升级成产品事实来源。

广告项目涉及产品真实性时加载 `video-advertising`，由它拥有产品事实与广告边界。

## 5. 最小参考集

为某个生成任务选参考素材时使用实现当前约束所需的最小充分集合。每份参考应有明确作用，例如人物身份、服装、场景、产品结构、动作或摄影；不要因为“可能有用”把整个素材库打进一次生成。

## 完成标准

复用素材目录中的每项内容都有清楚对象、用途和归属；跨镜头稳定信息可直接复用，镜头专属内容没有被误放进公共素材区。
