# Changelog

## Unreleased

- 初始化 Akira Video Skills 独立产品仓。
- 建立面向人的浅层视频项目目录、`VIDEO.md`、一次性生成包与 Shot 归档边界。
- 建立 `akira-video` Primary Router。
- 增加视频脚本、复用素材、镜头、生成包、审片、整片后期六个稳定核心 Skill。
- 增加品牌与产品项目的可选 `video-advertising` Skill。
- 将剧情因果与对白、多视角/机械参考、镜头导演与连续性、Take QA、最终成片 QC、产品事实等详细规范下沉为按需 references，避免稳定 Skill 主入口膨胀。
- 增加 `video-model-runway`、`video-model-veo`、`video-model-seedance` 三个 in-progress 模型适配 Package；模型专用 Prompt 方法与动态 capability 核验从稳定核心隔离。
- 增加稳定 `video-design` Skill，专门负责角色与场景视觉设计；恢复人物、衣物角色、普通衣物、道具、场景五套严格 1:1、2×2 四视图生图模板，并由 `video-materials` 按需使用。
