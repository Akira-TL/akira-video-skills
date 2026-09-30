---
name: video-design
description: 设计 AI 视频中的角色与场景视觉方案；当脚本只说明“需要一个什么样的人/场景”，但还没有形成可稳定生成的外形、服装、材质、色彩、空间、光线和视觉识别系统时使用。
---

# Video Design

本 Skill 负责把剧情与制作需求转换成**可复用、可辨认、可生成的角色和场景视觉设计**。它不直接承担最终图片生成，也不替代 `video-script` 的人物表演 / 场景剧情定义。

设计结果长期放在对应复用素材旁，例如：

- `video/materials/characters/CHR01_design.md`
- `video/materials/scenes/LOC01_design.md`

随后由 `video-materials` 把设计转成长期提示词、严格四视图和参考图片。

## 1. 先读取设计约束

优先读取：

- `VIDEO.md`；
- 当前 `SCRIPT.md` / `CHARACTERS.md` / `SCENES.md`；
- 上游小说、章节、世界观或品牌资料中与当前对象真正有关的部分；
- 已有视觉参考；
- 目标视频风格、时代、世界规则和生成限制。

只继承已经存在的事实与制作决定。脚本没有定义视觉细节时，本 Skill 可以提出设计方案，但不得把新设计反向冒充上游故事事实。

项目需要统一整片视觉语言时，先读取 [`references/foundation/ART-DIRECTION.md`](references/foundation/ART-DIRECTION.md)，再进入具体角色 / 场景设计。

## 2. 角色设计

角色设计不能停在“年轻女性”“中年男人”“帅气少年”这类泛化描述。

至少从当前剧情功能推导：

- 角色在画面中的第一识别点；
- 整体轮廓；
- 年龄感、身高与身体比例；
- 面部结构与稳定识别特征；
- 发型结构；
- 服装层级、剪裁、材质和配件；
- 主色、辅助色与对比关系；
- 职业、时代、生活状态如何通过外观被看见；
- 哪些特征必须跨镜头保持；
- 哪些服装 / 状态允许变化；
- 哪些设计容易导致生成漂移，应简化。

复杂角色设计按需读取 [`references/character/CHARACTER-DESIGN.md`](references/character/CHARACTER-DESIGN.md)。

## 3. 场景设计

场景设计不是“一个厨房”“一个未来城市”这样的名词，而要形成能够支撑镜头和连续性的空间。

至少从当前剧情功能推导：

- 场景承担什么叙事功能；
- 空间尺度与大体布局；
- 建筑 / 家具 / 自然结构；
- 主要材质；
- 主色与辅助色；
- 主光来源、方向和时间感；
- 关键视觉锚点；
- 角色和关键道具可以怎样在空间里活动；
- 哪些部分必须跨镜头稳定；
- 哪些细节只属于某个镜头，不进入公共场景设计。

复杂场景按需读取 [`references/environment/SCENE-DESIGN.md`](references/environment/SCENE-DESIGN.md)。项目存在多个视觉世界时读取 [`references/environment/WORLD-DESIGN.md`](references/environment/WORLD-DESIGN.md)；主场景空间关系或陌生机械会直接影响多个镜头时读取 [`references/environment/SPACE-MECHANISM.md`](references/environment/SPACE-MECHANISM.md)。

## 4. 设计方向不足时先做候选

当选择会明显改变主角色视觉身份、整片视觉语言、主要场景或大量后续素材，而上游资料没有答案时，按 [`references/foundation/DESIGN-APPROVAL.md`](references/foundation/DESIGN-APPROVAL.md) 区分“Agent 可直接补全的实现细节”和“应先由用户选择 / 明确授权的高影响创意分叉”。


当输入只提供功能而没有明确视觉方向时，先提出少量真正不同的视觉方案，而不是立刻随机补细节。

候选之间应在轮廓、材质、时代感、色彩或空间语言上有真实差异，并说明各自：

- 为什么符合当前故事 / 角色；
- 识别度；
- 多镜头一致性风险；
- AI 生成稳定性；
- 与已有角色 / 场景是否容易混淆。

没有必要时不制造大量候选。用户或当前制作决定选定方向后，再把选中设计写成长期设计文件。

## 5. 设计文件

正式写 `VISUAL_DIRECTION.md`、`CHRxx_design.md`、`LOCxx_design.md` 或按需的虚构道具设计时，使用 [`references/foundation/DESIGN-TEMPLATES.md`](references/foundation/DESIGN-TEMPLATES.md) 保持职责边界；模板不要求项目创建所有文件。


角色 `*_design.md` 只保存视觉设计当前有效版本，场景同理。Git 保存历史，不创建 `design_final2.md` 等伪版本。

设计文件可以引用上游来源和视觉参考，但不复制整段小说、人物百科或场景历史。

## 6. 交给 video-materials

角色 / 场景设计如何转成基础身份、四视图、服装 / 光照状态等长期参考，按 [`references/foundation/DESIGN-OUTPUTS.md`](references/foundation/DESIGN-OUTPUTS.md)；这些都是按真实镜头需求选择，不要求每个对象生成完整套装。


设计确认后：

1. `video-materials` 根据设计建立长期图片提示词；
2. 需要稳定身份 / 结构时，按严格四视图模板生成参考图；
3. 返回的图片和提示词与设计文件共置或放在同一类别目录；
4. 镜头专属动作、摄影和临时状态仍归对应镜头。

## 完成标准

角色或场景已经从“功能描述”变成具体、可辨认、跨镜头可保持、且适合 AI 生成的视觉设计；下一步可以直接进入参考素材提示词和四视图生成。
