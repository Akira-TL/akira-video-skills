# 视频项目目录

对象与文件命名统一按 [`NAMING.md`](NAMING.md)。

默认保持最浅、最容易浏览的结构：

```text
PROJECT/
├── VIDEO.md
├── <其他 Skill 拥有的项目内容>
├── video/
│   ├── script/
│   ├── materials/
│   ├── shots/
│   └── edit/        # 仅进入整片后期时创建
└── .tmp/            # 一次性生成包，不进入 Git
```

## script

只保存当前视频自己的制作定义。按真实需要创建：

```text
video/script/
├── SCRIPT.md
├── CHARACTERS.md
├── SCENES.md
└── SHOTS.md
```

这些文件可以缺省。视频 Skill 不把上游小说、章节、世界观或完整人物档案复制到这里；这里只记录视频改编、表演、视觉和镜头需要的转换结果与 pointer。

## materials

保存多个镜头会重复使用的内容。类别按真实项目出现，例如：

```text
video/materials/
├── characters/
├── scenes/
├── props/
├── products/
└── references/
```

不预建空目录。一个类别目录可以同时包含提示词与对应图片，例如：

```text
video/materials/characters/
├── CHR01_prompt.md
├── CHR01_identity.png
└── CHR01_costume-a.png
```

## shots

每个镜头集中保存自己的长期内容：

```text
video/shots/SC01_SH010/
├── SHOT.md
├── prompt_v01.md
├── prompt_v02.md
├── take01.mp4
└── take02.mp4
```

镜头专属图片、对白、声音或其他产物也放这里。首帧、尾帧、分镜草图 / 关键帧等只服务当前镜头的图片不进入公共 `materials/`；常用命名见 `NAMING.md`。项目复杂度增加时允许在 `video/script/`、`video/shots/` 内按真实需要增加章节等组织层，但默认保持最浅可读层级；启用条件和版本管理见 [`SCALING-VERSIONS.md`](SCALING-VERSIONS.md)。

## edit

只有进入整片级后期时才创建。保存 Premiere Pro、After Effects、DaVinci Resolve 等工程、全片级音乐/旁白/混音及最终成片。镜头专属内容仍留在对应镜头。

## tmp

`.tmp/` 保存一次性生成包。视频项目第一次需要一次性生成包前，确认目标项目自己的 `.gitignore` 包含：

```text
.tmp/
```

不要求提前创建空 `.tmp/` 目录。包里的提示词和参考素材均从正式项目复制或编译而来；生成结果已经导回 owning 目录后删除整个包。
