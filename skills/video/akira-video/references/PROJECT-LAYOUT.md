# 视频项目目录

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

不预建空目录。一个类别目录可以同时包含 Prompt 与对应图片，例如：

```text
video/materials/characters/
├── CHR01_prompt.md
├── CHR01_identity.png
└── CHR01_costume-a.png
```

## shots

每个 Shot 集中保存自己的长期内容：

```text
video/shots/SC01_SH010/
├── SHOT.md
├── prompt_v01.md
├── prompt_v02.md
├── take01.mp4
└── take02.mp4
```

镜头专属图片、对白、声音或其他产物也放这里。复杂项目只有在平铺已经影响阅读时，才在 `shots/` 内增加章节等组织层。

## edit

只有进入整片级后期时才创建。保存 Premiere Pro、After Effects、DaVinci Resolve 等工程、全片级音乐/旁白/混音及最终成片。镜头专属内容仍留在对应 Shot。

## tmp

`.tmp/` 保存一次性生成包，必须 gitignore。包里的 Prompt 和参考素材均从正式项目复制或编译而来；生成结果已经导回 owning 目录后删除整个包。
