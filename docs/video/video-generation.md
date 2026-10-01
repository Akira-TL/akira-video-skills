# video-generation

`video-generation` 为 AI 图片、视频、声音或音乐建立正式 Generation（G）与 Input Version（I），维护唯一执行 Prompt、实际参考版本与必要设置，并通过一次性交付包接收外部生成结果为 Take。

Generation 与 Shot 解耦：当前视频任务放 `Vxxx/generations/Gxxx/`，跨视频共享资产生成放 `video/shared/generations/Gxxx/`。同一 G 内 Prompt、参考或关键设置发生变化时建立新 I；生成目标本身改变时建立新 G。正式 Prompt 只存在对应 G/I，不在资产或 Shot 目录复制第二份；只有真正影响执行、复现或排错的设置才进入正式记录。

一次性交付包只放在当前项目 `.tmp/`，使用 `.tmp/V001/G003_I02/` 或 `.tmp/shared/G003_I02/` 这类作用域路径。包只复制当前 I 真正需要的 Prompt、参考文件、职责、必要设置和返回说明；`scripts/generation_pack.py` 提供 `init`、`copy`、`seal`、`returns`、`status`、`zip` 与幂等 `receive`。

返回候选先由 `receive` 全部保存到正式 G，并建立 Take → I 映射；Take 在 G 内连续编号，切换 I 不重置。若用户在外部平台改变 Prompt、参考或关键设置，必须先把真实输入正式保存为正确 I，再接收结果。正式接收成功并确认临时包没有唯一信息后自动精确清理；清理失败时重跑同一 `receive`，不重新分配 Take。

Generation 不维护 selected / current take。图片 Take 的正式资产采用由资产记录固定来源；视频最终采用在正式时间线建立前可暂记唯一 Shot 表，建立正式剪辑后只由剪辑记录维护。具体模型能力在执行当前 I 时核验当前官方资料，不长期维护供应商适配 Package。
