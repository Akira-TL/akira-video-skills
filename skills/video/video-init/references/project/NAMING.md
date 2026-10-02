# 视频项目命名

命名目标是稳定身份 + 人类可读，不把供应商、全部参数或状态机塞进文件名。

## 1. 核心对象 ID

- `V001`：一支独立交付视频 / 一集；
- `B001`：一次外部生成执行批次；
- `G001`：某个归属对象或视频范围内的 Generation；
- `I01`：某个 G 的正式 Input Version；
- `take01`：某个 G 内可独立 Review 的候选结果；
- `SC01`：叙事场景 / 场次；
- `SH010`：最终叙事 / 剪辑 Shot；
- `CHR01` / `LOC01` / `PROP01` / `PROD01`：人物 / 地点 / 道具 / 真实产品。

只创建真实需要的 ID。

## 2. 视频目录

物理目录可写 `video/V001_档案室钥匙/`，但正式身份只认 `V001`。不再增加 `video/videos/` 中间层。改标题通常不改目录；必要时改助记后缀也不改变 V 身份。

## 3. Generation 归属

Generation 跟随它生成的对象或视频任务：

- 共享人物：`video/shared/characters/CHR01/G001/`，引用可写 `CHR01/G001`；
- 共享地点：`video/shared/locations/LOC01/G001/`，引用可写 `LOC01/G001`；
- 当前视频专属复用对象：放在 `V001/materials/<category>/<object>/Gxxx/`；
- 直接服务视频 / Shot 的任务：`video/V001_<label>/generations/G001/`，跨视频引用写 `V001/G001`。

同一对象或 V 范围内 G 编号单调增加；不因为换模型重新建一套供应商编号。

## 4. Prompt 与 Input Version

正式 Prompt 只存在对应 I，例如 `prompt_i01.md`、`prompt_i02.md`。修改 Prompt、参考版本或关键执行输入但生成目标不变时通常新建 I。

## 5. Take

Take 在一个 G 内单调递增，切换 I 不重置：`take01.png`、`take02.mp4`、`take03/`。Take 与 Prompt 保存在同一个 G 目录；Generated media 不再复制到另一套资产版本文件。

## 6. 资产采用版本

资产记录可以维护逻辑版本，但直接指向原 Generation Take，例如：

```text
v01 → G001/take02.png
v02 → G003/take01.png
Current reference: v02
```

这样版本关系清楚，同时不重复保存二进制文件。外部导入或人工处理产生的新正式文件仍可使用清楚的用途名。

## 7. 生成批次

`B001` 表示一次实际交给外部平台执行的一批任务。目录固定为 `video/batches/B001/`，压缩文件为同目录的 `B001.tar.gz`。一个 B 可以包含多个 G/I；一个 G 在下一次实际外部执行时也可以进入新的 B。

## 8. Shot

默认使用留空编号 `SH010`、`SH020`，需要场景上下文时可写 `SC01_SH010`。简单视频只在唯一 Shot 表维护，不强制目录。

## 9. 最终导出

多语言 / 多画幅只有真实并存时加明确后缀，例如 `master.en-US.mp4`、`master_vertical.en-US.mp4`。不要为了未来可能本地化提前给所有文件加语言后缀；不要使用 `final2`、`new_final`、`real_final`。

## 10. 文件名不承担的内容

默认不把供应商、模型名、seed、FPS、分辨率、全部参考或 Prompt hash 塞进媒体文件名。这些有长期价值时写入对应 I / 批次记录。
