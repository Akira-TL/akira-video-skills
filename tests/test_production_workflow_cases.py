from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "video" / "video-generation" / "scripts" / "generation_pack.py"


class ProductionWorkflowCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(dir=REPO / "tests")
        self.root = Path(self.tempdir.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_cli(self, *args: str, expected: int = 0) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", *args],
            text=True,
            capture_output=True,
            cwd=REPO,
        )
        self.assertEqual(
            completed.returncode,
            expected,
            f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertTrue(completed.stdout.strip(), completed.stderr)
        return json.loads(completed.stdout)

    def make_generation(self, relative: str, prompt: str, *, input_id: str = "I01") -> Path:
        generation = self.project / relative
        generation.mkdir(parents=True, exist_ok=True)
        generation_md = generation / "GENERATION.md"
        if not generation_md.exists():
            generation_md.write_text(
                f"# {generation.name}\n\nPurpose: test generation\n",
                encoding="utf-8",
            )
        with generation_md.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## {input_id}\nPrompt: prompt_{input_id.lower()}.md\n")
        (generation / f"prompt_{input_id.lower()}.md").write_text(prompt, encoding="utf-8")
        return generation

    def create_batch(
        self,
        batch: str,
        tasks: list[tuple[str, str, list[str]]],
    ) -> dict[str, str]:
        self.run_cli("init", str(self.project), batch)
        keys: dict[str, str] = {}
        for generation, input_id, references in tasks:
            args = [
                "add",
                str(self.project),
                batch,
                generation,
                "--input",
                input_id,
            ]
            for reference in references:
                args += ["--reference", reference]
            result = self.run_cli(*args)
            keys[generation] = str(result["task"])
        self.run_cli("build", str(self.project), batch)
        return keys

    def test_case_one_short_video_uses_direct_v_root_and_shared_character_take(self) -> None:
        video = self.project / "video" / "V001_short"
        video.mkdir(parents=True)
        (video / "VIDEO.md").write_text(
            "# V001\n\n## Shot table\n\n- SH010 — planned\n",
            encoding="utf-8",
        )

        character = self.project / "video" / "shared" / "characters" / "CHR01"
        character.mkdir(parents=True)
        (character / "CHR01.md").write_text(
            "# CHR01\n\nCurrent reference: G001/take01.png\n",
            encoding="utf-8",
        )
        char_g = self.make_generation(
            "video/shared/characters/CHR01/G001",
            "Generate CHR01 identity reference.\n",
        )
        (char_g / "take01.png").write_bytes(b"stable-character")

        shot_g = self.make_generation(
            "video/V001_short/generations/G001",
            "Character enters the room and notices the key.\n",
        )
        keys = self.create_batch(
            "B001",
            [
                (
                    "video/V001_short/generations/G001",
                    "I01",
                    ["video/shared/characters/CHR01/G001/take01.png"],
                )
            ],
        )
        task = keys["video/V001_short/generations/G001"]
        returns = self.project / "video" / "batches" / "B001" / "returns" / task
        (returns / "platform-result.mp4").write_bytes(b"video-result")

        result = self.run_cli("receive", str(self.project), "B001")
        self.assertEqual(result["received_tasks"], [task])
        self.assertEqual((shot_g / "take01.mp4").read_bytes(), b"video-result")
        self.assertTrue((self.project / "video" / "batches" / "B001" / "B001.tar.gz").is_file())
        self.assertFalse((self.project / "video" / "videos").exists())
        self.assertEqual((char_g / "take01.png").read_bytes(), b"stable-character")

    def test_case_two_shared_character_versions_reference_generation_takes_without_copying_media(self) -> None:
        character = self.project / "video" / "shared" / "characters" / "CHR01"
        character.mkdir(parents=True)
        character_record = character / "CHR01.md"

        g1 = self.make_generation(
            "video/shared/characters/CHR01/G001",
            "Create first stable CHR01 reference.\n",
        )
        keys = self.create_batch(
            "B002",
            [("video/shared/characters/CHR01/G001", "I01", [])],
        )
        returns = (
            self.project
            / "video"
            / "batches"
            / "B002"
            / "returns"
            / keys["video/shared/characters/CHR01/G001"]
        )
        (returns / "candidate-a.png").write_bytes(b"candidate-a")
        (returns / "candidate-b.png").write_bytes(b"candidate-b")
        self.run_cli("receive", str(self.project), "B002")

        character_record.write_text(
            "# CHR01\n\n"
            "Versions:\n"
            "- v01: G001/take02.png\n\n"
            "Current reference: v01\n",
            encoding="utf-8",
        )

        g2 = self.make_generation(
            "video/shared/characters/CHR01/G002",
            "Create upgraded CHR01 reference.\n",
        )
        keys = self.create_batch(
            "B003",
            [("video/shared/characters/CHR01/G002", "I01", [])],
        )
        returns = (
            self.project
            / "video"
            / "batches"
            / "B003"
            / "returns"
            / keys["video/shared/characters/CHR01/G002"]
        )
        (returns / "candidate-new.png").write_bytes(b"candidate-new")
        self.run_cli("receive", str(self.project), "B003")

        character_record.write_text(
            "# CHR01\n\n"
            "Versions:\n"
            "- v01: G001/take02.png\n"
            "- v02: G002/take01.png\n\n"
            "Current reference: v02\n",
            encoding="utf-8",
        )

        self.assertEqual((g1 / "take02.png").read_bytes(), b"candidate-b")
        self.assertEqual((g2 / "take01.png").read_bytes(), b"candidate-new")
        self.assertFalse(any(character.glob("CHR01_ref_v*.png")))
        text = character_record.read_text(encoding="utf-8")
        self.assertIn("G001/take02.png", text)
        self.assertIn("G002/take01.png", text)

    def test_case_three_new_input_uses_new_batch_and_take_numbers_continue(self) -> None:
        generation = self.make_generation(
            "video/V001_short/generations/G003",
            "Original image prompt.\n",
        )
        keys = self.create_batch(
            "B004",
            [("video/V001_short/generations/G003", "I01", [])],
        )
        returns = (
            self.project
            / "video"
            / "batches"
            / "B004"
            / "returns"
            / keys["video/V001_short/generations/G003"]
        )
        (returns / "first.png").write_bytes(b"first")
        self.run_cli("receive", str(self.project), "B004")

        self.make_generation(
            "video/V001_short/generations/G003",
            "Revised image prompt.\n",
            input_id="I02",
        )
        keys = self.create_batch(
            "B005",
            [("video/V001_short/generations/G003", "I02", [])],
        )
        returns = (
            self.project
            / "video"
            / "batches"
            / "B005"
            / "returns"
            / keys["video/V001_short/generations/G003"]
        )
        (returns / "second.png").write_bytes(b"second")
        self.run_cli("receive", str(self.project), "B005")

        self.assertEqual((generation / "take01.png").read_bytes(), b"first")
        self.assertEqual((generation / "take02.png").read_bytes(), b"second")
        self.assertTrue((self.project / "video" / "batches" / "B004" / "B004.tar.gz").is_file())
        self.assertTrue((self.project / "video" / "batches" / "B005" / "B005.tar.gz").is_file())


if __name__ == "__main__":
    unittest.main()
