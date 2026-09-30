# 视频模型适配器独立黑盒验收模板

你正在对 Akira Video 的一个**视频模型适配器 Skill**进行独立黑盒验收。

这是验收任务，不是实现任务。不要修改被测 Skill、共享依赖 Skill、fixture 已有 tracked input、仓库文档或测试。

## 1. 需要由发起者填写

- Video Skills repository：`<VIDEO_REPO>`
- 被测 adapter Package：`<ADAPTER_PACKAGE>`
- 预期 repository HEAD：`<EXPECTED_HEAD>`
- 固定 fixture：`<FIXTURE_ROOT>`

默认 fixture 结构参考本仓：

`tests/blackbox/fixtures/model-adapter-001`

## 2. 开始前固定完整性

记录并在最终报告中给出：

- Video repo HEAD；
- Video repo `git status --porcelain`；
- fixture 所在 repo HEAD（如果 fixture 与 Skill 同仓则注明同一 HEAD）；
- fixture tracked working tree 状态；
- 被测 adapter `SKILL.md`；
- adapter `skiloom-package.toml`；
- adapter 按自身指针实际加载的 references；
- adapter declared dependencies。

如果 repository HEAD 不等于 `<EXPECTED_HEAD>`，不要继续执行产品验收，判定：

`inconclusive — fixed point mismatch`

不要自行切换 / reset / checkout 到另一个提交。

## 3. 只读与输出边界

禁止修改：

- `<ADAPTER_PACKAGE>`；
- `video-generation` 等被测依赖 Skill；
- fixture 已有 tracked input；
- 任何仓库规范文件。

允许输出只写入：

`<FIXTURE_ROOT>/output/`

如果该目录不存在，可以创建；它应当是 ignored / 非 tracked 输出区。

不允许为了让测试通过：

- 修改 Skill；
- 修改 fixture 输入；
- 补造缺失官方能力；
- 改写镜头设计；
- 替换产品事实；
- 删除不方便的约束。

## 4. 验收来源规则

从被测 adapter 的实际 `SKILL.md` 开始，只按其真实指针和 declared dependency 加载必要内容。

必须使用它实际依赖的 `video-generation` 模型适配器契约与验收规则；不要从模型记忆自行重建另一套规则。

如果某一阶段依赖**当前模型能力**：

- 以当前官方资料为准；
- 区分实际使用入口；
- 区分精确 model / version；
- 区分 stable / preview；
- 不用历史 preview 或第三方博客覆盖当前官方契约。

如果当前环境不能访问必须核验的官方资料，该动态能力相关阶段可以记：

`inconclusive — current official capability could not be verified`

但不依赖外部网络的契约测试仍应继续。

## 5. Fixture 概要

fixture 提供两个镜头和一组素材。

### SH010 — 基础 Image to Video

目标：

- 已有 CHR01 身份图；
- 已有 LOC01 场景图；
- 镜头只要求角色从静止到向桌面伸右手；
- 摄影机固定；
- 无声音。

重点验证：

- 适配器不会重新设计人物 / 场景；
- Image to Video 重点编译运动；
- 不为简单镜头强行写超长模板。

### SH020 — 高风险 reference + 声音 / edit 条件

目标：

- 角色继续使用同一身份；
- 有产品官方参考；
- 有动作参考视频；
- 有一句对白；
- fixture 明确产品结构不能被动作参考覆盖。

重点验证：

- 每份 reference 职责清楚；
- 当前模式只有官方明确支持时才启用声音 / reference / edit；
- 未确认能力必须 fail-closed；
- 不为了适配模型改变产品事实或镜头目的。

## 6. Phase A — Package / dependency boundary

验证：

1. adapter Package 能被 Skiloom 静态验证；
2. declared dependency 与实际读取需求一致；
3. 不通过源码相对路径读取未声明 sibling Package；
4. 一次性生成包 / 命名 / 结果归档仍由 `video-generation` 拥有；
5. adapter 没有要求 Router 自身成为运行时 required dependency，除非 Package 明确声明。

记录 evidence。

## 7. Phase B — 精确入口 / 模型 / 模式

对 fixture SH010，向被测 adapter 提交任务：

> 按 fixture 的 `SHOT.md` 和已给参考，为当前用户实际指定的入口 / 模型编译执行提示词。

验证 adapter 是否：

- 明确供应商 / 产品；
- 明确实际使用入口；
- 明确精确模型 / 版本；
- 明确 stable / preview（适用时）；
- 明确任务模式；
- 信息不足时暴露缺口，不直接猜。

如果 adapter 直接只凭模型家族名套能力，本阶段 rejected。

## 8. Phase C — Image to Video 编译

使用 SH010。

验证：

- 输入图已经固定的身份 / 场景不被长篇重写；
- 重点描述动作、摄影和环境变化；
- 固定机位被表达为明确正向要求；
- 不加入 fixture 没有的剧情、对白、道具或产品；
- 最终输出能映射回统一 adapter output contract。

把 adapter 实际输出保存到：

`output/phase-c.md`

## 9. Phase D — 参考职责与冲突

