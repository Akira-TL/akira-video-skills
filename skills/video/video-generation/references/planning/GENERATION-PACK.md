# 生成批次与外部执行

生成批次把当前可以一起执行的多个正式 G/I 组织成一次外部生成交付。批次只是执行快照；Prompt、参考来源和最终 Take 的正式归属仍在原项目对象与 Generation。

## 1. 一个批次可以包含多个 Generation

同一轮实际外部生成中，只要任务之间没有真实先后依赖，就应放进同一个 `Bxxx`，而不是每个 G 单独打包。

例如：

- CHR01 身份图 G001；
- LOC01 空场环境 G001；
- V001 的两个独立 Shot G003 / G004；

如果它们输入都已齐全，可以进入同一个 B。真正依赖前一任务返回结果的下游 G 留到下一批。

## 2. 批次位置

批次固定在项目内：

```text
video/batches/B001/
├── README.md
├── tasks/
│   ├── CHR01_G001_I01/
│   │   └── prompt.md
│   └── V001_G003_I02/
│       └── prompt.md
├── references/
│   ├── CHR01_identity.png
│   └── LOC01_four-view.png
├── returns/
│   ├── CHR01_G001_I01/
│   └── V001_G003_I02/
└── B001.tar.gz
```

`video/batches/` 默认由 CLI 写入 `.gitignore`。它不放到 `.tmp/`，也不在 Receive 后自动删除。

## 3. 共享参考只复制一次

一个批次中的多个任务可以共同使用同一份人物、地点、产品或动作参考。共享参考只复制一次到 `references/`，各 task 在 README / Prompt 中引用同一批次相对路径；不要为每个 Generation 再复制一套相同参考。

## 4. 每个 G 只带执行 Prompt

`tasks/<task>/prompt.md` 是对应正式 `prompt_iXX.md` 的执行快照。一个批次根目录只保留一份 README；不为每个 Generation 创建 handoff、instructions 或第二份 README。

正式 Prompt 仍只维护在原 G/I。若 build 后实际要改 Prompt、参考或关键设置，先回正式 G 建立正确的新 I，再建立新的 B；不要直接修改旧批次并把结果挂回原 I。

## 5. 就地生成 tar.gz

`generation_pack.py build` 直接把当前 B 的 README、tasks 和 references 打成同目录 `B001.tar.gz`。不需要额外 staging 目录，也不使用 zip。

原批次目录继续保留，tar.gz 只是方便一次性交付的压缩表示。

## 6. 返回与 Receive

用户把每个 task 的所有候选放入对应 `returns/<task>/`。`receive` 按批次 metadata 把候选导回各自正式 Generation，并分配 G 内连续 `takeNN`。

生成出的 Take 留在原 G 中，与 `GENERATION.md` 和 `prompt_iXX.md` 共置。图片被采用为人物 / 地点参考时，资产记录直接指向该 G/take，不复制第二份媒体。

Receive 不删除批次目录或 tar.gz。批次目录与 tar.gz 保留，方便回看当时一次实际外部执行到底包含哪些任务和参考。

## 7. 批次输入冻结

build 时记录 README、tasks 与 references 的内容摘要。Receive 前若这些输入发生变化，CLI 会拒绝接收，并要求把真实输入正式化为新的 G/I / Batch；不通过隐藏 snapshot 或临时副本猜测真实输入。

## 8. 常用 CLI

```text
generation_pack.py init <project> B001
generation_pack.py add <project> B001 video/V001_demo/generations/G003 --input I02 --reference video/shared/characters/CHR01/G001/take02.png
generation_pack.py add <project> B001 video/V001_demo/generations/G004 --input I01 --reference video/shared/characters/CHR01/G001/take02.png
generation_pack.py build <project> B001
generation_pack.py status <project> B001
generation_pack.py receive <project> B001
```

## 完成标准

一次实际外部执行只有一个清楚的 B 批次；多个 G/I 能共享参考；用户拿到一个 `tar.gz` 即可执行；返回结果进入各自原 G，批次自身保留且不成为第二份正式媒体来源。
