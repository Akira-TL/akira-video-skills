---
name: video-generation
description: 为 AI 图片或视频生成准备可直接使用的提示词与一次性生成包，并在用户把生成结果带回项目后归档；当需要从正式视频脚本、复用素材和 SHOT.md 编译生成内容、选择参考素材、约定返回文件名或清理临时包时使用。
---

# Video Generation

本 Skill 负责把正式项目内容转换成可执行的 AI 生成输入。长期来源仍然是 `video/script/`、`video/materials/` 和 `video/shots/`；一次性生成包只是方便用户外部生成的派生物。

正式决定一次生成覆盖多少内容、采用哪种生成方式前，读取 [`references/planning/GENERATION-STRATEGY.md`](references/planning/GENERATION-STRATEGY.md)。需要批量生成大量素材 / 镜头时，再读取 [`references/planning/BATCHING.md`](references/planning/BATCHING.md)：先用高风险代表样本验证基准，稳定后才扩大当前可并行批次，不规定固定批量大小。已有视频基本正确、需要连续延长或生成式局部修改时，再读取 [`references/transform/EDIT-EXTEND.md`](references/transform/EDIT-EXTEND.md)，先判断是否其实更适合确定性后期或新建镜头。

## 1. 识别生成对象

生成对象可以是：

- 跨镜头复用的人物、场景、道具、产品等图片素材；
- 某个镜头的视频；
- 某个镜头专属的首帧、尾帧、分镜草图 / 关键帧、补充图片或声音；
- 角色长期声音参考，或整片级配乐 / 旁白草案。

先加载正式归属内容：复用素材使用 `video-materials` 的定义，镜头视频使用 `video-shot` 的 `SHOT.md`。不要从一次性包或旧聊天记录重建长期事实。

## 2. 编写长期提示词

为镜头编写通用视频提示词前读取 [`references/prompting/VIDEO-PROMPT.md`](references/prompting/VIDEO-PROMPT.md)；如果当前项目已安装对应模型适配器，再由适配器把通用镜头意图编译成该模型的最终执行提示词。所有模型适配器统一遵守 [`references/prompting/MODEL-ADAPTER-CONTRACT.md`](references/prompting/MODEL-ADAPTER-CONTRACT.md)，明确具体入口 / 模型 / 模式、当前官方能力核验、输入映射、执行设置和未知项。同一个镜头需要并列测试多个模型时，再读取 [`references/prompting/MODEL-COMPARISON.md`](references/prompting/MODEL-COMPARISON.md)，保持同一 `SHOT.md` 和连续生成结果编号，不按模型复制镜头目录。


可复用素材的提示词保存在对应 `video/materials/` 目录；镜头提示词保存在对应镜头目录，使用 `prompt_v01.md`、`prompt_v02.md` 等少量明确版本。

提示词只编译当前生成模型真正需要的信息。内部镜头 / 素材定义可以比最终模型提示词更完整；模型能力、字段、时长和参考输入上限由当前实际加载的模型适配 Skill 或官方资料决定，不在本 Skill 写死。模型 / 使用入口、时长、比例、声音开关等执行设置与长期项目记录的边界按 [`references/prompting/EXECUTION-PARAMETERS.md`](references/prompting/EXECUTION-PARAMETERS.md)。

若没有可靠模型专用规则，保持通用、明确、可验证的画面与动作描述，并向用户说明当前使用通用提示词，不伪造具体模型能力。

## 3. 选择参考素材

使用最小充分参考集。每份参考都要能回答“它负责稳定什么”：人物身份、服装、场景、产品结构、动作、摄影或其他具体作用。

不把无关参考塞入同一生成，以免身份竞争、风格污染或产品结构漂移。

## 4. 整理一次性生成包

正式打包前读取 [`references/planning/GENERATION-PACK.md`](references/planning/GENERATION-PACK.md)，按图片 / 声音 / 视频包的依赖分批、最小参考集、导回和删除边界执行；需要直接交给用户时使用 [`references/planning/PACK-TEMPLATES.md`](references/planning/PACK-TEMPLATES.md) 生成自包含任务文件。项目内 pack 初始化、正式文件复制、输入冻结、returns、状态检查、zip、幂等 Receive 与自动收尾优先复用本 Skill 自带的 [`scripts/generation_pack.py`](scripts/generation_pack.py)，不要为每个项目重新写临时打包脚本。作用域化 Generation 包使用 `V001/G003_I02` 或 `shared/G003_I02` 这类 ID 路径；CLI 只处理文件生命周期与 G / I / Take 追溯，不决定 Prompt 内容、参考职责、Review 结论或最终采用关系。


在项目 `.tmp/` 下创建作用域明确的目录。新 Generation 流程优先使用：

```text
.tmp/V001/G003_I02/
├── README.md
├── prompt.md
└── references/
```

共享资产生成使用 `.tmp/shared/G003_I02/`。人类助记后缀不参与 ID 解析；包内 Prompt 与上传素材必须是正式输入版本的可重建副本。

只复制当前这批生成需要的提示词与参考素材。README 至少写清：

- 本次生成目标；
- 推荐生成顺序（如果有依赖）；
- 每项使用哪些参考；
- 返回文件名；
- 需要用户特别检查的硬性约束。

返回候选不预先假定最终采用位置。作用域化 Generation 由 `receive` 在 G 内连续分配 `takeNN`，切换 I 不重置；Take 只是可独立评审候选，最终资产 / Shot / 剪辑采用关系由消费该结果的正式记录维护。旧的 `next-take` / `archive` 命令仅保留兼容已有镜头归档流程。

## 5. 导回结果

用户带回生成结果后先可靠确认它属于哪个 scope / G / I。作用域化 Generation 优先使用 `generation_pack.py receive`：先把全部返回候选正式保存为该 G 的 Take，并建立 Take → I 映射，再进入 `video-review`；失败候选同样先保存，不因为质量差就留在临时包里。Receive 可安全重跑，中断后复用已保留的 Take 编号；正式保存与映射成功后，还要确认用户修改后的 Prompt、替换参考、实际设置或返回结果没有只存在于临时包，才自动删除对应 `.tmp/<scope>/Gxxx_Iyy/` 及派生 zip。

如果用户实际生成时改过输入，不能硬挂回原 I：先把真实 Prompt / 参考 / 设置正式保存为正确输入版本，再通过 `receive --input <Ixx>` 和必要的 `--actual-source` 映射后接收。最终哪个 Take / 时间范围被人物资产、Shot、音轨或剪辑采用，不写回 Generation 的 selected 状态。旧的 `archive --confirm-reviewed` 与手动 `cleanup` 只保留给已有流程兼容。

## 6. 迭代纪律

生成失败时先判断问题来自：

- 长期素材/身份定义；
- SHOT.md 本身；
- 提示词表达；
- 模型执行随机性；
- 可以确定性后期修复的缺陷。

一次重试优先只改变一个主要变量。不要用不断加长提示词代替问题定位。

## 完成标准

用户拿到的包能够直接执行当前生成任务；返回文件名明确；正式项目仍是唯一长期来源；结果归档后临时包可安全删除。
