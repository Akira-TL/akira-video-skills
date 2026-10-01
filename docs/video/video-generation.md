# video-generation

`video-generation` 从正式视频脚本、复用素材和 `SHOT.md` 编译长期提示词与一次性生成包。生成包按真实依赖分批：需要人物 / 场景 / 产品参考或上一镜头实际出口的任务，必须等上游输入先生成、审片并归档后再打包。默认按单镜头或少量强连续镜头生成，不因为模型允许更长时长就把完整长片塞进一次请求；持续失败时会回查设计、参考、镜头负载和生成模式。大量任务按 `references/planning/BATCHING.md` 先用高风险代表样本验证角色 / 场景 / 产品 / 模型组合，稳定后再逐步放量，不固定“每批几个”。

一次性生成包只放在当前 ForgeRelay 项目工作区的 `.tmp/`，按 `references/planning/GENERATION-PACK.md` 只复制本次生成需要的提示词和参考素材，并用 `references/planning/PACK-TEMPLATES.md` 整理成用户无需打开项目目录即可执行的自包含任务文件。新 Generation 流程使用 `.tmp/V001/G003_I02/` 或 `.tmp/shared/G003_I02/` 这类作用域路径；`scripts/generation_pack.py` 支持 `seal` 冻结交付输入与幂等 `receive`：返回候选先全部进入正式 G 并建立 Take → I 映射，再审片；接收成功后自动清理该版本临时包，重复执行不会重新分配 Take。若用户在外部生成时改变 Prompt / 参考 / 设置，Receive 会阻止静默归入旧 I，直到真实输入被正式保存并显式映射。CLI 不决定 Prompt 内容、Review 结论或最终采用关系；旧 `next-take`、`archive` 和手动 cleanup 仅保留兼容已有流程。

`SHOT.md` 是内部制作定义，最终视频提示词只是从它编译出的执行文本；通用编译规则位于 `references/prompting/VIDEO-PROMPT.md`。同一镜头确实需要并列比较多个视频模型时，按 `references/prompting/MODEL-COMPARISON.md` 让模型专用提示词并列、生成结果连续编号，不按模型复制镜头结构。已有视频需要生成式延长 / V2V 局部编辑时按 `references/transform/EDIT-EXTEND.md`：同一连续镜头保持 Shot 身份但生成新结果，硬切 / 新视点 / 新叙事功能则建立新 Shot，原始 `takeNN.mp4` 不覆盖。模型能力、时长、参考输入上限和模型专用提示词规则由实际加载的模型适配 Skill 或当前官方资料决定；通用生成 Skill 不写死某个模型版本。`references/prompting/EXECUTION-PARAMETERS.md` 区分长期创作事实与一次执行参数：一次性包写当前真正需要用户确认的设置，seed / request ID 等只有复现或排错需要时才长期保留。
