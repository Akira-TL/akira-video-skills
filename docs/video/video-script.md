# video-script

`video-script` 把小说、章节、故事梗概、品牌 brief 或其他上游资料转换成当前视频自己的脚本层。小说 / 长文本改编会先固定改编范围，再把内心叙事和背景说明转换成可见动作、场次与必要对白，而不是把原文缩写成旁白。

它只维护 `video/script/`，按需创建 `SCRIPT.md`、`CHARACTERS.md`、`SCENES.md` 和 `SHOTS.md`；具体最小写法由 `references/SCRIPT-TEMPLATES.md` 给出，模板是职责边界而不是必建文件清单。这些文件记录视频改编、表演、场景与镜头选择，不重新拥有或完整复制小说、世界观、客户资料等上游内容。

有剧情时优先保证事件因果、人物选择和对白连续性；复杂剧情、人物和对白检查通过 Skill 自己的 `references/NARRATIVE.md` 按需展开。包含可见对白、长台词、多角色说话或同步口型时，再用 `references/DIALOGUE-TIMING.md` 检查自然语速、镜头时长和说话人关系。角色需要跨镜头保持声音身份时把详细音色与声音参考交给 `video-audio`。简单无剧情视频可以只维护镜头总览，不强制建立完整故事结构。存在严格总时长时用 `references/DURATION-BUDGET.md` 做段落 / 镜头粗预算，但不把模型默认生成时长当最终剪辑时长。
