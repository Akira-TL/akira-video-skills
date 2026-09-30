# akira-video

`akira-video` 是完整 AI 视频制作项目的入口。它维护项目根目录的 `VIDEO.md`，恢复当前制作上下文，再把具体工作交给视频脚本、视觉 / 声音设计、复用素材、镜头、生成、审片或整片后期的权威 Skill。用户已经有现成图片、视频、声音或粗剪时按 `references/project/IMPORT-MEDIA.md` 直接判断用途并复用，不为了流程完整强制重新生产。完整人机协作流程见 `references/workflow/PRODUCTION-FLOW.md`：已有项目从当前工作续，外部生成结果未返回时不假装推进依赖它的下游；跨会话等待按 `references/workflow/WAITING-RESUME.md` 记录生成包、预期返回和下一步，下一轮先恢复现有包而不是重新打包。不同制作层发生冲突时按 `references/workflow/AUTHORITY.md` 回到真正权威来源修复；提示词和一次性生成包不是项目事实源。

## 项目目录

视频 Skill 不接管整个项目。小说、章节、世界观、品牌资料和其他上游内容继续由原来的 Skill / 文件拥有；视频制作只维护：

```text
VIDEO.md
video/script/
video/materials/
video/shots/
video/edit/      # 按需
.tmp/            # 一次性生成包
```

目录以人容易浏览为优先，不预建空分类。跨镜头重复使用的提示词、图片和参考资料放在 `video/materials/`；单个镜头自己的 `SHOT.md`、提示词版本、生成结果、图片和声音集中在对应 `video/shots/<shot-id>/`。

## 专业能力

Router 按当前真实制作任务加载：`video-script`、`video-design`、`video-audio`、`video-materials`、`video-shot`、`video-generation`、`video-review` 或 `video-editing`。品牌与产品项目按需增加 `video-advertising`；模型专用参数和提示词规则不进入 Router。

## 外部生成

用户可以在外部 AI 平台实际生成。Agent 根据正式项目内容整理一次性生成包，把当前所需提示词、参考素材和返回文件名放进 `.tmp/`；生成结果返回后归档到正式目录，临时包删除。

## VIDEO.md

`VIDEO.md` 是当前制作首页和导航；项目记录边界按 `references/project/RECORDING.md`，重要决定先写真正归属文件，项目首页只保留整片级当前摘要。它同时保存整片级项目定义、交付要求、来源 / 授权限制、当前进度、当前工作、阻塞项和仍有效的关键决定，不保存全部生成结果、提示词历史或生成日志。对象和文件命名统一由 `akira-video/references/project/NAMING.md` 维护；进入昂贵下一阶段前按 `references/workflow/PRODUCTION-GATES.md` 运行当前项目适用的轻量门禁。默认保持短片浅结构，只有真实复杂度出现时才按 `references/project/SCALING-VERSIONS.md` 增加章节或临时创意变体。
