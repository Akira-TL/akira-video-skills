# Akira Video Skills

`akira-video-skills` 是 Akira 的 AI 视频制作 Skill 产品仓。它服务于从上游故事、小说、品牌资料或用户素材到视频脚本、复用素材、镜头生成、审片和整片后期的制作过程。

## 工作方式

完整视频项目由 `akira-video` 路由。项目根目录使用 `VIDEO.md` 作为当前视频制作首页；长期制作内容保持浅层、面向人的结构：

```text
PROJECT/
├── VIDEO.md
├── <其他 Skill 拥有的项目内容>
├── video/
│   ├── script/
│   ├── materials/
│   ├── shots/
│   └── edit/        # 仅进入整片后期时创建
└── .tmp/            # 一次性生成包，gitignored
```

`video/script/` 保存当前视频自己的脚本和制作定义，不重新拥有小说、章节或其他上游事实；`video/materials/` 保存跨镜头复用的提示词、图片和参考素材；每个镜头的定义、提示词版本、生成图片/视频和镜头专属声音集中在自己的 `video/shots/<shot-id>/` 中。

用户需要在外部模型生成素材或视频时，Agent 从正式项目内容整理一次性生成包。结果返回后归档到正式目录，临时包删除。

## Skills

稳定 Skill 位于 `skills/video/`。尚未稳定的模型适配能力位于 `skills/in-progress/`。

稳定核心：

- `akira-video`：完整 AI 视频制作 Primary Router。
- `video-script`：把上游内容转换成当前视频脚本层。
- `video-design`：把人物 / 场景功能需求设计成可辨认、可复用的视觉方案，并按需处理多个视觉世界、空间和陌生机械。
- `video-audio`：管理角色跨镜头声音一致性、声音参考和镜头 / 整片声音职责边界。
- `video-materials`：管理跨镜头复用的提示词、严格四视图、图片与参考素材。
- `video-shot`：维护单镜头 `SHOT.md`、连续性与生产定义。
- `video-generation`：编写生成提示词、整理一次性生成包并导回结果。
- `video-review`：审核复用素材和生成结果，决定采用、后期修复或重生成。
- `video-editing`：按需组织整片级后期工程和最终成片。

可选领域：

- `video-advertising`：品牌、产品真实性与广告叙事边界。

## Installation

入口 Package：

```text
akira-tl/akira-video-skills/akira-video
```

运行时安装与依赖解析由 Skiloom 管理；本地维护 checkout 不作为运行时 source。

## Development

```bash
./scripts/list-skills.sh
skiloom validate . --json
./scripts/check.sh
```
