# Akira Video Skills

`akira-video-skills` 是面向单 Agent 连贯推进的 AI 视频制作 Skill 产品仓。项目按长期共享资产、单支视频、Generation / Input Version / Take 和正式剪辑关系组织；Skill 表达专业方法，不模拟剧组部门交接。

## 工作方式

`akira-video` 只负责定位 / 初始化目标 `Vxxx`，随后进入 `video-production`。Production 是单支视频唯一流程负责人，根据真实依赖按需调用 Director、Script、Visual Design、Storyboard、Cinematography、Audio、Generation、Review 和 Editing。

项目核心结构：

```text
video/
├── INDEX.md                    # 多视频时按需
├── shared/                     # 跨视频资产 / shared generations
└── videos/
    └── V001_<human-label>/
        ├── VIDEO.md            # 当前视频主要制作稿
        ├── scenes/             # 按规模
        ├── materials/          # 本视频专属复用资产
        ├── generations/
        ├── shots/              # 个别复杂 Shot 按需
        └── edit/               # 正式后期按需

.tmp/V001/G003_I02/           # 自包含 outbound pack
.tmp/shared/G003_I02/
```

Generation 与 Shot 解耦：一个 G 可以覆盖多个 Shot，一个 Shot 可以由多个 G / Take 拼接。Prompt 正文只属于对应 Input Version；Take 只记录可独立 Review 的候选结果，最终采用关系由资产记录或正式剪辑记录维护。

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
- `video-generation`：G/I、Prompt、outbound pack、幂等 Receive 和 Take；
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

当前新拓扑的确定性制作案例位于 `tests/test_production_workflow_cases.py`，覆盖一次性短片、跨视频共享资产版本升级、真实输入变化、分批返回与中断恢复；其余契约与 CLI 回归分别由对应 `tests/test_*` 文件维护。