使用 SH020。

fixture 包含：

- 人物身份图；
- 场景图；
- 产品官方参考；
- 动作参考视频。

验证 adapter 是否明确：

- 人物图负责身份；
- 场景图负责空间；
- 产品官方图负责产品结构；
- 动作参考只负责动作，不负责演员身份 / 服装 / 背景；
- 同一职责冲突时先解决，而不是把全部素材无说明交给模型。

把实际输出保存到：

`output/phase-d.md`

## 10. Phase E — 动态能力 fail-closed

选择被测 adapter 当前一个会变化的能力，例如：

- 同步声音；
- reference / ingredients；
- first + last frame；
- edit；
- extend；
- 输入数量；
- 时长 / 分辨率。

验证：

1. 当前任务依赖该能力时，adapter 会查看 / 要求查看当前官方资料；
2. 明确实际入口与精确模型；
3. 官方未确认时输出未确认，而不是自行启用；
4. 不把 MODEL-GUIDE 的历史快照当永久事实；
5. 第三方入口不自动继承官方 API 全部能力。

保存 evidence：

`output/phase-e.md`

## 11. Phase F — 声音边界

SH020 含一句 fixture 对白。

如果当前模式明确支持同步声音，验证：

- 对白文本保持 fixture 原文；
- 没有新增台词；
- 声音身份仍来源于视频声音定义，而不是 adapter 自造；
- 只编译当前镜头需要的声音。

如果当前模式不支持 / 未确认：

- 应明确交后期或单独声音生成；
- 不伪装模型会输出同步声音。

## 12. Phase G — 模型能力不匹配

构造一个当前模型未确认支持的要求，不修改 fixture，只作为验收输入，例如：

> 假设当前指定入口未确认支持该 reference 模式，但用户仍要求使用。

验证 adapter 是否：

- 明确能力缺口；
- 给出已确认可用的替代模式 / 换入口 / 换模型 / 回后期；
- 不静默删掉镜头要求；
- 不私自改镜头；
- 不伪造“应该支持”。

## 13. Phase H — 跨模型 / 跨入口隔离

如果被测 adapter 允许同一模型家族存在多个入口，验证：

- 官方 API 能力不会无条件套到第三方 UI；
- preview 能力不会套到 stable；
- 旧 model 的参数不会套到新 model；
- 同一 `SHOT.md` 切换模型仍保持同一镜头身份。

## 14. Phase I — 统一输出契约

对至少一个成功场景检查最终输出是否覆盖适用项：

- 供应商 / 产品；
- 使用入口；
- 精确模型 / 版本；
- stable / preview；
- 任务模式；
- 当前提示词；
- 输入素材与职责；
- 用户需确认设置；
- 当前明确不支持 / 未确认能力；
- 能力核验状态。

简单模式可以省略不适用项，但不能省略关键歧义。

## 15. Phase J — 不越权

检查所有阶段输出，不得出现 adapter 自行：

- 改剧情；
- 改人物外形；
- 改场景结构；
- 改产品事实；
- 改对白内容；
- 改镜头核心动作；
- 把模型限制偷偷变成作品设定。

如果模型做不到，应暴露风险 / 回上游，不得静默重写作品。

## 16. Phase K — 工作树完整性

结束前再次记录：

- Video repo HEAD；
- Video repo `git status --porcelain`；
- fixture tracked working tree；
- output 文件清单。

必须确认：

- Skill source 未修改；
- fixture tracked input 未修改；
- 只有 `output/` 新增验收产物。

## 17. Decision

只能给：

### accepted

所有**适用且可执行**的关键阶段通过；环境导致的不适用项不影响核心契约判断。

### rejected

存在真实产品 / Skill 行为失败，例如：

- 越权改镜头；
- 动态能力猜测；
- reference 职责冲突；
- adapter 输出契约缺失；
- 未声明隐藏依赖；
- stable / preview 混用；
- 不安全地把模型限制反写作品。

### inconclusive

只有当关键验收因环境无法合法完成时使用，例如：

- 固定 HEAD 不一致；
- 官方能力来源不可访问，且该能力是当前被测核心；
- fixture 路径 / 工作区宿主限制导致关键阶段无法执行；
- 当前执行环境无法加载被测 Skill / dependency。

环境问题不能判产品 rejected，也不能伪装 accepted。

## 18. 最终报告格式

```markdown
# Decision

accepted / rejected / inconclusive

## Fixed points

- repo HEAD:
- repo clean:
- fixture:
- adapter:
- dependency closure:

## Phase results

| Phase | Result | Evidence |
| --- | --- | --- |
| A | pass/fail/inconclusive | ... |
| B | ... | ... |

## Findings

### Critical
- ...

### Major
- ...

### Minor
- ...

## Integrity

- Skill source modified: no
- Fixture tracked input modified: no
- Output only under output/: yes/no

## Remaining uncertainty

- ...
```

如果 accepted，不要为了“显得完整”制造无关 minor finding。

如果 rejected，finding 必须指向可复现输入 / 输出和违反的契约，不写主观“感觉不够好”。
