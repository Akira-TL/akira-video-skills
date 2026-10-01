---
name: video-script
description: 把小说、章节、故事梗概、品牌要求或其他上游内容转换和修订为当前 Vxxx 的正式剧情、动作、对白与旁白；短片直接维护 VIDEO.md，长片按需拆 scenes/SCxx.md，不建立重复脚本正文。
---

# Video Script

本 Skill 负责当前视频的**正式剧情正文**。上游小说、世界观、章节、客户资料等继续归原权威来源；视频只记录本次采用 / 改编范围和正式视频化内容。

## 1. 读取上游与当前制作稿

先读取 `Vxxx/VIDEO.md`、已经拆出的场景正文和用户指定上游来源。小说 / 长文本改编按 [`references/ADAPTATION.md`](references/ADAPTATION.md)。只提取当前视频真正需要的事实，不复制上游全文。

用户已明确的风格、结构、时长、广告顺序等要求即使带创意性质也属于已知条件，不能因为“不是 Script 职责”而丢失。

## 2. 正文只维护一处

短视频可以直接在 `VIDEO.md` 写剧情、动作、对白和场景顺序。内容变长影响阅读时再拆 `Vxxx/scenes/SCxx.md`；拆出后 `VIDEO.md` 只保留概要、顺序和链接，不重复维护同一句对白或动作。

Director 方法发现剧情 / 动作 / 对白需要调整时可以直接落实，但正式修改仍写回这份唯一正文，不建立竞争的 `DIRECTOR.md` / `SCRIPT.md` 副本。

## 3. 剧情与人物

完整剧情、人物弧光和因果按 [`references/NARRATIVE.md`](references/NARRATIVE.md)。需要把情绪变成可拍摄行为时按 [`references/PERFORMANCE.md`](references/PERFORMANCE.md)：情绪词不是最终表演指令，要转成身体、视线、动作和可见节拍。

## 4. 对白、旁白与时长

可见说话、长对白、多角色对话或口型按 [`references/DIALOGUE-TIMING.md`](references/DIALOGUE-TIMING.md)。旁白属于正式剧情文本，但不作为修补不清楚剧情的万能解释层。总时长有明确边界时按 [`references/DURATION-BUDGET.md`](references/DURATION-BUDGET.md) 做故事 / 场景级粗预算。

## 5. 交给 Storyboard

Script 决定“发生什么、说什么”；`video-storyboard` 决定如何切成 Shot。Script 可以提出关键镜头意图，但不维护另一份详细 Shot List；Visual Design / Cinematography 的具体设计也不复制进剧情正文。

## 完成标准

当前 V 的正式剧情、动作、对白和旁白在唯一正文中可追踪，并足以让 Director / Storyboard / Visual Design 等方法继续工作，同时没有复制上游原文。
