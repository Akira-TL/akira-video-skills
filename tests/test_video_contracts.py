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
        layout = read(STABLE / "akira-video" / "references" / "PROJECT-LAYOUT.md")
        self.assertNotIn("video/audio/", layout)
        self.assertNotIn("video/delivery/", layout)
        self.assertIn("└── edit/", layout)
        self.assertIn("video/shots/", layout)

    def test_video_home_is_project_definition_and_current_snapshot(self) -> None:
        home = read(STABLE / "akira-video" / "references" / "VIDEO-HOME.md")
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
