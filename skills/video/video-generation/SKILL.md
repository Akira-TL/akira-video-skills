---
name: video-generation
description: 为 AI 图片、视频、声音或音乐建立正式 Generation 与 Input Version，编写唯一执行 Prompt、选择实际参考文件、打自包含 outbound pack，并幂等接收用户外部生成结果为 Take。
---

# Video Generation

本 Skill 负责**生成任务的正式输入、人工外部生成交付和结果接收**。Generation 与 Shot 解耦：一个 G 可以覆盖多个 Shot，一个 Shot 也可以使用多个 G / Take。

正式决定当前生成目标如何拆分、哪些依赖必须先满足时，读取 [`references/planning/GENERATION-STRATEGY.md`](references/planning/GENERATION-STRATEGY.md)。大量独立任务需要逐步放量时按 [`references/planning/BATCHING.md`](references/planning/BATCHING.md) 先做代表样本；已有视频基本正确、确实需要生成式编辑或延长时，读取 [`references/transform/EDIT-EXTEND.md`](references/transform/EDIT-EXTEND.md)，先判断是否更适合确定性后期。

## 1. 建立 Generation

Generation 是一项有明确制作目标的生成任务，不是一次点击生成。按归属创建：

- 当前视频任务 → `Vxxx/generations/Gxxx/`；
- 跨视频共享资产生成 → `video/shared/generations/Gxxx/`。

G 在所属 scope 内编号；跨视频引用写 `V001/G003`，共享生成写 `shared/G003`。人类助记后缀不参与正式引用。

## 2. Input Version 是唯一正式输入

同一目标下，每组正式模型输入使用 `Ixx`：唯一 Prompt 正文、实际参考文件版本和必要执行设置。正式 Prompt 只维护在 G/I，不在资产或 Shot 目录复制第二份。

Prompt 编译按 [`references/prompting/VIDEO-PROMPT.md`](references/prompting/VIDEO-PROMPT.md)。需要判断哪些模型设置应进入正式 I、哪些只属于一次执行时，按 [`references/prompting/EXECUTION-PARAMETERS.md`](references/prompting/EXECUTION-PARAMETERS.md) 处理。实际模型的输入类型、时长、参考数量、声音、首尾帧或编辑能力在执行当前 I 时查看当前官方资料；不安装供应商 Adapter Skill，也不把历史模型记忆当当前能力。

Prompt、参考版本或关键设置改变但生成目标不变 → 新 I；生成目标本身改变 → 新 G。跨模型比较按 [`references/prompting/MODEL-COMPARISON.md`](references/prompting/MODEL-COMPARISON.md)。

## 3. 选择最小充分参考

每份参考都明确职责：人物身份、服装 / 状态、地点空间、产品 / 道具结构、动作、摄影、风格或声音。只上传当前 G 真正需要的版本；已投入生产的二进制参考不覆盖。

## 4. Outbound Pack

按 [`references/planning/GENERATION-PACK.md`](references/planning/GENERATION-PACK.md) 与 [`references/planning/PACK-TEMPLATES.md`](references/planning/PACK-TEMPLATES.md) 建立自包含包。作用域路径使用 `.tmp/V001/G003_I02/` 或 `.tmp/shared/G003_I02/`。包必须包含实际 Prompt、真实上传文件、上传顺序、职责、必要设置和返回要求，不能让用户再回项目目录找素材。

文件生命周期优先用 [`scripts/generation_pack.py`](scripts/generation_pack.py)：`init`、`copy`、`seal`、`returns`、`status`、`zip`、`receive`。不要为项目临时重写打包 / 导入脚本。

## 5. Receive 与 Take

返回结果必须先可靠确认属于哪个 scope / G / I，不能根据画面猜。`receive` 把所有候选正式保存为 G 内连续 `takeNN`，切换 I 不重置编号；一个 Take 是一个可独立评审的候选，必要时可以是视频 + 音轨 + 字幕等配套文件集合。

Receive 可安全重跑；中断恢复不重新分配 Take。若用户实际修改 Prompt、参考或关键设置，先把真实输入正式保存成正确 I，再接收；输入无法确定则保留临时包待核对。

正式结果与 Take → I 映射完成，并确认没有用户修改后的 Prompt、替换参考、实际设置或返回结果只存在于临时包后，Receive 自动清理精确对应的 pack / zip。

## 6. 不拥有最终采用关系

Generation 记录输入、输出和后续 Review 结论，但不维护 selected / current take。图片 Take 被用作正式参考时由资产记录固定版本来源；视频最终用了哪条 Take / 哪个时间范围，在无正式时间线时可暂记唯一 Shot 表，建立正式剪辑后以剪辑记录为准。

## 7. 迭代

失败先判断来自参考资产、Shot / 摄影设计、Prompt、模型能力还是随机执行。目标不变时修改一个主要变量并建立新 I，不通过无限加长 Prompt 代替问题定位。

## 完成标准

当前 G 的正式 I 可重建，用户拿到的 outbound pack 能直接执行，返回 Take 能追溯真实 I，临时包安全收尾且没有形成第二份采用状态。
