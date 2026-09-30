# Akira Video Skills

`akira-video-skills` 是 Akira 的 AI 视频制作 Skill 产品仓。它服务于从上游故事、小说、品牌资料或用户素材到视频脚本、角色 / 场景与灯光设计、声音、复用素材、镜头、外部生成交接、真实结果审片和整片后期的制作过程。

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

用户需要在外部模型生成素材或视频时，Agent 从正式项目内容整理项目内 `.tmp/` 一次性生成包；`video-generation` 自带 CLI 负责安全复制、`takeNN` 分配、返回归档和清理。结果返回后由 `video-review` 基于实际图片 / 视频 / 声音审片，审片辅助 CLI 只提供元数据、抽帧和严格 2×2 分格，不替代内容判断；最终成片再由 `video-editing` 的技术 QC CLI 做完整解码与显式交付参数检查。

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

模型适配器（in-progress，按需安装）：

- `video-model-runway`：Runway 当前模型提示词 / 能力适配。
- `video-model-veo`：Google Veo 当前入口 / stable / preview 能力适配。
- `video-model-seedance`：Seedance 当前多模态参考、时间线、声音、编辑与延长适配。

所有模型适配器遵守统一契约：先固定实际使用入口、精确模型 / 版本和任务模式，再按当前官方资料核验动态能力；模型限制不能反向改写镜头、角色或产品事实。

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

独立黑盒模板和固定 synthetic fixtures 位于 `tests/blackbox/`，当前覆盖模型适配器、核心制作交接、跨会话返回参考和返回视频审片等关键边界。
