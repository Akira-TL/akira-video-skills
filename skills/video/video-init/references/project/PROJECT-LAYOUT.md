# 视频项目目录

Akira Video 使用**共享资产层 + 单支视频层**。复杂度按真实需要出现，不为模板完整创建空目录。对象命名见 [`NAMING.md`](NAMING.md)。

```text
PROJECT/
├── <其他 Skill 拥有的上游内容>
├── video/
│   ├── INDEX.md                  # 多视频时按需，只做导航
│   ├── shared/                   # 跨视频复用资产，按需
│   │   ├── characters/
│   │   ├── locations/
│   │   ├── props/
│   │   ├── voices/
│   │   └── generations/
│   └── videos/
│       └── V001_<human-label>/
│           ├── VIDEO.md          # 当前视频唯一主要制作稿
│           ├── scenes/           # 长视频按需
│           ├── materials/        # 本视频专属复用资产
│           ├── generations/
│           ├── shots/            # 个别复杂 Shot 按需
│           └── edit/             # 真正进入后期时
└── .tmp/                         # outbound pack，gitignored
```

## INDEX

`video/INDEX.md` 只在多视频项目需要导航时创建。它列视频 ID、状态和 shared 入口，不复制单支剧情、Generation、Take 或剪辑状态。单视频可以没有 INDEX，但仍使用 `video/videos/Vxxx_*/VIDEO.md`，以后扩成多视频无需搬目录。

## shared

人物、地点、道具、声音和参考图默认考虑跨视频复用。资产记录与二进制版本共置；正式生图 Prompt 不在资产目录复制，唯一正文属于对应 shared Generation / Input Version。

## 单支 Vxxx

`VIDEO.md` 是该视频主要制作稿。正文过长时按场景拆 `scenes/SCxx.md`，拆出后原位置只留概要 / 链接。`materials/` 只放本视频专属但跨镜头复用资产；Generation 与 Shot 不互为父子。

简单视频不要求建立 `shots/`：唯一 Shot 表可以直接在 `VIDEO.md`。只有某个 Shot 需要独立资料时再创建文件 / 目录。

## generations

正式 Generation 在当前 scope 内保存 G/I/Take：视频任务放 `Vxxx/generations/Gxxx*/`，跨视频共享资产生成放 `video/shared/generations/Gxxx*/`。Take 不放回 Shot 目录。

## edit

只有建立正式时间线 / 后期时创建 `Vxxx/edit/`。一旦正式剪辑时间线存在，最终视频实际使用的 Take、时间范围、复用与拼接关系以剪辑记录为唯一来源。

## tmp

`.tmp/V001/G003_I02/` 或 `.tmp/shared/G003_I02/` 是可重建 outbound pack。Receive 正式保存结果与真实输入后自动精确清理；`.tmp` 不是事实源。
