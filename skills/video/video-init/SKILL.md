---
name: video-init
description: 初始化 Akira Video 项目的最小文件与目录骨架；当当前项目尚未建立 video/ 结构或需要创建新的 Vxxx 视频工作目录时使用，不负责创意、剧情、视觉或镜头决策。
---

# Video Init

本 Skill 只负责**建立可开始工作的最小视频项目骨架**。它不讨论这支片应该讲什么、拍多久、是什么风格，也不替代 `video-production` 的制作判断。目录约定按 [`references/project/PROJECT-LAYOUT.md`](references/project/PROJECT-LAYOUT.md)，稳定 ID 与文件命名按 [`references/project/NAMING.md`](references/project/NAMING.md)。

## 1. 判断初始化范围

先检查当前项目已有内容，不覆盖已有视频结构。

- 没有 `video/`：建立项目视频根；
- 已有 `video/` 但没有目标视频：创建下一个稳定 `Vxxx`；
- 已有目标 `Vxxx`：不重复初始化，交给 `video-production` 恢复；
- 多视频项目需要导航时按需创建 `video/INDEX.md`；只有一支视频时可以不建。

视频目录身份只认 `Vxxx`。物理目录可以带人类助记后缀，例如 `V001_档案室钥匙/`，但任何 Agent / 文件引用只使用 V ID。

## 2. 最小结构

新视频至少建立 `video/videos/Vxxx_<human-label>/VIDEO.md`。只有真实需要时再创建 `video/shared/`、`Vxxx/scenes/`、`Vxxx/materials/`、`Vxxx/generations/`、`Vxxx/shots/` 或 `Vxxx/edit/`；不要为了模板完整创建空目录。

## 3. 初始化 VIDEO.md

新 `VIDEO.md` 只写足够让 Production 接手的最小信息：视频 ID、用户已经明确给出的标题 / 工作名、已知来源 pointer 和当前状态。用户已经给出的创意要求、时长、平台、剧情等信息可以原样保留，但 Init 不主动扩写或解释。

## 4. 上游内容不搬家

小说、章节、世界观、品牌资料或其他上游内容继续留在原有体系。视频目录只记录 pointer / 采用范围，不复制上游正文建立第二份事实源。

## 完成标准

项目存在一个稳定可定位的 `Vxxx/VIDEO.md`，没有预创建不需要的目录，也没有在初始化阶段替用户做创意决策。随后立即交给 `video-production`。
