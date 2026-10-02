# Akira Video Skills

`akira-video-skills` 是面向单 Agent 连贯推进的 AI 视频制作 Skill 产品仓。项目按长期共享资产、单支视频、Generation / Input Version / Take 和正式剪辑关系组织；Skill 表达专业方法，不模拟剧组部门交接。

## 工作方式

`akira-video` 只负责定位 / 初始化目标 `Vxxx`，随后进入 `video-production`。Production 是单支视频唯一流程负责人，根据真实依赖按需调用 Director、Script、Visual Design、Storyboard、Cinematography、Audio、Generation、Review 和 Editing。

项目核心结构：

```text
video/
├── INDEX.md                         # 多视频时按需
├── shared/
│   ├── characters/CHR01/G001/      # 对象记录 + Prompt + Generated Take 共置
│   └── locations/LOC01/G001/
├── V001_<human-label>/
│   ├── VIDEO.md
│   ├── scenes/
│   ├── materials/                  # 当前视频专属复用对象
│   ├── generations/                # 直接服务视频 / Shot 的 G
│   ├── shots/
│   └── edit/
└── batches/B001/
    ├── README.md
    ├── tasks/
    ├── references/
    ├── returns/
    └── B001.tar.gz
```

Generation 与 Shot 解耦：一个 G 可以覆盖多个 Shot，一个 Shot 可以由多个 G / Take 拼接。Prompt 与 Generated Take 保存在同一个 G；对象采用版本直接引用对应 G/take，不复制第二份媒体。一次实际外部执行使用一个 B 批次，可同时包含多个 G/I，并共享一份参考素材。

## Stable Skills

- `akira-video`：Primary Router，只选择 / 初始化目标视频并进入 Production；
- `video-init`：只初始化最小项目骨架；
- `video-production`：单支视频唯一流程负责人；
- `video-director`：整片级表达、叙事、表演、节奏与高层创作策略；
- `video-script`：正式剧情、动作、对白与旁白；
- `video-visual-design`：人物、地点、道具 / 机械、整体视觉和参考资产准备；
- `video-storyboard`：Shot List、动作衔接、时长、计划连续性和 Animatic；
- `video-cinematography`：机位、构图、运动、透视、焦点、曝光和镜头级用光；
- `video-audio`：声音身份与声音设计；
- `video-generation`：G/I、Prompt、多 G/I 生成批次、`tar.gz`、幂等 Receive 和 Take；
- `video-review`：真实候选 QA、问题范围和返修判断；
- `video-editing`：正式时间线、最终采用关系、后期和交付；
- `video-advertising`：可选品牌 / 产品事实与广告边界。

具体模型不维护长期 Adapter Package；执行当前 G/I 时按当前官方资料核验真实模型 / 入口能力。

## Installation

入口 Package：`akira-tl/akira-video-skills/akira-video`。运行时安装与依赖由 Skiloom 管理，本地维护 checkout 不作为运行时 source。

## Development

```bash
./scripts/list-skills.sh
skiloom validate . --json
./scripts/check.sh
```

当前新拓扑的确定性制作案例位于 `tests/test_production_workflow_cases.py`，覆盖单支视频直放 `video/Vxxx`、共享对象 Generation 共置、多 G/I 批次执行、资产版本直接引用 Take 与新 I / 新 Batch 迭代；其余契约与 CLI 回归分别由对应 `tests/test_*` 文件维护。
