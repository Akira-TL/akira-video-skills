from __future__ import annotations

import hashlib
import re
import tomllib
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
STABLE = REPO / "skills" / "video"
IN_PROGRESS = REPO / "skills" / "in-progress"
DOCS = REPO / "docs" / "video"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dependencies(package: Path) -> set[str]:
    data = tomllib.loads(read(package / "skiloom-package.toml"))
    return set(data.get("dependencies", {}))


def markdown_files() -> list[Path]:
    return [p for p in REPO.rglob("*.md") if ".git" not in p.parts]


def resolved_local_markdown_links() -> tuple[list[tuple[Path, str]], set[Path]]:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken: list[tuple[Path, str]] = []
    targets: set[Path] = set()
    for source in markdown_files():
        for raw_target in pattern.findall(read(source)):
            if "://" in raw_target or raw_target.startswith(("#", "mailto:")):
                continue
            target = raw_target.split("#", 1)[0]
            if not target:
                continue
            resolved = (source.parent / target).resolve()
            if resolved.exists():
                targets.add(resolved)
            else:
                broken.append((source, raw_target))
    return broken, targets


class VideoRepositoryContractTests(unittest.TestCase):
    def test_local_markdown_links_are_not_broken(self) -> None:
        broken, _ = resolved_local_markdown_links()
        self.assertEqual(
            broken,
            [],
            "\n".join(f"{source.relative_to(REPO)} -> {target}" for source, target in broken),
        )

    def test_all_reference_markdown_is_reachable(self) -> None:
        _, linked_targets = resolved_local_markdown_links()
        references = {
            p.resolve()
            for root in (STABLE, IN_PROGRESS)
            for p in root.glob("*/references/**/*.md")
        }
        unreachable = sorted(p.relative_to(REPO) for p in references - linked_targets)
        self.assertEqual(unreachable, [])

    def test_stable_skill_packages_have_docs_and_metadata(self) -> None:
        expected = {
            "akira-video",
            "video-advertising",
            "video-audio",
            "video-cinematography",
            "video-director",
            "video-editing",
            "video-generation",
            "video-init",
            "video-production",
            "video-review",
            "video-script",
            "video-storyboard",
            "video-visual-design",
        }
        actual = {p.name for p in STABLE.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}
        self.assertEqual(actual, expected)

        for name in expected:
            package = STABLE / name
            self.assertTrue((package / "skiloom-package.toml").is_file(), name)
            self.assertTrue((package / "agents" / "openai.yaml").is_file(), name)
            self.assertTrue((DOCS / f"{name}.md").is_file(), name)

    def test_router_is_thin_and_production_owns_core_closure(self) -> None:
        self.assertEqual(
            dependencies(STABLE / "akira-video"),
            {
                "akira-tl/akira-video-skills/video-init",
                "akira-tl/akira-video-skills/video-production",
            },
        )
        self.assertEqual(
            dependencies(STABLE / "video-production"),
            {
                "akira-tl/akira-video-skills/video-director",
                "akira-tl/akira-video-skills/video-script",
                "akira-tl/akira-video-skills/video-visual-design",
                "akira-tl/akira-video-skills/video-storyboard",
                "akira-tl/akira-video-skills/video-cinematography",
                "akira-tl/akira-video-skills/video-audio",
                "akira-tl/akira-video-skills/video-generation",
                "akira-tl/akira-video-skills/video-review",
                "akira-tl/akira-video-skills/video-editing",
            },
        )
        self.assertNotIn(
            "akira-tl/akira-video-skills/video-advertising",
            dependencies(STABLE / "video-production"),
        )

    def test_model_supplier_adapters_are_not_packages(self) -> None:
        package_names = {
            p.name for p in IN_PROGRESS.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
        }
        self.assertFalse(any(name.startswith("video-model-") for name in package_names))
        generation = read(STABLE / "video-generation" / "SKILL.md")
        self.assertIn("不安装供应商 Adapter Skill", generation)

    def test_only_primary_router_is_user_invoked(self) -> None:
        router_metadata = read(STABLE / "akira-video" / "agents" / "openai.yaml")
        self.assertIn("allow_implicit_invocation: false", router_metadata)

        for package in STABLE.iterdir():
            if not package.is_dir() or package.name == "akira-video":
                continue
            metadata = package / "agents" / "openai.yaml"
            if metadata.is_file():
                self.assertNotIn("allow_implicit_invocation: false", read(metadata), package.name)

    def test_strict_four_view_contract_is_preserved(self) -> None:
        text = read(STABLE / "video-visual-design" / "references" / "assets" / "FOUR-VIEW-PROMPTS.md")
        required = (
            "严格 2×2 四格等大排列",
            "人物 180° 后脑勺",
            "面部区域不画眼睛、眉毛、鼻子、嘴巴",
            "衣物为空心",
            "四格全部禁止五官",
            "关键背面或连接结构",
            "四格必须是同一个三维空间",
            "固定等效焦段",
            "镜像替代反面",
        )
        for marker in required:
            self.assertIn(marker, text)

    def test_generation_pack_stays_inside_project_tmp(self) -> None:
        pack = read(STABLE / "video-generation" / "references" / "planning" / "GENERATION-PACK.md")
        self.assertIn(".tmp/V001/G003_I02/", pack)
        self.assertIn("receive", pack)
        self.assertIn("Take → I", pack)

        roots = (STABLE, IN_PROGRESS, DOCS, REPO / "AGENTS.md", REPO / "CONTEXT.md", REPO / "README.md")
        offenders: list[str] = []
        for root in roots:
            paths = [root] if root.is_file() else root.rglob("*")
            for path in paths:
                if not path.is_file() or path.suffix not in {".md", ".toml", ".yaml"}:
                    continue
                if "/tmp/" in read(path):
                    offenders.append(str(path.relative_to(REPO)))
        self.assertEqual(offenders, [])

    def test_project_layout_has_no_top_level_audio_or_delivery_tree(self) -> None:
        layout = read(STABLE / "video-init" / "references" / "project" / "PROJECT-LAYOUT.md")
        self.assertNotIn("video/audio/", layout)
        self.assertNotIn("video/delivery/", layout)
        self.assertIn("video/", layout)
        self.assertIn("shared/", layout)
        self.assertIn("videos/", layout)
        self.assertIn("generations/", layout)
        self.assertIn(".tmp/", layout)

    def test_naming_preserves_scene_location_and_take_semantics(self) -> None:
        naming = read(STABLE / "video-init" / "references" / "project" / "NAMING.md")
        self.assertIn("`V001`", naming)
        self.assertIn("`G001`", naming)
        self.assertIn("`I01`", naming)
        self.assertIn("Take 在一个 G 内单调递增", naming)
        self.assertIn("`CHR01_ref_v01.png`", naming)

    def test_product_shot_contract_preserves_real_product_identity(self) -> None:
        product_shots = read(STABLE / "video-advertising" / "references" / "PRODUCT-SHOTS.md")
        for marker in (
            "优先使用官方产品图作为图生视频起点",
            "有限视差（2.5D）",
            "现实品牌产品默认保留现实工业身份",
            "不要求模型重新发明 Logo、接口、按钮或文字",
        ):
            self.assertIn(marker, product_shots)

    def test_generation_pack_is_self_contained_and_reproducible(self) -> None:
        templates = read(STABLE / "video-generation" / "references" / "planning" / "PACK-TEMPLATES.md")
        for marker in (
            "包内所有上传素材都复制到当前包的 `materials/`",
            "任务文件只引用包内相对路径",
            "不使用软链接作为交付素材",
            "先修改正式归属文件",
            "不只在旧 `.tmp/` 包里临时改字",
        ):
            self.assertIn(marker, templates)

    def test_project_scaling_is_opt_in_and_git_remains_version_authority(self) -> None:
        scaling = read(STABLE / "video-production" / "references" / "project" / "SCALING-VERSIONS.md")
        for marker in (
            "默认不创建章节层级",
            "只有出现以下情况之一时才增加组织层",
            "上游小说章节不等于视频章节",
            "普通修改使用 Git",
            "只有确实需要并行比较两套创意内容时",
        ):
            self.assertIn(marker, scaling)

    def test_previs_and_editing_rhythm_remain_need_driven(self) -> None:
        previs = read(STABLE / "video-storyboard" / "references" / "planning" / "PREVIS.md")
        editing = read(STABLE / "video-editing" / "references" / "EDITING-RHYTHM.md")
        self.assertIn("按需工具", previs)
        self.assertIn("不需要额外创建 storyboard 目录", previs)
        self.assertIn("不要用复杂转场掩盖", editing)
        self.assertIn("镜头不因为“看起来漂亮”就必须保留完整生成时长", editing)

    def test_production_flow_resumes_existing_work_and_stops_on_external_dependencies(self) -> None:
        flow = read(STABLE / "video-production" / "references" / "workflow" / "PRODUCTION-FLOW.md")
        self.assertIn("不是固定阶段表", flow)
        self.assertIn("不同 G 可以同时处于不同进度", flow)
        self.assertIn("缺参考 → 图片 G", flow)
        self.assertIn("只暂停依赖该结果的分支", flow)

    def test_dialogue_timing_and_multiformat_rules_avoid_late_fixups(self) -> None:
        dialogue = read(STABLE / "video-script" / "references" / "DIALOGUE-TIMING.md")
        multiformat = read(STABLE / "video-storyboard" / "references" / "planning" / "MULTI-FORMAT.md")
        naming = read(STABLE / "video-init" / "references" / "project" / "NAMING.md")
        self.assertIn("不要只用固定“每分钟多少字”替代真实语速", dialogue)
        self.assertIn("字幕不是生成任务", dialogue)
        self.assertIn("优先生成一个主版本", multiformat)
        self.assertIn("不应该强行裁切", multiformat)
        self.assertIn("`prompt_i01.md`", naming)

    def test_reference_continuity_and_candidate_selection_prioritize_identity_over_aesthetics(self) -> None:
        continuity = read(STABLE / "video-visual-design" / "references" / "assets" / "REFERENCE-CONTINUITY.md")
        selection = read(STABLE / "video-review" / "references" / "CANDIDATE-SELECTION.md")
        self.assertIn("已验收素材是后续基准参考", continuity)
        self.assertIn("不自动替换基准参考", continuity)
        self.assertIn("先淘汰硬错误", selection)
        self.assertIn("硬错误不能由“画面更漂亮”抵消", selection)
        self.assertIn("“最好的一条”也可以全部不合格", selection)

    def test_design_approval_and_technical_qc_keep_human_and_media_boundaries(self) -> None:
        approval = read(STABLE / "video-visual-design" / "references" / "foundation" / "DESIGN-APPROVAL.md")
        technical = read(STABLE / "video-editing" / "references" / "TECHNICAL-QC.md")
        self.assertIn("应先让用户决定的高影响分叉", approval)
        self.assertIn("用户已经授权 Agent 自主决定", approval)
        self.assertIn("已确认设计不要反复重问", approval)
        self.assertIn("文件基本可用", technical)
        self.assertIn("每一个真正要交付的文件至少分别核对", technical)
        self.assertIn("不能检查就明确保留", technical)

    def test_design_outputs_keep_identity_separate_from_state(self) -> None:
        outputs = read(STABLE / "video-visual-design" / "references" / "foundation" / "DESIGN-OUTPUTS.md")
        self.assertIn("服装不是新角色", outputs)
        self.assertIn("白天 / 夜晚不是新地点", outputs)
        self.assertIn("状态变化不改变角色 ID", outputs)
        self.assertIn("只属于一个镜头的姿势、动作路径或手势放在当前镜头 / 预演中", outputs)

    def test_sound_layers_and_graphics_keep_precision_in_post(self) -> None:
        sound = read(STABLE / "video-audio" / "references" / "SOUND-LAYERS.md")
        graphics = read(STABLE / "video-editing" / "references" / "GRAPHICS-TITLES.md")
        self.assertIn("不要因为模型“能生成声音”就把所有后期声音任务都塞进镜头提示词", sound)
        self.assertIn("精确文字默认后期完成", graphics)
        self.assertIn("使用官方文件", graphics)
        self.assertIn("不写死一个通用像素安全区", graphics)

    def test_review_failure_modes_drive_targeted_repairs(self) -> None:
        failures = read(STABLE / "video-review" / "references" / "FAILURE-MODES.md")
        repair = read(STABLE / "video-review" / "references" / "REPAIR-DECISIONS.md")
        self.assertIn("身份漂移", failures)
        self.assertIn("产品 / 道具结构错误", failures)
        self.assertIn("不要用后期掩盖硬错误", repair)
        self.assertIn("一次改一个主要变量", repair)
        self.assertIn("连续失败升级", repair)

    def test_shot_derivatives_and_media_cleanup_preserve_originals(self) -> None:
        derivatives = read(STABLE / "video-storyboard" / "references" / "continuity" / "SHOT-DERIVATIVES.md")
        lifecycle = read(STABLE / "video-production" / "references" / "project" / "MEDIA-LIFECYCLE.md")
        self.assertIn("这些属于后期派生，不新建 Shot ID", derivatives)
        self.assertIn("后期修复后的片段不要覆盖原 `takeNN.mp4`", derivatives)
        self.assertIn("文件不是当前采用结果", lifecycle)
        self.assertIn("文件不是用户唯一原始输入", lifecycle)
        self.assertIn("不要让 `.tmp/.../returns/` 里的文件成为项目唯一正式副本", lifecycle)

    def test_existing_media_is_reused_without_forcing_regeneration(self) -> None:
        importing = read(STABLE / "video-production" / "references" / "project" / "IMPORT-MEDIA.md")
        self.assertIn("不要为了“流程完整”强制重新生成", importing)
        self.assertIn("`source.mp4`", importing)
        self.assertIn("不要把它误命名成 `take01.mp4`", importing)
        self.assertIn("不强制补不存在的中间件", importing)

    def test_continuity_handoff_distinguishes_parallel_and_dependent_shots(self) -> None:
        handoff = read(STABLE / "video-storyboard" / "references" / "continuity" / "CONTINUITY-HANDOFF.md")
        self.assertIn("无（可独立生成）", handoff)
        self.assertIn("必须等前一镜结果的镜头", handoff)
        self.assertIn("计划出口不是已发生事实", handoff)
        self.assertIn("优先继承实际出口", handoff)
        self.assertIn("不机械全部推倒重来", handoff)
        self.assertIn("世界空间", handoff)
        self.assertIn("角色自身左右", handoff)
        self.assertIn("角色自身左右不能因为反打 / 镜像变成另一只手", handoff)
        self.assertIn("最小状态块", handoff)
        self.assertIn("状态词保持稳定", handoff)

    def test_direction_rules_preserve_screen_space_without_forbidding_intentional_axis_crossing(self) -> None:
        direction = read(STABLE / "video-cinematography" / "references" / "DIRECTION.md")
        self.assertIn("180° 轴线规则", direction)
        self.assertIn("这不是不可违反的硬规则", direction)
        self.assertIn("反打要从空间另一观察方向重新构图，不能简单把上一镜水平翻转", direction)
        self.assertIn("动作匹配", direction)

    def test_reference_roles_prevent_identity_and_structure_contamination(self) -> None:
        roles = read(STABLE / "video-visual-design" / "references" / "assets" / "REFERENCE-ROLES.md")
        self.assertIn("动作参考视频", roles)
        self.assertIn("默认不负责：", roles)
        self.assertIn("不参考演员身份 / 服装 / 背景", roles)
        self.assertIn("如果两份参考对同一个职责给出不同答案", roles)
        self.assertIn("参考越多越稳", roles)

    def test_authority_chain_blocks_generated_errors_from_becoming_facts(self) -> None:
        authority = read(STABLE / "video-production" / "references" / "workflow" / "AUTHORITY.md")
        self.assertIn("提示词不是新的事实源", authority)
        self.assertIn("一次性生成包只复制 / 编译当前任务所需内容", authority)
        self.assertIn("实际可见出口", authority)
        self.assertIn("不能自动升级为正式事实", authority)
        self.assertIn("在第一个真正错误的归属层修复", authority)

    def test_model_comparison_stays_inside_one_generation_goal(self) -> None:
        comparison = read(STABLE / "video-generation" / "references" / "prompting" / "MODEL-COMPARISON.md")
        self.assertIn("模型是执行方式，不是 Shot 或 Generation 身份", comparison)
        self.assertIn("同一个 Generation 目标", comparison)
        self.assertIn("Take 编号仍在同一 G 内连续递增", comparison)
        self.assertIn("不按供应商复制一套资产或镜头结构", comparison)
        self.assertIn("不能偷偷改变人物、产品、场景、剧情或 Shot 核心目的", comparison)

    def test_coverage_is_need_driven_not_a_fixed_shot_package(self) -> None:
        coverage = read(STABLE / "video-storyboard" / "references" / "planning" / "COVERAGE.md")
        self.assertIn("不要求按传统覆盖套路机械生成", coverage)
        self.assertIn("不要每个动作后机械加一个“惊讶脸”", coverage)
        self.assertIn("同一动作不要重复展示", coverage)
        self.assertIn("备用镜头必须有明确可能用途", coverage)

    def test_animatic_and_finishing_reduce_cost_without_hiding_hard_errors(self) -> None:
        previs = read(STABLE / "video-storyboard" / "references" / "planning" / "PREVIS.md")
        finishing = read(STABLE / "video-editing" / "references" / "FINISHING.md")
        self.assertIn("动态分镜（Animatic）", previs)
        self.assertIn("如果只是一次性节奏验证，可以放 `.tmp/`", previs)
        self.assertIn("不应仅靠 finishing 掩盖", finishing)
        self.assertIn("原始 `takeNN.mp4` 不覆盖", finishing)
        self.assertIn("放大不是恢复真实不存在的结构细节", finishing)
        self.assertIn("首帧 / 尾帧 / 关键帧不是新的创意来源", previs)
        self.assertIn("尾帧只是计划出口", previs)
        self.assertIn("关键帧数量越多不一定越稳定", previs)
        self.assertIn("关键帧图没有通过身份 / 结构 / 空间检查前", previs)

    def test_script_and_visual_design_keep_single_source_boundaries(self) -> None:
        script = read(STABLE / "video-script" / "SKILL.md")
        visual = read(STABLE / "video-visual-design" / "SKILL.md")
        self.assertIn("正文只维护一处", script)
        self.assertIn("不建立竞争的 `DIRECTOR.md` / `SCRIPT.md` 副本", script)
        self.assertIn("正式送去生成的唯一正文必须保存在对应 G / I", visual)
        self.assertIn("资产记录只引用该 Prompt 来源", visual)
        self.assertIn("外部导入图片可以直接成为资产", visual)

    def test_batching_validates_high_risk_samples_before_scaling(self) -> None:
        batching = read(STABLE / "video-generation" / "references" / "planning" / "BATCHING.md")
        self.assertIn("先做代表样本", batching)
        self.assertIn("没有固定批量大小", batching)
        self.assertIn("停止放量的信号", batching)
        self.assertIn("更换模型 / 参考基准后重新小样", batching)
        self.assertIn("不要把一个数字写成通用规则", batching)

    def test_project_recording_has_one_source_for_each_fact(self) -> None:
        recording = read(STABLE / "video-production" / "references" / "project" / "RECORDING.md")
        self.assertIn("正文和事实只维护一处", recording)
        self.assertIn("VIDEO.md 当前摘要", recording)
        self.assertIn("Generation 不维护 selected take", recording)
        self.assertIn("正式剪辑时间线建立前", recording)
        self.assertIn("Blocker 必须真实", recording)

    def test_external_generation_waiting_is_scoped_and_resumable(self) -> None:
        waiting = read(STABLE / "video-production" / "references" / "workflow" / "WAITING-RESUME.md")
        self.assertIn("只阻塞依赖它的分支", waiting)
        self.assertIn("不重复打同一 I", waiting)
        self.assertIn("部分 / 一批返回", waiting)
        self.assertIn("不能根据画面内容或上传顺序猜归属", waiting)
        self.assertIn("正式接收成功但清理失败", waiting)

    def test_cross_package_reference_paths_require_declared_dependencies(self) -> None:
        pattern = re.compile(r"(video-[a-z0-9-]+)/references/")
        failures: list[str] = []
        for package in sorted(path for path in STABLE.iterdir() if (path / "SKILL.md").is_file()):
            declared = dependencies(package)
            for source in package.rglob("*.md"):
                for target in pattern.findall(read(source)):
                    if target == package.name:
                        continue
                    coordinate = f"akira-tl/akira-video-skills/{target}"
                    if coordinate not in declared:
                        failures.append(
                            f"{source.relative_to(REPO)} -> {target} without required dependency"
                        )
        self.assertEqual(failures, [])

    def test_optional_cross_skill_collaboration_has_no_hidden_reference_dependencies(self) -> None:
        audio = read(STABLE / "video-audio" / "SKILL.md")
        editing = read(STABLE / "video-editing" / "SKILL.md") + read(STABLE / "video-editing" / "references" / "EDITING-RHYTHM.md")
        self.assertEqual(dependencies(STABLE / "video-audio"), set())
        self.assertEqual(dependencies(STABLE / "video-editing"), set())
        self.assertNotIn("video-script/references/", audio)
        self.assertNotIn("video-storyboard/references/", editing)
        self.assertNotIn("video-audio/references/", editing)

    def test_temporal_review_checks_frame_to_frame_ai_drift(self) -> None:
        failures = read(STABLE / "video-review" / "references" / "FAILURE-MODES.md")
        qa = read(STABLE / "video-review" / "references" / "TAKE-QA.md")
        self.assertIn("时间稳定性 / 纹理漂移", failures)
        self.assertIn("背景墙体、家具出现呼吸 / 融化", failures)
        self.assertIn("经过遮挡后重新出现时换形", failures)
        self.assertIn("帧间稳定性", qa)
        self.assertIn("最终判断必须基于完整播放", qa)

    def test_performance_and_interaction_rules_make_acting_and_contact_observable(self) -> None:
        performance = read(STABLE / "video-script" / "references" / "PERFORMANCE.md")
        interaction = read(STABLE / "video-storyboard" / "references" / "direction" / "INTERACTION.md")
        self.assertIn("不把情绪词当表演指令终点", performance)
        self.assertIn("情绪要有触发点", performance)
        self.assertIn("多人场景中，当前叙事重点只有一个时", performance)
        self.assertIn("先明确交互主体", interaction)
        self.assertIn("哪只手", interaction)
        self.assertIn("不要让同一角色同时", interaction)
        self.assertIn("遮挡前后需要特别检查", interaction)

    def test_execution_parameters_stay_out_of_long_term_shot_intent_by_default(self) -> None:
        params = read(STABLE / "video-generation" / "references" / "prompting" / "EXECUTION-PARAMETERS.md")
        self.assertIn("Shot 不拥有模型参数", params)
        self.assertIn("seed 不是身份系统", params)
        self.assertIn("I 保存真正影响执行的设置", params)
        self.assertIn("严格可复现项目", params)
        self.assertIn("这不是所有视频的默认负担", params)

    def test_finishing_distinguishes_source_resolution_from_delivery_resolution(self) -> None:
        finishing = read(STABLE / "video-editing" / "references" / "FINISHING.md")
        technical = read(STABLE / "video-editing" / "references" / "TECHNICAL-QC.md")
        self.assertIn("源素材规格", finishing)
        self.assertIn("不等于原生 4K 细节", finishing)
        self.assertIn("不通过非等比拉伸", finishing)
        self.assertIn("裁切后的有效分辨率是否足够", finishing)
        self.assertIn("没有非等比拉伸", technical)

    def test_camera_language_distinguishes_framing_lens_and_motion(self) -> None:
        camera = read(STABLE / "video-cinematography" / "references" / "CAMERA-LANGUAGE.md")
        self.assertIn("景别与焦段不是一回事", camera)
        self.assertIn("推近 / 拉远（Dolly In / Out）", camera)
        self.assertIn("变焦（Zoom）", camera)
        self.assertIn("锁定机位也是主动选择", camera)
        self.assertIn("产品结构优先于炫技摄影", camera)
        self.assertIn("一个镜头优先只有一个主要摄影运动", camera)

    def test_lighting_preserves_world_space_and_product_readability(self) -> None:
        lighting = read(STABLE / "video-visual-design" / "references" / "environment" / "LIGHTING.md")
        self.assertIn("主光方向是连续性状态", lighting)
        self.assertIn("世界空间中的窗户仍在东侧", lighting)
        self.assertIn("白天 / 夜晚状态", lighting)
        self.assertIn("金属 / 玻璃反射不伪造不存在的结构", lighting)
        self.assertIn("曝光与调色分开", lighting)
        self.assertIn("不能用调色真正修复", lighting)

    def test_music_design_separates_temp_score_from_final_delivery(self) -> None:
        music = read(STABLE / "video-audio" / "references" / "MUSIC.md")
        self.assertIn("先区分临时音乐与最终音乐", music)
        self.assertIn("不要为了卡节拍", music)
        self.assertIn("不默认要求分轨", music)
        self.assertIn("网上能播放不等于允许进入最终对外交付", music)
        self.assertIn("如果关掉音乐后剧情完全不成立", music)

    def test_voiceover_is_scripted_narration_not_an_exposition_patch(self) -> None:
        voiceover = read(STABLE / "video-audio" / "references" / "VOICEOVER.md")
        self.assertIn("旁白不是剧情补丁", voiceover)
        self.assertIn("小说原文旁白不能机械复制成视频旁白", voiceover)
        self.assertIn("临时旁白不能因为已经剪进工程就自动变成最终声音", voiceover)
        self.assertIn("旁白字幕从**最终确认的旁白文本 / 音频**生成", voiceover)
        self.assertIn("产品功能、参数和宣传表达仍受 `video-advertising` 的产品事实约束", voiceover)

    def test_localization_reuses_project_assets_without_changing_facts(self) -> None:
        localization = read(STABLE / "video-production" / "references" / "workflow" / "LOCALIZATION.md")
        naming = read(STABLE / "video-init" / "references" / "project" / "NAMING.md")
        self.assertIn("不为每种语言复制整套 `video/`", localization)
        self.assertIn("不允许为了“更顺”改变", localization)
        self.assertIn("明显正面口型", localization)
        self.assertIn("只有目标语言真的改变画面时", localization)
        self.assertIn("不要为了未来可能本地化提前给所有文件加语言后缀", naming)
        self.assertIn("master.en-US.mp4", naming)

    def test_subtitles_follow_final_audio_semantics_and_delivery_requirements(self) -> None:
        subtitles = read(STABLE / "video-editing" / "references" / "SUBTITLES.md")
        self.assertIn("字幕文本来自最终声音 / 最终脚本", subtitles)
        self.assertIn("断句按语义，不按固定字符数", subtitles)
        self.assertIn("无障碍字幕（CC）", subtitles)
        self.assertIn("不写死一个全局每秒字符数", subtitles)
        self.assertIn("自动转写可以作为初稿", subtitles)
        self.assertIn("目标语言句长变化时重新检查", subtitles)

    def test_generated_edit_and_extension_preserve_original_shot_media(self) -> None:
        edit_extend = read(STABLE / "video-generation" / "references" / "transform" / "EDIT-EXTEND.md")
        self.assertIn("先判断是否应该后期", edit_extend)
        self.assertIn("Generation 关系", edit_extend)
        self.assertIn("原始 Take 不覆盖", edit_extend)
        self.assertIn("新增尾段本身仍是一个可独立 Review 的 Take", edit_extend)
        self.assertIn("完整 Review", edit_extend)

    def test_readme_points_to_current_production_workflow_validation(self) -> None:
        readme = read(REPO / "README.md")
        self.assertIn("tests/test_production_workflow_cases.py", readme)
        self.assertNotIn("tests/blackbox/", readme)

    def test_stable_docs_do_not_publish_obsolete_top_level_video_paths(self) -> None:
        pattern = re.compile(r"video/(?:script|materials|shots|edit|generations|scenes)/")
        offenders: list[str] = []
        for root in (STABLE, DOCS):
            for path in root.rglob("*.md"):
                for line_number, line in enumerate(read(path).splitlines(), start=1):
                    if pattern.search(line):
                        offenders.append(f"{path.relative_to(REPO)}:{line_number}: {line.strip()}")
        self.assertEqual(offenders, [])

    def test_media_review_helper_is_only_an_aid_not_full_video_acceptance(self) -> None:
        review_skill = read(STABLE / "video-review" / "SKILL.md")
        helper = read(STABLE / "video-review" / "scripts" / "media_review.py")
        self.assertIn("scripts/media_review.py", review_skill)
        self.assertIn("只是辅助定位", review_skill)
        self.assertIn("不能替代完整播放、听音、口型或视觉语义检查", review_skill)
        self.assertIn("不能替代完整播放", helper)
        self.assertIn("split-2x2", helper)

    def test_delivery_qc_helper_uses_explicit_requirements_and_not_content_acceptance(self) -> None:
        editing_skill = read(STABLE / "video-editing" / "SKILL.md")
        technical = read(STABLE / "video-editing" / "references" / "TECHNICAL-QC.md")
        helper = read(STABLE / "video-editing" / "scripts" / "delivery_qc.py")
        self.assertIn("scripts/delivery_qc.py", editing_skill)
        self.assertIn("期望值必须来自当前视频交付要求", editing_skill)
        self.assertIn("脚本没有通用“标准成片”默认值", technical)
        self.assertIn("技术 QC 只确认媒体文件与显式交付参数", helper)
        self.assertIn("--video-codec", helper)
        self.assertIn("--audio-codec", helper)
        self.assertIn("--sample-rate", helper)
        self.assertIn("不能替代从头到尾观看成片", helper)

    def test_video_home_is_single_video_record_and_current_snapshot(self) -> None:
        home = read(STABLE / "video-production" / "references" / "project" / "VIDEO-HOME.md")
        for heading in (
            "## 建议内容",
            "## 长视频拆分",
            "## 当前摘要",
            "## 上游来源",
        ):
            self.assertIn(heading, home)
        self.assertIn("唯一主要制作稿", home)
        self.assertIn("当前状态摘要不重复最终采用关系", home)


if __name__ == "__main__":
    unittest.main()
