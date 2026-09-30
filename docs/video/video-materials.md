# video-materials

`video-materials` 管理 `video/materials/` 中跨镜头复用的 Prompt、参考图、人物、场景、道具、产品和其他素材。人物或场景视觉尚未设计清楚时先进入 `video-design`，再生成长期参考素材。

目录按真实需要创建，不预生成空分类。长期 Prompt 可以与对应图片放在同一目录；身份与状态只在确实需要区分时拆开。镜头专属内容留在对应 Shot，不复制进公共素材区。

四视图不强制所有项目都建立；但一旦需要稳定人物、衣物、道具或场景，就使用 `references/FOUR-VIEW-PROMPTS.md` 中对应的严格 1:1、2×2 模板，不改成自由多视角。产品项目会额外区分官方素材与 AI 辅助参考；广告真实性由 `video-advertising` 负责。
