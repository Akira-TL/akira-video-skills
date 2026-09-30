# In progress

尚未稳定的模型适配和实验性视频能力放在这里。模型能力、参数、供应商差异和提示词编译规则只有在形成可维护边界后再进入 stable。

当前模型适配器：

- `video-model-runway`：当前重点适配 Runway Gen-4.5 Text to Video / Image to Video。
- `video-model-veo`：适配 Google Veo，并显式区分不同 Google surface / stable / preview 能力。
- `video-model-seedance`：当前重点适配 Seedance 2.5 多模态参考、时间线、编辑与延长工作流。

这些 Package 不进入 `akira-video` 的默认 dependency closure。只有项目明确使用对应模型时才按需安装；精确时长、分辨率、输入上限和 endpoint 等动态能力在实际使用时重新核验官方资料。
