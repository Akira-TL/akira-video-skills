# video-generation

`video-generation` 从正式视频脚本、复用素材和 `SHOT.md` 编译长期提示词与一次性生成包。生成包按真实依赖分批：需要人物 / 场景 / 产品参考或上一镜头实际出口的任务，必须等上游输入先生成、审片并归档后再打包。默认按单镜头或少量强连续镜头生成，不因为模型允许更长时长就把完整长片塞进一次请求；持续失败时会回查设计、参考、镜头负载和生成模式。大量任务按 `references/BATCHING.md` 先用高风险代表样本验证角色 / 场景 / 产品 / 模型组合，稳定后再逐步放量，不固定“每批几个”。

一次性生成包只放在当前 ForgeRelay 项目工作区的 `.tmp/`，按 `references/GENERATION-PACK.md` 只复制本次生成需要的提示词和参考素材，并用 `references/PACK-TEMPLATES.md` 整理成用户无需打开项目目录即可执行的自包含任务文件。用户在外部模型完成生成后，结果归档回 `video/materials/` 或对应镜头，确认没有唯一信息后删除临时包。

`SHOT.md` 是内部制作定义，最终视频提示词只是从它编译出的执行文本；通用编译规则位于 `references/VIDEO-PROMPT.md`。同一镜头确实需要并列比较多个视频模型时，按 `references/MODEL-COMPARISON.md` 让模型专用提示词并列、生成结果连续编号，不按模型复制镜头结构。已有视频需要生成式延长 / V2V 局部编辑时按 `references/EDIT-EXTEND.md`：同一连续镜头保持 Shot 身份但生成新结果，硬切 / 新视点 / 新叙事功能则建立新 Shot，原始 `takeNN.mp4` 不覆盖。模型能力、时长、参考输入上限和模型专用提示词规则由实际加载的模型适配 Skill 或当前官方资料决定；通用生成 Skill 不写死某个模型版本。`references/EXECUTION-PARAMETERS.md` 区分长期创作事实与一次执行参数：一次性包写当前真正需要用户确认的设置，seed / request ID 等只有复现或排错需要时才长期保留。
