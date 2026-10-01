# 项目规模与版本管理

默认项目保持浅结构。本文件只在当前视频已经大到平铺影响阅读，或确实需要同时比较创意版本时使用。

## 1. 默认不创建章节层级

普通短片保持：

```text
video/
├── script/
├── materials/
├── shots/
└── edit/        # 按需
```

不要为了“以后可能很长”提前创建 chapter / episode / sequence 多层目录。

## 2. 什么时候增加章节

只有出现以下情况之一时才增加组织层：

- 当前 `VIDEO.md` / 场景 Shot 表或少量独立 Shot 记录已经难以浏览；
- 一个视频项目真实包含多个章节 / 集数 / 明确独立段落；
- `SCRIPT.md` 已经长到无法快速定位当前制作段落；
- 用户明确希望按章节组织当前视频制作。

可选示例：

```text
video/
├── script/
│   ├── SCRIPT.md          # 整体改编 / 导航仍可保留
│   └── chapters/
│       ├── CH01.md
│       └── CH02.md
└── shots/
    ├── chapter-01/
    │   ├── SC01_SH010/
    │   └── SC01_SH020/
    └── chapter-02/
```

这只是组织示例，不要求所有长项目同时建立 `SCRIPT.md + chapters/ + chapter folders`；使用满足当前浏览需要的最少层级。

## 3. 上游小说章节不等于视频章节

小说 Skill 的章节结构仍归上游内容所有。

视频可以：

- 一个视频只改编小说一个章节；
- 多个小说章节压缩成一个视频段落；
- 一个小说章节拆成多个视频章节；
- 完全不用视频章节，只保留 Scene / Shot。

不要把小说目录机械复制进 `video/`。

## 4. 普通修改使用 Git

`SCRIPT.md`、`*_design.md`、`SHOT.md`、长期提示词等只有一个当前有效版本时，直接修改原文件，由 Git 保存历史。

不要创建：

- `SCRIPT_final.md`；
- `SCRIPT_final2.md`；
- `CHARACTER_new.md`；
- `SHOT_real_final.md`。

## 5. 两个方案需要同时比较

只有确实需要并行比较两套创意内容时，才临时保留明确变体。

故事级可以使用：

`SCRIPT_variant-a.md`
`SCRIPT_variant-b.md`

设计级可以使用：

`CHR01_design_variant-a.md`
`CHR01_design_variant-b.md`

单镜头通常不复制整个镜头目录；优先用多个提示词版本和生成结果比较。

选定方案后：

1. 把选中内容合并回当前正式文件；
2. 删除不再需要的临时 variant 文件；
3. 由 Git 保留决策前后的历史。

## 6. 后期版本

普通后期修改留在同一个工程里。

需要给用户 / 客户比较阶段导出时可以使用：

`review_v01.mp4`
`review_v02.mp4`

如果真的同时维护两个不同创意剪辑，文件名应描述区别，例如：

`edit_fast-cut.prproj`
`edit_dialogue-led.prproj`

而不是 `final_a` / `final_b`。

## 7. VIDEO.md

如果当前存在多个活跃变体，`VIDEO.md` 只需要指出：

- 当前正在比较哪些版本；
- 当前推荐 / 正在推进哪一个；
- 还缺什么决定。

方案确定后清理这段临时状态。

## 完成标准

短片项目仍然一眼可懂；长项目只有真实复杂度出现时才增加一层组织；版本历史主要由 Git 保存，不在文件系统里长出永久版本树。
