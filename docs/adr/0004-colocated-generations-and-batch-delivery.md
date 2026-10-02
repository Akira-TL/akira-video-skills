---
status: accepted
supersedes:
  - 0002-shared-assets-and-per-video-records.md
  - 0003-generation-traceability-and-pack-receive.md
---

# Generation 与生成对象共置，外部执行按批次交付

## 决定

视频项目采用以下存储与外部执行规则：

1. 单支视频直接位于 `video/Vxxx_<human-label>/`，不增加 `video/videos/` 中间层。
2. 可复用人物、地点、道具、声音等对象拥有自己的目录；对象自己的 Generation 直接位于对象目录中。
3. Generated Take 始终留在产生它的 G 中，与 `GENERATION.md` 和 `prompt_iXX.md` 共置；资产记录通过 G/take 表达采用版本，不复制第二份生成媒体。
4. 直接服务整支视频、Shot 或多对象任务的 G 继续位于 `Vxxx/generations/`。
5. 一次实际外部生成执行使用一个 `Bxxx` 批次。一个 B 可以包含多个互不阻塞的 G/I，同一参考在批次中只复制一次。
6. 批次位于 `video/batches/Bxxx/`，在该目录就地生成 `Bxxx.tar.gz`。Receive 后目录与 tar.gz 继续保留。
7. 一个 B 只有一份批次级执行说明；不为每个 Generation 创建 handoff / instructions / 独立压缩包。

## 目标结构

```text
video/
├── INDEX.md
├── shared/
│   ├── characters/CHR01/
│   │   ├── CHR01.md
│   │   ├── G001/
│   │   │   ├── GENERATION.md
│   │   │   ├── prompt_i01.md
│   │   │   └── take01.png
│   │   └── G002/
│   └── locations/LOC01/G001/
├── V001_<human-label>/
│   ├── VIDEO.md
│   ├── materials/
│   ├── generations/G001/
│   ├── shots/
│   └── edit/
└── batches/B001/
    ├── README.md
    ├── tasks/
    ├── references/
    ├── returns/
    └── B001.tar.gz
```

## 为什么移除 video/videos

`video/` 本身已经是视频产品边界，`Vxxx` 也有稳定前缀，不需要再用一层 `videos/` 做类型区分。直接放 `Vxxx` 可以减少路径长度，同时仍与 `shared/`、`batches/`、`INDEX.md` 清楚区分。

## 为什么对象拥有自己的 Generation

人物身份图、地点参考图等结果的自然上下文是被生成对象。把对象记录放在 `characters/CHR01/`、把真正的 Prompt 和 Take 放在另一个全局 `shared/generations/`，会让人浏览时来回跳转，并诱导复制 `CHR01_ref_v01.png` 作为第二份媒体。

对象目录内的 G 同时保存正式 Prompt 与实际输出；对象记录只维护设计、逻辑版本、采用关系和用途。这样 Generated media 只有一份。

## 为什么按 B 批次交付

外部平台的一次工作通常会连续执行多个已经准备好的任务。若每个 G 都建立临时目录、README、参考副本和压缩包，会重复上传相同人物 / 地点参考，也增加用户操作次数。

`Bxxx` 表达一次真实外部执行：多个 G/I 可共享参考与一份说明，`tar.gz` 只用于方便传输。批次本身不是新的事实源，但保留能直接回答“这一轮实际给平台交了什么”。

## 输入变化

正式 G/I 仍是输入权威来源。B build 后若 Prompt、参考或关键设置需要变化，先建立正确的新 I，再建立新的 B；不修改旧 B 后继续把结果归入旧输入。

## Receive

Receive 根据 Batch task 映射把返回候选写回各自原 G，并分配该 G 内连续 Take。Receive 可幂等重跑，但不会清理 B 目录或 tar.gz。

## 仍然不变的边界

- Generation 与 Shot 继续多对多；
- Prompt 正文只属于对应 I；
- Generation 不维护最终 selected take；
- 正式剪辑建立后，最终 Take / 时间范围 / 复用 / 拼接关系只由剪辑记录维护；
- `video/batches/` 默认不进入 Git，它是保留在本地的可重建执行快照。
