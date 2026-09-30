# video-audio

`video-audio` 管理角色跨镜头声音一致性和视频声音设计，但不建立独立 `audio/` 目录。

角色长期声音定义和声音参考放在 `video/materials/voices/`；某个镜头独有的对白、呼吸、音效等留在对应镜头；全片音乐、旁白和混音进入 `video/edit/`。

它重点固定角色基础音色、年龄感、音域、发音和节奏，同时允许情绪、混响和空间感随场景变化。对白文本、自然说完所需时长、可见口型和多说话人关系由 `video-script/references/DIALOGUE-TIMING.md` 规划，声音 Skill 不复制第二套对白规则。
