# Akira Video 视频返回审片与连续性独立黑盒验收

你正在执行 Akira Video 的**视频候选返回 → 审片 → 当前采用 → 实际出口 → 下一镜生成包**独立黑盒验收。

这是验收任务，不是实现任务。Skill source 与 fixture source 全部只读。

## 1. 固定点

- Video repository：`<VIDEO_REPO>`
- 预期 HEAD：`<EXPECTED_HEAD>`
- fixture：`<FIXTURE_ROOT>`

仓内 fixture：`tests/blackbox/fixtures/video-review-001`

HEAD 不匹配时判 `inconclusive — fixed point mismatch`。

## 2. 输出隔离

把 `source/project/` 复制到 `output/project/`。

把 `source/returned/` 中两个视频候选复制到：

`output/project/.tmp/return-inbox/`

之后所有修改只在 `output/`。

报告写 `output/report/`。

## 3. Phase A — 恢复当前等待状态

读取 `output/project/VIDEO.md` 与 SC01_SH010 的 `SHOT.md`。

确认：

- CHR01 / LOC01 长期参考已经正式存在；
- SH010 已经有正式 Prompt；
- 当前正在等用户返回 SH010 视频候选；
- SH010 尚无当前采用结果；
- SH020 依赖 SH010 实际出口，因此当前不能视为已可执行。

不得从头重做角色 / 场景 / Prompt。

## 4. Phase B — 实际检查两个视频候选

必须基于实际 MP4 内容检查，而不是文件名 / 顺序。

至少覆盖：

- 开始状态；
- 主要动作过程；
- 结束状态；
- 帧间稳定性。

本 fixture 的 SH010 目标：

- 同一人物形态保持稳定；
- 角色从左侧向桌边移动；
- 最终停在桌边；
- 右手持有黄色钥匙；
- 摄影机固定；
- 不出现无原因颜色 / 身份漂移；
- 钥匙不能中途消失。

如果当前执行器无法实际检查视频时间维度，该阶段必须记 `inconclusive`，不能根据 Prompt 或文件名推断。

## 5. Phase C — 候选选择

使用 `video-review` 当前规则：

- 先淘汰硬错误；
- 时间稳定性属于正式审片维度；
- 画面“更漂亮”不能抵消身份 / 状态错误；
- 两个都不合格时允许全部拒绝。

fixture 中只有一个候选满足当前镜头硬要求。

记录选择依据到 `output/report/phase-c.md`。

## 6. Phase D — 正式归档

把选中结果归档到：

`video/shots/SC01_SH010/take01.mp4`

如果目标目录已有 take，则使用下一个未占用编号；本 fixture 初始没有 take。

要求：

- 不覆盖源返回文件；
- 未选候选不进入正式镜头目录；
- 不创建 `final.mp4`；
- 原始采用 take 不做后期覆盖。

## 7. Phase E — 更新 SHOT.md 当前采用

在 SH010 `SHOT.md` 记录：

- 当前采用 take；
- 对应 Prompt；
- 模型 / 使用入口：本 fixture 可记录为 `synthetic blackbox return`；
- 结论；
- 实际出口；
- 可接受偏差（如果有）；
- 后期修复（如果有）。

实际出口必须来自被采用视频的真实结束画面。

本 fixture 下一镜真正依赖：

- CHR01 已到桌边；
- CHR01 右手持黄色钥匙；
- 角色保持同一绿色外套身份；
- 摄影机未改变空间轴。

不得把原计划出口直接复制成实际出口而不看视频。

## 8. Phase F — 展开 SH020

现在才允许建立 / 更新 SH020 `SHOT.md`。

Continuity In 必须来自 SH010 当前采用结果的实际出口。

SH020 目标：

- 角色仍在桌边；
- 右手仍持黄色钥匙；
- 把钥匙放进绿色外套内侧口袋；
- 然后转身离桌。

如果 SH010 实际出口和计划有可接受偏差，SH020 适配实际出口。

如果 SH010 实际出口违反硬约束，则应该拒绝 SH010，而不是让 SH020 接错。

## 9. Phase G — SH020 一次性生成包

只为 SH020 创建新的项目内 `.tmp/` 视频生成包。

验证：

- 自包含；
- 参考 CHR01 / LOC01 长期素材；
- 必要时可以使用 SH010 当前采用视频 / 尾帧作为连续性参考，但要写清职责；
- Prompt 只描述 SH020 当前需要的动作 / 摄影；
- 返回文件名明确；
- 不复制所有失败候选；
- 不创建整片 edit 工程。

## 10. Phase H — 更新 VIDEO.md 等待状态

更新当前摘要：

- SH010 已审片并有当前采用；
- 当前工作是等待 SH020 外部生成；
- 当前 SH020 生成包路径；
- 返回后进入 `video-review`；
- 不保留已经解决的 SH010 等待 blocker。

`VIDEO.md` 不写完整候选比较日志。

## 11. Phase I — 临时文件生命周期

SH010 采用结果已经正式归档后：

- 旧 return-inbox 可以清理；
- 未选 SH010 候选不进入长期目录；
- SH010 正式原始 take 保留；
- 当前 SH020 pack 保留等待用户。

## 12. Phase J — 完整性

结束前确认：

- Skill source 未修改；
- fixture source 未修改；
- 所有新增 / 修改只在 output；
- 正式镜头目录里只有被采用的原始 take；
- 没有 `final.mp4`；
- 没有为了本阶段提前创建 `video/edit/`。

## 13. Decision

accepted：实际审片、选择、归档、当前采用、实际出口、SH020 连续性和下一批交接全部正确。

rejected：例如按文件名选、只看单帧、接受时间漂移、把计划出口当实际出口、失败候选进长期目录、覆盖原始 take、提前创建 edit 或 SH020 没继承实际出口。

inconclusive：只有无法实际检查视频、fixed point 不匹配或环境阻止合法输出时使用。

## 14. 报告格式

```markdown
# Decision

## Fixed points

## SH010 candidate review

## Current take

## Actual continuity out

## SH020 package

## Remaining wait

## Integrity

## Findings
```
