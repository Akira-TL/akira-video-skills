# video-generation

`video-generation` 为 AI 图片、视频、声音或音乐建立正式 Generation（G）与 Input Version（I），维护唯一执行 Prompt、实际参考版本与必要设置，并把当前可并行执行的多个 G/I 组成一个外部生成批次。

Generation 跟随真正被生成的对象或视频任务。共享人物 / 地点 / 道具等对象自己的 G 放在对象目录内，例如 `video/shared/characters/CHR01/G001/`；直接服务视频或 Shot 的 G 放在 `video/V001_*/generations/G001/`。Generated Take 与 Prompt 共置在同一个 G，资产记录直接引用 `Gxxx/takeNN`，不复制第二份媒体。

一次外部执行使用一个 `video/batches/Bxxx/`。一个 B 可以包含多个互不阻塞的 G/I，根目录只有一份 README，共享参考只复制一次；`scripts/generation_pack.py` 提供 `init`、`add`、`build`、`status` 与幂等 `receive`。`build` 就地生成并保留 `Bxxx.tar.gz`，不再为每个 G 建 `.tmp` 包、handoff 或独立压缩包。

返回候选按 Batch task 保存回原 G 并建立 Take → I 映射。若 Prompt、参考或关键设置在外部执行前需要变化，先建立新的正式 I 和新的 B；Receive 不删除旧批次目录或 tar.gz。

Generation 不维护 selected / current take。图片 Take 的正式采用由对象记录指向原 G/take；视频最终采用在正式时间线建立前可暂记唯一 Shot 表，建立正式剪辑后只由剪辑记录维护。
