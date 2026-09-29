# Video Skill 调用边界

本仓稳定 Skill 位于 `skills/video/<name>/`。

- **User-invoked**：只由用户显式进入。canonical `SKILL.md` 保持标准 frontmatter；OpenAI 使用同目录 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false`。
- **Model-invoked**：模型和用户都可以调用。`description` 写清真实触发条件；OpenAI metadata 不禁止隐式调用。

`akira-video` 是顶层 user-invoked Primary Router。其他稳定专业 Skill 默认 model-invoked，由 Router 根据当前制作任务按需加载；用户也可以直接调用某个专业 Skill。

依赖通过 Skill 名称与能力契约表达。Router 可以概括其他 Skill 的职责，但在依赖其具体行为、输入、输出或门禁前必须加载 canonical Skill；缺失 required dependency 时报告能力缺口，不从 Router 摘要或模型记忆重建正文。
