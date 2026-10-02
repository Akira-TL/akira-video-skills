# Video Skills

稳定 AI 视频制作 Skills 位于本目录。

## User-invoked

- `akira-video`：Primary Router；拥有项目入口、`VIDEO.md` 与专业 Skill 路由。

## Model-invoked

- `video-script`：视频脚本层。
- `video-visual-design`：角色、场景、世界、空间与机械视觉设计。
- `video-audio`：角色跨镜头声音一致性与声音设计。
- `video-visual-design`：跨镜头复用素材与严格四视图。
- `video-storyboard`：单镜头生产定义。
- `video-generation`：提示词、多 G/I 生成批次、tar.gz 与结果导回。
- `video-review`：生成结果审片与采用判断。
- `video-editing`：整片级后期。
- `video-advertising`：品牌与产品项目的可选领域能力。

具体模型能力在执行当前 G/I 时核验当前官方资料，不维护供应商 Adapter Package。`video-generation`、`video-review`、`video-editing` 各自提供窄用途 CLI，分别处理多 G/I 生成批次、媒体审片辅助和最终成片技术 QC；脚本不接管创作判断。不要为了目录对称建立空 Skill。
