# Akira Video 返回结果与恢复独立黑盒验收

你正在执行 Akira Video 的**跨会话恢复 + 返回结果审片 + 下一批生成**独立黑盒验收。

这是验收任务，不是实现任务。不要修改 Skill 源码或 fixture tracked input。

## 1. 固定点

- Video repository：`<VIDEO_REPO>`
- 预期 HEAD：`<EXPECTED_HEAD>`
- fixture：`<FIXTURE_ROOT>`

仓内 fixture：`tests/blackbox/fixtures/video-resume-001`

HEAD 不匹配时判 `inconclusive — fixed point mismatch`，不要自行 reset / checkout。

## 2. 输出隔离

fixture `source/` 全部只读。

先把：

`<FIXTURE_ROOT>/source/project/`

复制为：

`<FIXTURE_ROOT>/output/project/`

再把：

`<FIXTURE_ROOT>/source/returned/`

中的用户返回候选复制到：

`<FIXTURE_ROOT>/output/project/.tmp/return-inbox/`

之后所有修改只发生在 `output/`。

验收报告写入 `output/report/`。

## 3. Phase A — 恢复而不是重建

先读取复制后的 `VIDEO.md`。

验证：

- 能识别项目已经完成脚本、角色设计、场景设计和图片 Prompt；
- 当前工作是等待 CHR01 / LOC01 四视图返回；
- 不重新创建另一套人物 / 场景设计；
- 不重新编号对象；
- 不为了新会话重复制作旧的图片生成包。

## 4. Phase B — 审查用户返回候选

`return-inbox/` 中有：

- 两个人物四视图候选；
- 两个场景四视图候选。

必须实际检查候选内容，而不是按文件顺序猜。

### 人物合格标准

- 2×2；
- 同一人物 / 服装；
- 右上是后脑；
- 下方两格全身；
- 下方两格无五官。

### 场景合格标准

- 2×2；
- 同一三维空间；
- 门 / 窗 / 桌相对关系一致；
- 反向观察不是镜像复制；
- 主光方向保持同一世界空间逻辑。

如果两个候选都不合格，应重新生成，不能为了必须选一个而接受最不差结果。

## 5. Phase C — 候选选择与正式归档

对合格候选：

- 只有选中结果进入长期稳定名；
- 人物归入 `video/materials/characters/CHR01_four-view.png`；
- 场景归入 `video/materials/scenes/LOC01_four-view.png`；
- 未选候选不进入长期 materials；
- 不创建 `final.png / final2.png`。

归档前保留 return-inbox 原始候选；归档确认后才允许清理临时返回。

## 6. Phase D — 更新项目状态

更新 `VIDEO.md`：

- 清除“等待人物 / 场景四视图”的已解决阻塞项；
- 当前工作改为准备第一个视频镜头；
- 不把候选比较过程写成完整日志；
- 不把所有失败候选列到首页。

长期参考本身成为后续基准，但不反向改写 CHR01 / LOC01 正式设计。

## 7. Phase E — 展开第一个镜头

根据已有 `SHOTS.md`：

- SC01_SH010 可独立生成；
- SC01_SH020 明确依赖 SC01_SH010 当前采用结果的实际出口。

因此：

- 可以建立 SC01_SH010 的 `SHOT.md`；
- 可以为 SH010 编译正式视频 Prompt；
- **不得**因为参考图已经齐全就提前把 SH020 当成可执行任务。

SH020 仍然必须等待 SH010 实际视频返回并审片。

## 8. Phase F — 视频一次性生成包

只打当前可执行的 SH010 视频包。

验证：

- 包只在项目 `.tmp/`；
- README 自包含；
- SH010 任务文件明确目标时长、提示词、参考素材职责、硬性约束与返回文件名；
- 只复制最小充分参考；
- 人物四视图负责人物身份 / 比例 / 服装；
- 场景四视图负责空间；
- 不要求用户回项目其他目录找素材；
- SH020 不出现在当前可执行任务列表。

## 9. Phase G — 新等待断点

更新 `VIDEO.md`：

- 当前等待 SH010 外部视频生成；
- 写明当前包路径；
- 写明预期返回 `SC01_SH010_take01.mp4` 或项目按现有编号实际分配的下一个未使用编号；
- 返回后先 `video-review`；
- SH020 阻塞原因是依赖 SH010 实际出口。

不得：

- 伪造 `take01.mp4`；
- 写假“当前采用”；
- 把计划出口当实际出口；
- 创建 SH020 视频包。

## 10. Phase H — 临时文件生命周期

人物 / 场景选中结果已正式归档后：

- 旧 `return-inbox` 可以清理；
- 不能删掉唯一长期参考；
- 当前 SH010 视频生成包继续保留，等待用户外部生成；
- `.tmp/` 不进入长期事实层。

## 11. Phase I — 完整性

结束时确认：

- Video Skills source 未修改；
- fixture `source/` 未修改；
- 所有产物只在 `output/`；
- 输出项目没有新增一级 `audio/` / `delivery/` / `assets/` / 数据库。

## 12. Decision

accepted：恢复、候选审片、稳定归档、状态更新、SH010 单镜头包和 SH020 串行阻塞全部正确。

rejected：例如按顺序猜候选、把失败候选长期归档、重做已确认设计、提前打 SH020、伪造视频结果、把计划出口写成实际出口、临时文件成为唯一长期副本。

inconclusive：只有 fixed point / 环境导致关键阶段不能合法完成时使用。

## 13. 报告格式

```markdown
# Decision

accepted / rejected / inconclusive

## Fixed points

## Resume state

## Candidate review

## Archived references

## Generated SH010 pack

## Remaining blocker

## Integrity

## Findings
```
