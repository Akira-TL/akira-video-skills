# video-design

`video-design` 负责真正的角色与场景视觉设计，而不是直接把“一个人”“一个厨房”写成生图 Prompt。

角色设计从剧情功能推导轮廓、比例、脸、发型、服装、材质、颜色、状态与跨镜头识别特征；场景设计从叙事功能推导空间骨架、材质、色彩、照明、视觉锚点和镜头可用性。

设计文件建议与对应复用素材共置，例如：

`video/materials/characters/CHR01_design.md`

`video/materials/scenes/LOC01_design.md`

设计确认后再由 `video-materials` 编写长期图片 Prompt，并在需要稳定身份或结构时使用严格四视图模板生成参考图。
