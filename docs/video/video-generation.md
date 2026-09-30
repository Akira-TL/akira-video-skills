# video-generation

`video-generation` 从正式视频脚本、复用素材和 `SHOT.md` 编译长期 Prompt 与一次性生成包。

一次性生成包只放在当前 ForgeRelay 项目工作区的 `.tmp/`，按 `references/GENERATION-PACK.md` 只复制本次生成需要的 Prompt 和参考素材，并明确返回文件名。用户在外部模型完成生成后，结果归档回 `video/materials/` 或对应 Shot，确认没有唯一信息后删除临时包。

`SHOT.md` 是内部制作定义，最终视频 Prompt 只是从它编译出的执行文本；通用编译规则位于 `references/VIDEO-PROMPT.md`。模型能力、时长、参考输入上限和模型专用 Prompt 规则由实际加载的模型适配 Skill 或当前官方资料决定；通用生成 Skill 不写死某个模型版本。
