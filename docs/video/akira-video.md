# akira-video

`akira-video` 是完整 AI 视频制作项目的入口。它维护项目根目录的 `VIDEO.md`，恢复当前制作上下文，再把具体工作交给视频脚本、复用素材、镜头、生成、审片或整片后期的 canonical Skill。

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

目录以人容易浏览为优先，不预建空分类。跨镜头重复使用的 Prompt、图片和参考资料放在 `video/materials/`；单个镜头自己的 `SHOT.md`、Prompt 版本、Take、图片和声音集中在对应 `video/shots/<shot-id>/`。

## 专业能力

Router 按当前真实制作任务加载：`video-script`、`video-design`、`video-materials`、`video-shot`、`video-generation`、`video-review` 或 `video-editing`。品牌与产品项目按需增加 `video-advertising`；模型专用参数和 Prompt 规则不进入 Router。

## 外部生成

用户可以在外部 AI 平台实际生成。Agent 根据正式项目内容整理一次性生成包，把当前所需 Prompt、参考素材和返回文件名放进 `.tmp/`；生成结果返回后归档到正式目录，临时包删除。

## VIDEO.md

`VIDEO.md` 是当前制作首页和导航。它记录项目目标、交付要求、当前进度、当前工作、阻塞项和仍有效的关键决定，不保存全部 Take、Prompt 历史或生成日志。
