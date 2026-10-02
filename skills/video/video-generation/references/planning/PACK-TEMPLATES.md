# 生成批次目录模板

批次目录只服务一次实际外部执行。长期事实仍来自正式 G/I、资产记录与视频记录。

## 1. 批次根目录

一个批次根目录只保留一份 README.md：

```text
video/batches/B001/
├── README.md
├── tasks/
│   ├── CHR01_G001_I01/
│   │   └── prompt.md
│   └── V001_G003_I01/
│       └── prompt.md
├── references/
├── returns/
└── B001.tar.gz
```

不为每个 G 建 handoff、README 或 instructions 文件。

## 2. task

每个 task 对应一个正式 G/I。最小 task 只有：

```text
tasks/<task>/prompt.md
```

Prompt 从正式 `prompt_iXX.md` 复制。执行目标、正式 Generation 路径、Input Version、参考列表与返回目录统一列在批次根 README。

## 3. references

所有需要上传的参考统一放在 `references/`。同一人物 / 地点 / 产品参考被多个 task 使用时，共享参考只保留一份。

参考文件名应让人可以直接辨认，例如：

- `references/CHR01_identity.png`；
- `references/LOC01_four-view.png`；
- `references/PROD01_official-front.png`。

如果不同来源同名，使用明确对象 ID 或职责重命名；不要覆盖。

## 4. returns

每个 task 的候选放到：

```text
returns/<task>/
```

同一个 task 的多个候选全部放在该目录，Receive 再统一映射成原 G 中连续的 `takeNN`。

## 5. README

批次 README 至少说明：

- 本批有哪些 task；
- 每个 task 对应哪个正式 Generation / I；
- Prompt 在哪里；
- 使用哪些共享参考；
- 返回结果放到哪个 `returns/<task>/`。

这份 README 是整批唯一执行说明，不复制 Prompt 正文。

## 6. tar.gz

`build` 在当前 B 目录就地生成 `Bxxx.tar.gz`，压缩 README、tasks、references；不包含内部 metadata、returns 或 tar.gz 自己。

批次目录与 tar.gz 在 Receive 后继续保留。需要清理时由用户或项目自己的存储策略决定，不由 Receive 自动删除。

## 7. 驳回后的下一轮

如果 Review 判断某任务需要改 Prompt、设计、参考或关键设置：

1. 先修改正式归属；
2. 在原 G 建立新的 I，或在目标改变时建立新 G；
3. 建立新的 B；
4. 不修改旧 B 来伪装新的实际输入。

## 完成标准

一次外部执行只有一个批次目录和一个 tar.gz；Prompt、共享参考与返回位置都一眼可找；批次不会因为 G 数量增加而复制大量 handoff 与相同参考。
