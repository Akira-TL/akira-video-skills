---
name: video-generation
description: 为 AI 图片、视频、声音或音乐建立正式 Generation 与 Input Version，编写唯一执行 Prompt、选择实际参考文件，把多个 G/I 组织成可保留的批次 tar.gz，并幂等接收用户外部生成结果为 Take。
---

# Video Generation

本 Skill 负责**生成任务的正式输入、人工外部生成交付和结果接收**。Generation 与 Shot 解耦：一个 G 可以覆盖多个 Shot，一个 Shot 也可以使用多个 G / Take。

正式决定当前生成目标如何拆分、哪些依赖必须先满足时，读取 [`references/planning/GENERATION-STRATEGY.md`](references/planning/GENERATION-STRATEGY.md)。大量独立任务需要逐步放量时按 [`references/planning/BATCHING.md`](references/planning/BATCHING.md) 先做代表样本；已有视频基本正确、确实需要生成式编辑或延长时，读取 [`references/transform/EDIT-EXTEND.md`](references/transform/EDIT-EXTEND.md)，先判断是否更适合确定性后期。

## 1. 建立 Generation

Generation 是一项有明确制作目标的生成任务，不是一次点击生成。它跟随真正被生成的对象或视频任务：

- 共享人物 / 地点 / 道具 / 声音 → 对应对象目录，例如 `video/shared/characters/CHR01/G001/`；
- 当前视频专属复用对象 → `Vxxx/materials/<category>/<object-id>/Gxxx/`；
- 直接服务整支视频、Shot 或多对象任务 → `Vxxx/generations/Gxxx/`。

Prompt 与 Generated Take 始终保存在同一个 G 目录。资产记录直接引用 `Gxxx/takeNN`，不再复制第二份 `*_ref_vNN` 媒体。

## 2. Input Version 是唯一正式输入

同一目标下，每组正式模型输入使用 `Ixx`：唯一 Prompt 正文、实际参考文件版本和必要执行设置。正式 Prompt 只维护在 G/I，不在资产或 Shot 目录复制第二份。

Prompt 编译按 [`references/prompting/VIDEO-PROMPT.md`](references/prompting/VIDEO-PROMPT.md)。需要判断哪些模型设置应进入正式 I、哪些只属于一次执行时，按 [`references/prompting/EXECUTION-PARAMETERS.md`](references/prompting/EXECUTION-PARAMETERS.md) 处理。实际模型的输入类型、时长、参考数量、声音、首尾帧或编辑能力在执行当前 I 时查看当前官方资料；不安装供应商 Adapter Skill，也不把历史模型记忆当当前能力。

Prompt、参考版本或关键设置改变但生成目标不变 → 新 I；生成目标本身改变 → 新 G。跨模型比较按 [`references/prompting/MODEL-COMPARISON.md`](references/prompting/MODEL-COMPARISON.md)。

## 3. 选择最小充分参考

每份参考都明确职责：人物身份、服装 / 状态、地点空间、产品 / 道具结构、动作、摄影、风格或声音。只上传当前 G 真正需要的版本；已投入生产的二进制参考不覆盖。

## 4. 生成批次

按 [`references/planning/GENERATION-PACK.md`](references/planning/GENERATION-PACK.md) 与 [`references/planning/PACK-TEMPLATES.md`](references/planning/PACK-TEMPLATES.md) 把当前可以一起执行的多个 G/I 组织成一个 `video/batches/Bxxx/`。一个批次根目录只有一份执行说明，同一参考只复制一次；不为每个 Generation 单独建 handoff、临时目录或压缩包。

文件生命周期优先用 [`scripts/generation_pack.py`](scripts/generation_pack.py)：`init` 建批次、`add` 加入一个 G/I 与其参考、`build` 就地生成并保留 `Bxxx.tar.gz`、`status` 检查、`receive` 批量接收。批次目录和压缩包不会因 Receive 自动删除。

## 5. Receive 与 Take

返回结果按 Batch task 明确映射回正式 G / I，不能根据画面猜。`receive` 把各 task 的候选正式保存为对应 G 内连续 `takeNN`，切换 I 不重置编号；一个 Take 是一个可独立评审的候选，必要时可以是视频 + 音轨 + 字幕等配套文件集合。

Receive 可安全重跑；中断恢复不重新分配 Take。若用户实际修改 Prompt、参考或关键设置，先把真实输入正式保存成新的 I，并建立新的执行批次，不在已 build 的 B 中临时改字后继续冒充旧输入。

Receive 完成后保留 `video/batches/Bxxx/`、返回目录与 `Bxxx.tar.gz`；它们是执行快照，不是正式媒体归属，也不替代 G/I/Take。

## 6. 不拥有最终采用关系

Generation 记录输入、输出和后续 Review 结论，但不维护 selected / current take。图片 Take 被用作正式参考时由资产记录固定版本来源；视频最终用了哪条 Take / 哪个时间范围，在无正式时间线时可暂记唯一 Shot 表，建立正式剪辑后以剪辑记录为准。

## 7. 迭代

失败先判断来自参考资产、Shot / 摄影设计、Prompt、模型能力还是随机执行。目标不变时修改一个主要变量并建立新 I，不通过无限加长 Prompt 代替问题定位。

## 完成标准

当前 G 的正式 I 可重建；多个可并行 G/I 能按一次实际外部执行组成一个可直接使用的批次 tar.gz；返回 Take 与 Prompt 共置并能追溯真实 I，批次保留但不形成第二份正式媒体或采用状态。
