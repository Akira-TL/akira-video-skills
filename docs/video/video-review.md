# video-review

`video-review` 审核返回项目的复用素材和 Shot Take。

它根据正式人物/场景/产品定义、`SHOT.md`、Prompt 和相邻连续性判断：采用、接受偏差并调整后续、后期修复、重新生成，还是重写定义/Prompt。详细人物、空间、声音、摄影和产品检查按 `references/TAKE-QA.md` 展开。采用哪个 Take 记录在 Shot 自己的 `SHOT.md` 中，并保留实际出口、可接受偏差和后期修复项；不复制 `final.mp4`，也不建立额外选择数据库。
