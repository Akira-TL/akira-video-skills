# 整片后期工程组织

`video/edit/` 只在进入整片后期时创建，并保持尽量浅。

## 1. 最小示例

```text
video/edit/
├── project.prproj
├── master-audio.wav
└── master.mp4
```

实际使用 After Effects、DaVinci Resolve 或其他软件时，把 `project.prproj` 换成真实工程文件即可。

如果项目只有一个工程、一个主混音和一个成片，不要再创建 `project/`、`audio/`、`delivery/` 等子目录。

## 2. 什么时候才加子目录

只有文件数量已经明显影响浏览时，才按真实用途增加少量子目录，例如：

- 多个合成工程；
- 大量 review export；
- 多语言字幕；
- 多平台成片变体。

目录来自真实复杂度，不来自模板。

## 3. 导出命名

正式成片优先用用途命名，而不是 `final`：

- `master.mp4`；
- `master_vertical.mp4`；
- `master_subtitled.mp4`；
- `master_clean.mp4`。

需要同时保留多个审片版本时才使用：

- `review_v01.mp4`；
- `review_v02.mp4`。

普通修改由后期工程和 Git / 项目历史管理，不无限累积 `final2`。

## 4. 声音

镜头专属对白 / 音效仍留在镜头。

进入整片后的全片音乐、旁白、总混音可以直接放在 `video/edit/`，例如：

- `music.wav`；
- `voiceover.wav`；
- `master-audio.wav`。

不单独建立一级 `audio/`。

## 5. 媒体来源

后期工程使用各镜头当前采用的生成结果。为了软件代理、缓存或渲染而生成的可重建文件按具体软件管理，不把它们误当成新的长期视频源。

## 完成标准

`video/edit/` 只保存整片级真正需要的工程与输出，人打开目录能直接找到工程、主声音和成片。
