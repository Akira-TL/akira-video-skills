# video-audio

`video-audio` 负责角色声音身份、声音参考、对白声音要求、环境声、音效、音乐与整片声音关系，不建立独立项目级 `audio/` 根目录。

声音按复用范围归属：

- 跨视频角色声音定义 / 参考 → `video/shared/voices/`；
- 只属于当前 V、但跨多个 Shot 复用 → `Vxxx/materials/voices/`；
- 单个 Shot / Generation 的对白、呼吸、音效等 → 对应正式 Shot / G 输入；
- 最终全片音乐、旁白、混音与实际采用关系 → `Vxxx/edit/`。

角色声音需要跨镜头稳定时，明确基础音色、年龄感、音域、发音、节奏与允许的情绪变化。对白与旁白的正式文本仍由视频脚本拥有；声音 Skill 只负责声音身份和声音表演，不复制第二套文本。

需要 AI 生成声音或音乐时交给 `video-generation` 建立 G/I 和一次性交付包；返回 Take 由 `video-review` 检查。正式时间线采用的声音由 Editing / 音频记录固定，不在 Generation 维护第二份 selected 状态。
