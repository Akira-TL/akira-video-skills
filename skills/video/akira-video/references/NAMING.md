# 视频项目命名

命名目标是让人一眼知道对象是什么，同时不给文件名塞入数据库式元数据。

## 1. 稳定对象 ID

默认可使用：

- `CHR01`：角色；
- `LOC01`：长期场景 / 地点；
- `PROP01`：道具；
- `PROD01`：具体产品；
- `SC01`：剧本场次 / 场景编号；
- `SH010`：镜头。

简单项目只使用真实需要的 ID，不要求全部存在。

## 2. Shot ID

有明确场次时：

`SC01_SH010`
`SC01_SH020`

没有 Scene 的简单项目可以直接：

`SH010`
`SH020`

镜头编号默认留间隔，便于以后插入 `SH015` 或 `SH025`，不因为新增一个镜头重排后面所有身份。

## 3. 复用素材

文件名优先采用：

`<object-id>_<用途或状态>.<ext>`

例如：

`CHR01_design.md`
`CHR01_prompt.md`
`CHR01_identity.png`
`CHR01_four-view.png`
`CHR01_costume-a.png`
`CHR01_voice.md`
`CHR01_voice-reference.wav`
`LOC01_design.md`
`LOC01_four-view.png`
`LOC01_kitchen.png`
`PROP01_damaged.png`
`PROD01_truth.md`
`PROD01_official-front.png`

用途 / 状态只有真的需要区分时才写。

## 4. Prompt 版本

长期文本普通修改由 Git 保存历史。

只有同一时刻确实需要保留多个可比较 Prompt 时才使用：

`prompt_v01.md`
`prompt_v02.md`

不要因为每改一句就创建新版本文件。

## 5. 图片候选

同一长期图片一次返回多个候选时，候选只在 Generation Pack 的 `returns/` 暂存，例如：

`CHR01_identity_take01.png`
`CHR01_identity_take02.png`

审片选中后再归档成长期稳定名：

`CHR01_identity.png`

没有被选中的候选默认随临时包清理；如果用户明确要长期保留多个真正不同的状态 / 方案，再给它们明确状态名或用途名，而不是长期留下 `takeNN`。

## 6. 视频 Take

在镜头目录内：

`take01.mp4`
`take02.mp4`

文件离开镜头目录，需要用户从外部平台传回时，可以使用完整归属：

`SC01_SH010_take01.mp4`

导回项目后可按镜头目录现有简洁命名整理。

## 7. 禁止 final 链

不要使用：

`final.png`
`final2.mp4`
`new_final.mp4`
`real_final.mp4`

当前采用哪个 Take 由 `SHOT.md` 或等价明确记录表示；整片当前导出也由 Git / 后期工程和清楚版本关系管理，不靠文件名猜。

## 8. 文件名不承担的内容

默认不把以下内容塞进媒体文件名：

- 模型名称；
- Provider；
- seed；
- 分辨率；
- FPS；
- 全部参考素材；
- Prompt hash。

这些只有在真实工作流需要长期保存时才进入对应说明，而不是污染所有文件名。

## 完成标准

用户不看数据库、不读隐藏 metadata，仅凭目录和文件名就能判断对象归属；同时文件名不会因为每次模型参数变化而不断膨胀。
