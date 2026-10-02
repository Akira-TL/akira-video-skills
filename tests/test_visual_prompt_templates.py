from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
STABLE = REPO / "skills" / "video"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class VisualPromptTemplateTests(unittest.TestCase):
    def test_dedicated_character_environment_and_blocking_prompt_templates_exist(self) -> None:
        character = read(
            STABLE
            / "video-visual-design"
            / "references"
            / "character"
            / "CHARACTER-PROMPTS.md"
        )
        environment = read(
            STABLE
            / "video-visual-design"
            / "references"
            / "environment"
            / "ENVIRONMENT-PROMPTS.md"
        )
        blocking = read(
            STABLE
            / "video-storyboard"
            / "references"
            / "direction"
            / "BLOCKING-PROMPTS.md"
        )
        for marker in ("人物身份参考图", "全身角色参考", "严格四视图"):
            self.assertIn(marker, character)
        for marker in ("空场环境参考图", "空间结构", "严格四视图"):
            self.assertIn(marker, environment)
        for marker in ("场面调度（Blocking）", "世界空间", "角色站位", "摄影轴"):
            self.assertIn(marker, blocking)


if __name__ == "__main__":
    unittest.main()
