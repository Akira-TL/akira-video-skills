# video-script

`video-script` 把小说、章节、故事梗概、品牌 brief 或其他上游资料转换成当前视频自己的脚本层。

它只维护 `video/script/`，按需创建 `SCRIPT.md`、`CHARACTERS.md`、`SCENES.md` 和 `SHOTS.md`。这些文件记录视频改编、表演、场景与镜头选择，不重新拥有或完整复制小说、世界观、客户资料等上游内容。

有剧情时优先保证事件因果、人物选择和对白连续性；复杂剧情、人物和对白检查通过 Skill 自己的 `references/NARRATIVE.md` 按需展开。简单无剧情视频可以只维护镜头总览，不强制建立完整故事结构。
