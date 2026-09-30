from __future__ import annotations

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


class VideoRepositoryContractTests(unittest.TestCase):
    def test_stable_skill_packages_have_docs_and_metadata(self) -> None:
        expected = {
            "akira-video",
            "video-advertising",
            "video-audio",
            "video-design",
            "video-editing",
            "video-generation",
            "video-materials",
            "video-review",
            "video-script",
            "video-shot",
        }
        actual = {p.name for p in STABLE.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}
        self.assertEqual(actual, expected)

        for name in expected:
            package = STABLE / name
            self.assertTrue((package / "skiloom-package.toml").is_file(), name)
            self.assertTrue((package / "agents" / "openai.yaml").is_file(), name)
            self.assertTrue((DOCS / f"{name}.md").is_file(), name)

    def test_akira_video_default_closure_is_core_only(self) -> None:
        deps = dependencies(STABLE / "akira-video")
        expected = {
            "akira-tl/akira-video-skills/video-audio",
            "akira-tl/akira-video-skills/video-design",
            "akira-tl/akira-video-skills/video-editing",
            "akira-tl/akira-video-skills/video-generation",
            "akira-tl/akira-video-skills/video-materials",
            "akira-tl/akira-video-skills/video-review",
            "akira-tl/akira-video-skills/video-script",
            "akira-tl/akira-video-skills/video-shot",
        }
        self.assertEqual(deps, expected)
        self.assertNotIn("akira-tl/akira-video-skills/video-advertising", deps)
        self.assertFalse(any("video-model-" in dep for dep in deps))

    def test_materials_depend_on_design(self) -> None:
        self.assertEqual(
            dependencies(STABLE / "video-materials"),
            {"akira-tl/akira-video-skills/video-design"},
        )

    def test_model_adapters_are_optional_and_have_required_core_dependencies(self) -> None:
        runway = dependencies(IN_PROGRESS / "video-model-runway")
        veo = dependencies(IN_PROGRESS / "video-model-veo")
        seedance = dependencies(IN_PROGRESS / "video-model-seedance")

        self.assertEqual(runway, {"akira-tl/akira-video-skills/video-generation"})
        self.assertEqual(
            veo,
            {
                "akira-tl/akira-video-skills/video-audio",
                "akira-tl/akira-video-skills/video-generation",
            },
        )
        self.assertEqual(
            seedance,
            {
                "akira-tl/akira-video-skills/video-audio",
                "akira-tl/akira-video-skills/video-generation",
            },
        )

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
        text = read(STABLE / "video-materials" / "references" / "FOUR-VIEW-PROMPTS.md")
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
        pack = read(STABLE / "video-generation" / "references" / "GENERATION-PACK.md")
        self.assertIn("当前项目 ForgeRelay 工作区内的 `.tmp/`", pack)
        self.assertIn("returns/", pack)
        self.assertIn("_take01.png", pack)

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
        layout = read(STABLE / "akira-video" / "references" / "project" / "PROJECT-LAYOUT.md")
        self.assertNotIn("video/audio/", layout)
        self.assertNotIn("video/delivery/", layout)
        self.assertIn("└── edit/", layout)
        self.assertIn("video/shots/", layout)
        self.assertIn("目标项目自己的 `.gitignore`", layout)
        self.assertIn(".tmp/", layout)

    def test_naming_preserves_scene_location_and_take_semantics(self) -> None:
        naming = read(STABLE / "akira-video" / "references" / "project" / "NAMING.md")
        self.assertIn("场次与地点不同", naming)
        self.assertIn("道具与产品不同", naming)
        self.assertIn("生成结果编号在同一个镜头内单调递增", naming)
        self.assertIn("start-frame.png", naming)
        self.assertIn("这些图片只有在多个镜头确实复用时才升级到 `video/materials/`", naming)

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
        templates = read(STABLE / "video-generation" / "references" / "PACK-TEMPLATES.md")
        for marker in (
            "包内所有上传素材都复制到当前包的 `materials/`",
            "任务文件只引用包内相对路径",
            "不使用软链接作为交付素材",
            "先修改正式归属文件",
            "不只在旧 `.tmp/` 包里临时改字",
        ):
            self.assertIn(marker, templates)

    def test_project_scaling_is_opt_in_and_git_remains_version_authority(self) -> None:
        scaling = read(STABLE / "akira-video" / "references" / "project" / "SCALING-VERSIONS.md")
        for marker in (
            "默认不创建章节层级",
            "只有出现以下情况之一时才增加组织层",
            "上游小说章节不等于视频章节",
            "普通修改使用 Git",
            "只有确实需要并行比较两套创意内容时",
        ):
            self.assertIn(marker, scaling)

    def test_previs_and_editing_rhythm_remain_need_driven(self) -> None:
        previs = read(STABLE / "video-shot" / "references" / "PREVIS.md")
        editing = read(STABLE / "video-editing" / "references" / "EDITING-RHYTHM.md")
        self.assertIn("按需工具", previs)
        self.assertIn("不需要额外创建 storyboard 目录", previs)
        self.assertIn("不要用复杂转场掩盖", editing)
        self.assertIn("镜头不因为“看起来漂亮”就必须保留完整生成时长", editing)

    def test_production_flow_resumes_existing_work_and_stops_on_external_dependencies(self) -> None:
        flow = read(STABLE / "akira-video" / "references" / "workflow" / "PRODUCTION-FLOW.md")
        self.assertIn("已有项目先读取 `VIDEO.md` 和当前实际文件，从当前工作继续", flow)
        self.assertIn("不能假装已经生成", flow)
        self.assertIn("长期角色 / 场景参考没有通过审片前，不拿它继续批量生成视频", flow)
        self.assertIn("完整项目是依赖图，不是固定流水线", flow)

    def test_dialogue_timing_and_multiformat_rules_avoid_late_fixups(self) -> None:
        dialogue = read(STABLE / "video-script" / "references" / "DIALOGUE-TIMING.md")
        multiformat = read(STABLE / "video-shot" / "references" / "MULTI-FORMAT.md")
        naming = read(STABLE / "akira-video" / "references" / "project" / "NAMING.md")
        self.assertIn("不要只用固定“每分钟多少字”替代真实语速", dialogue)
        self.assertIn("字幕不是生成任务", dialogue)
        self.assertIn("优先生成一个主版本", multiformat)
        self.assertIn("不应该强行裁切", multiformat)
        self.assertIn("prompt_vertical_v01.md", naming)

    def test_reference_continuity_and_candidate_selection_prioritize_identity_over_aesthetics(self) -> None:
        continuity = read(STABLE / "video-materials" / "references" / "REFERENCE-CONTINUITY.md")
        selection = read(STABLE / "video-review" / "references" / "CANDIDATE-SELECTION.md")
        self.assertIn("已验收素材是后续基准参考", continuity)
        self.assertIn("不自动替换基准参考", continuity)
        self.assertIn("先淘汰硬错误", selection)
        self.assertIn("硬错误不能由“画面更漂亮”抵消", selection)
        self.assertIn("“最好的一条”也可以全部不合格", selection)

    def test_design_approval_and_technical_qc_keep_human_and_media_boundaries(self) -> None:
        approval = read(STABLE / "video-design" / "references" / "DESIGN-APPROVAL.md")
        technical = read(STABLE / "video-editing" / "references" / "TECHNICAL-QC.md")
        self.assertIn("应先让用户决定的高影响分叉", approval)
        self.assertIn("用户已经授权 Agent 自主决定", approval)
        self.assertIn("已确认设计不要反复重问", approval)
        self.assertIn("文件基本可用", technical)
        self.assertIn("每一个真正要交付的文件至少分别核对", technical)
        self.assertIn("不能检查就明确保留", technical)

    def test_design_outputs_keep_identity_separate_from_state(self) -> None:
        outputs = read(STABLE / "video-design" / "references" / "DESIGN-OUTPUTS.md")
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
        derivatives = read(STABLE / "video-shot" / "references" / "SHOT-DERIVATIVES.md")
        lifecycle = read(STABLE / "akira-video" / "references" / "project" / "MEDIA-LIFECYCLE.md")
        self.assertIn("这些属于后期派生，不新建 Shot ID", derivatives)
        self.assertIn("后期修复后的片段不要覆盖原 `takeNN.mp4`", derivatives)
        self.assertIn("文件不是当前采用结果", lifecycle)
        self.assertIn("文件不是用户唯一原始输入", lifecycle)
        self.assertIn("不要让 `.tmp/.../returns/` 里的文件成为项目唯一正式副本", lifecycle)

    def test_existing_media_is_reused_without_forcing_regeneration(self) -> None:
        importing = read(STABLE / "akira-video" / "references" / "project" / "IMPORT-MEDIA.md")
        self.assertIn("不要为了“流程完整”强制重新生成", importing)
        self.assertIn("`source.mp4`", importing)
        self.assertIn("不要把它误命名成 `take01.mp4`", importing)
        self.assertIn("不强制补不存在的中间件", importing)

    def test_continuity_handoff_distinguishes_parallel_and_dependent_shots(self) -> None:
        handoff = read(STABLE / "video-shot" / "references" / "CONTINUITY-HANDOFF.md")
        self.assertIn("无（可独立生成）", handoff)
        self.assertIn("必须等前一镜结果的镜头", handoff)
        self.assertIn("计划出口不是已发生事实", handoff)
        self.assertIn("优先继承实际出口", handoff)
        self.assertIn("不机械全部推倒重来", handoff)

    def test_direction_rules_preserve_screen_space_without_forbidding_intentional_axis_crossing(self) -> None:
        direction = read(STABLE / "video-shot" / "references" / "DIRECTION.md")
        self.assertIn("180° 轴线规则", direction)
        self.assertIn("这不是不可违反的硬规则", direction)
        self.assertIn("反打要从空间另一观察方向重新构图，不能简单把上一镜水平翻转", direction)
        self.assertIn("动作匹配", direction)

    def test_reference_roles_prevent_identity_and_structure_contamination(self) -> None:
        roles = read(STABLE / "video-materials" / "references" / "REFERENCE-ROLES.md")
        self.assertIn("动作参考视频", roles)
        self.assertIn("默认不负责：", roles)
        self.assertIn("不参考演员身份 / 服装 / 背景", roles)
        self.assertIn("如果两份参考对同一个职责给出不同答案", roles)
        self.assertIn("参考越多越稳", roles)

    def test_authority_chain_blocks_generated_errors_from_becoming_facts(self) -> None:
        authority = read(STABLE / "akira-video" / "references" / "workflow" / "AUTHORITY.md")
        self.assertIn("提示词不是新的事实源", authority)
        self.assertIn("一次性生成包只复制 / 编译当前任务所需内容", authority)
        self.assertIn("实际可见出口", authority)
        self.assertIn("不能自动升级为正式事实", authority)
        self.assertIn("在第一个真正错误的归属层修复", authority)

    def test_model_comparison_keeps_one_shot_identity(self) -> None:
        comparison = read(STABLE / "video-generation" / "references" / "MODEL-COMPARISON.md")
        self.assertIn("模型不是镜头版本", comparison)
        self.assertIn("不自动创建新的 Shot ID", comparison)
        self.assertIn("生成结果编号不按模型重置", comparison)
        self.assertIn("项目不会按模型复制一套镜头结构", comparison)
        self.assertIn("不让模型差异反写镜头", comparison)

    def test_coverage_is_need_driven_not_a_fixed_shot_package(self) -> None:
        coverage = read(STABLE / "video-shot" / "references" / "COVERAGE.md")
        self.assertIn("不要求按传统覆盖套路机械生成", coverage)
        self.assertIn("不要每个动作后机械加一个“惊讶脸”", coverage)
        self.assertIn("同一动作不要重复展示", coverage)
        self.assertIn("备用镜头必须有明确可能用途", coverage)

    def test_animatic_and_finishing_reduce_cost_without_hiding_hard_errors(self) -> None:
        previs = read(STABLE / "video-shot" / "references" / "PREVIS.md")
        finishing = read(STABLE / "video-editing" / "references" / "FINISHING.md")
        self.assertIn("动态分镜（Animatic）", previs)
        self.assertIn("如果只是一次性节奏验证，可以放 `.tmp/`", previs)
        self.assertIn("不应仅靠 finishing 掩盖", finishing)
        self.assertIn("原始 `takeNN.mp4` 不覆盖", finishing)
        self.assertIn("放大不是恢复真实不存在的结构细节", finishing)

    def test_video_home_is_project_definition_and_current_snapshot(self) -> None:
        home = read(STABLE / "akira-video" / "references" / "project" / "VIDEO-HOME.md")
        for heading in (
            "## 项目定义",
            "## 交付要求",
            "## 来源与限制",
            "## 当前进度",
            "## 当前工作",
            "## 阻塞项",
            "## 关键决定",
            "## 导航",
        ):
            self.assertIn(heading, home)


if __name__ == "__main__":
    unittest.main()
