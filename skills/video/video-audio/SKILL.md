---
name: video-audio
description: 设计并维护 AI 视频中的角色声音身份、声音参考、对白声音要求、环境声、音效、音乐与整片声音关系；当声音需要跨视频/镜头复用或进入 Generation 与剪辑时使用。
---

# Video Audio

本 Skill 负责声音设计与声音一致性，不建立项目级独立 `audio/` 根目录。

## 1. 声音归属

- 跨视频复用的角色声音定义 / 参考 → `video/shared/voices/`；
- 只属于当前 V 但跨多个 Shot 复用 → `Vxxx/materials/voices/`；
- 单个 Shot / Generation 的临时对白、呼吸、音效等写入对应正式 Shot / G 输入；
- 最终全片音乐、旁白、混音与实际采用关系进入 `Vxxx/edit/`。

完整层次按 [`references/SOUND-LAYERS.md`](references/SOUND-LAYERS.md)，音乐按 [`references/MUSIC.md`](references/MUSIC.md)，旁白按 [`references/VOICEOVER.md`](references/VOICEOVER.md)。

## 2. 角色声音身份

跨镜头角色声音需要稳定时，定义年龄感、基础音域、音色、共鸣、默认语速 / 音量、节奏、发音与允许情绪变化。详细模板见 [`references/VOICE-DESIGN.md`](references/VOICE-DESIGN.md)。工具提供 speaker ID / voice reference 等机制时按当前官方能力使用，不写死供应商字段。

## 3. 文本与声音分工

对白 / 旁白正式文本属于当前视频剧情正文，由 `video-script` 方法维护；本 Skill 负责声音身份与声音表演。需要同步声音的视频模型时把必要文本和声音事件编译进对应 G/I，但不为了模型能力增加原本不存在的台词。

## 4. 外部生成与 Review

需要 AI 生成声音 / 音乐时交给 `video-generation` 建立 G/I 和自包含包；返回 Take 由 `video-review` 检查。被最终时间线采用的音频由 Editing / 音频正式记录固定，不在 Generation 重复维护 selected 状态。

## 完成标准

需要复用的声音身份稳定、声音层职责清楚，生成与最终剪辑采用关系各归其位。
