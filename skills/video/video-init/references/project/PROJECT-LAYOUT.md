# 视频项目目录

Akira Video 使用“共享对象 + 单支视频 + 生成批次”结构。复杂度按真实需要出现，不为模板完整创建空目录。对象命名见 [`NAMING.md`](NAMING.md)。

```text
PROJECT/
├── <其他 Skill 拥有的上游内容>
└── video/
    ├── INDEX.md                         # 多视频时按需，只做导航
    ├── shared/                          # 跨视频复用对象
    │   ├── characters/
    │   │   └── CHR01/
    │   │       ├── CHR01.md            # 设计、采用版本与用途
    │   │       └── G001/
    │   │           ├── GENERATION.md
    │   │           ├── prompt_i01.md
    │   │           └── take01.png      # 生成结果与 Prompt 共置
    │   ├── locations/
    │   │   └── LOC01/
    │   │       └── G001/
    │   ├── props/
    │   └── voices/
    ├── V001_<human-label>/             # 单支视频直接位于 video/ 下
    │   ├── VIDEO.md
    │   ├── scenes/                     # 长视频按需
    │   ├── materials/                  # 当前视频专属复用对象，结构与 shared 相同
    │   ├── generations/                # 整支视频 / Shot / 多对象生成任务
    │   │   └── G001/
    │   │       ├── GENERATION.md
    │   │       ├── prompt_i01.md
    │   │       └── take01.mp4
    │   ├── shots/                      # 个别复杂 Shot 按需
    │   └── edit/                       # 真正进入后期时
    └── batches/
        └── B001/
            ├── README.md               # 整批唯一执行说明
            ├── tasks/                  # 本批各 G/I 的执行 Prompt 副本
            ├── references/             # 本批共享参考只复制一次
            ├── returns/                # 按 task 收回候选
            └── B001.tar.gz             # 就地压缩，Receive 后仍保留
```

## 单支视频

`Vxxx_<human-label>/` 直接位于 `video/` 下，不再增加一层 `video/videos/`。`video/INDEX.md` 只在确实需要多视频导航时创建；单视频项目可以只有 `video/V001_.../VIDEO.md`。

## 共享对象与对象生成

人物、地点、道具和声音按对象归档。某个对象自己的生成任务直接放在该对象目录内，例如 `video/shared/characters/CHR01/G001/`。

Generated Take 永远留在产生它的 G 中，与 `GENERATION.md` 和对应 `prompt_iXX.md` 共置。资产记录通过 `G001/take02.png` 之类的路径指向采用结果；不要为了“资产版本”再复制一份 `CHR01_ref_v01.png`。

外部导入、人工绘制或其他非 Generation 来源的正式参考可以直接放在对象目录，由对象记录说明来源。

## 当前视频专属复用对象

`Vxxx/materials/` 只放当前视频专属但跨多个 Shot 复用的对象。若这些对象也需要生成，沿用与 `shared/` 相同的“对象目录内建 G”规则。

## 视频 Generation

不属于某个可复用对象、而是直接服务整支视频、一个或多个 Shot、视频延长、声音片段等任务时，放在 `Vxxx/generations/Gxxx/`。Generation 与 Shot 仍保持多对多。

## 生成批次

外部生成交付按一次实际执行批次建立 `video/batches/Bxxx/`。一个批次可以包含多个互不阻塞的 G/I；同一参考只在批次 `references/` 中复制一次。批次目录与 `tar.gz` 都保留，不在 Receive 后自动删除。

`video/batches/` 是可重建执行快照，默认由生成批次 CLI 加入项目 `.gitignore`，不作为长期事实源。

## edit

只有建立正式时间线 / 后期时创建 `Vxxx/edit/`。一旦正式剪辑时间线存在，最终视频实际使用的 Take、时间范围、复用与拼接关系以剪辑记录为唯一来源。
