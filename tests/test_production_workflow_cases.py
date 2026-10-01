from __future__ import annotations

import json
import shutil
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

    def prepare_pack(
        self,
        name: str,
        *,
        prompt_source: str,
        references: list[tuple[str, str]] = [],
        instructions_source: str | None = None,
    ) -> Path:
        self.run_cli("init", str(self.project), name)
        self.run_cli(
            "copy",
            str(self.project),
            name,
            prompt_source,
            "--dest",
            "prompt.md",
        )
        for source, destination in references:
            self.run_cli(
                "copy",
                str(self.project),
                name,
                source,
                "--dest",
                destination,
            )
        if instructions_source:
            self.run_cli(
                "copy",
                str(self.project),
                name,
                instructions_source,
                "--dest",
                "README.md",
            )
        self.run_cli("seal", str(self.project), name)
        result = self.run_cli("returns", str(self.project), name)
        return Path(str(result["returns"]))

    def make_video_generation(
        self,
        video_id: str,
        label: str,
        generation_id: str,
        prompt: str,
    ) -> Path:
        video = self.project / "video" / "videos" / f"{video_id}_{label}"
        generation = video / "generations" / generation_id
        generation.mkdir(parents=True)
        (video / "VIDEO.md").write_text(
            f"# {video_id}\n\n## Shot table\n\n- SH010 — planned\n",
            encoding="utf-8",
        )
        (generation / "GENERATION.md").write_text(
            f"# {generation_id}\n\nPurpose: test generation\n\n## I01\nPrompt: prompt_i01.md\n",
            encoding="utf-8",
        )
        (generation / "prompt_i01.md").write_text(prompt, encoding="utf-8")
        (generation / "instructions_i01.md").write_text(
            "# Generate\n\nUpload references in numeric order.\n",
            encoding="utf-8",
        )
        return generation

    def make_shared_generation(
        self,
        generation_id: str,
        prompt: str,
    ) -> Path:
        generation = self.project / "video" / "shared" / "generations" / generation_id
        generation.mkdir(parents=True)
        (generation / "GENERATION.md").write_text(
            f"# {generation_id}\n\nPurpose: shared asset generation\n\n## I01\nPrompt: prompt_i01.md\n",
            encoding="utf-8",
        )
        (generation / "prompt_i01.md").write_text(prompt, encoding="utf-8")
        (generation / "instructions_i01.md").write_text(
            "# Generate asset\n\nReturn every candidate.\n",
            encoding="utf-8",
        )
        return generation

    def test_case_one_short_video_reuses_reference_and_receives_direct_video(self) -> None:
        shared = self.project / "video" / "shared" / "characters"
        shared.mkdir(parents=True)
        (shared / "CHR01.md").write_text(
            "# CHR01\n\nCurrent reference: CHR01_ref_v01.png\n",
            encoding="utf-8",
        )
        (shared / "CHR01_ref_v01.png").write_bytes(b"stable-character-v01")

        generation = self.make_video_generation(
            "V001",
            "short",
            "G001",
            "Character enters the room and notices the key.\n",
        )
        returns = self.prepare_pack(
            "V001/G001_I01",
            prompt_source="video/videos/V001_short/generations/G001/prompt_i01.md",
            references=[
                (
                    "video/shared/characters/CHR01_ref_v01.png",
                    "references/01_character.png",
                )
            ],
            instructions_source="video/videos/V001_short/generations/G001/instructions_i01.md",
        )

        (returns / "platform-result.mp4").write_bytes(b"video-result")
        bundle = returns / "platform-result-with-audio"
        bundle.mkdir()
        (bundle / "video.mp4").write_bytes(b"video-bundle")
        (bundle / "audio.wav").write_bytes(b"audio-bundle")
        (bundle / "captions.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n", encoding="utf-8")

        result = self.run_cli("receive", str(self.project), "V001/G001_I01")
        self.assertFalse(result["cleanup_pending"])
        by_source = {item["source"]: item["take"] for item in result["takes"]}
        self.assertEqual(set(by_source), {"platform-result.mp4", "platform-result-with-audio"})
        plain_take = generation / by_source["platform-result.mp4"]
        bundle_take = generation / by_source["platform-result-with-audio"]
        self.assertEqual(plain_take.read_bytes(), b"video-result")
        self.assertEqual((bundle_take / "audio.wav").read_bytes(), b"audio-bundle")
        self.assertFalse((self.project / ".tmp" / "V001" / "G001_I01").exists())

        generation_text = (generation / "GENERATION.md").read_text(encoding="utf-8")
        self.assertIn(f"{plain_take.name} — I01", generation_text)
        self.assertIn(f"{bundle_take.name} — I01", generation_text)

        video_md = self.project / "video" / "videos" / "V001_short" / "VIDEO.md"
        video_md.write_text(
            video_md.read_text(encoding="utf-8")
            + "\n- SH010 candidate: V001/G001 take01.mp4 00:00–00:04\n",
            encoding="utf-8",
        )
        self.assertIn("V001/G001 take01.mp4", video_md.read_text(encoding="utf-8"))

        repeated = self.run_cli("receive", str(self.project), "V001/G001_I01")
        self.assertTrue(repeated["already_received"])
        self.assertFalse((generation / "take03.mp4").exists())

    def test_case_two_series_reuses_shared_reference_then_upgrades_without_rewriting_history(self) -> None:
        characters = self.project / "video" / "shared" / "characters"
        characters.mkdir(parents=True)
        character_record = characters / "CHR01.md"
        character_record.write_text("# CHR01\n\nCurrent reference: none\n", encoding="utf-8")

        shared_g1 = self.make_shared_generation("G001", "Create the first stable CHR01 reference.\n")
        returns = self.prepare_pack(
            "shared/G001_I01",
            prompt_source="video/shared/generations/G001/prompt_i01.md",
            instructions_source="video/shared/generations/G001/instructions_i01.md",
        )
        (returns / "candidate-a.png").write_bytes(b"candidate-a")
        (returns / "candidate-b.png").write_bytes(b"candidate-b")
        self.run_cli("receive", str(self.project), "shared/G001_I01")

        shutil.copy2(shared_g1 / "take02.png", characters / "CHR01_ref_v01.png")
        character_record.write_text(
            "# CHR01\n\n"
            "Versions:\n"
            "- v01: CHR01_ref_v01.png ← shared/G001 take02.png\n\n"
            "Current reference: v01\n",
            encoding="utf-8",
        )

        v1_g = self.make_video_generation("V001", "episode-one", "G001", "Episode one prompt.\n")
        v2_g = self.make_video_generation("V002", "episode-two", "G001", "Episode two prompt.\n")
        for generation in (v1_g, v2_g):
            with (generation / "GENERATION.md").open("a", encoding="utf-8") as handle:
                handle.write("\nReference: CHR01_ref_v01.png\n")

        shared_g2 = self.make_shared_generation("G002", "Create an upgraded CHR01 reference.\n")
        returns = self.prepare_pack(
            "shared/G002_I01",
            prompt_source="video/shared/generations/G002/prompt_i01.md",
            instructions_source="video/shared/generations/G002/instructions_i01.md",
        )
        (returns / "candidate-new.png").write_bytes(b"candidate-new")
        self.run_cli("receive", str(self.project), "shared/G002_I01")

        shutil.copy2(shared_g2 / "take01.png", characters / "CHR01_ref_v02.png")
        character_record.write_text(
            "# CHR01\n\n"
            "Versions:\n"
            "- v01: CHR01_ref_v01.png ← shared/G001 take02.png\n"
            "- v02: CHR01_ref_v02.png ← shared/G002 take01.png\n\n"
            "Current reference: v02\n",
            encoding="utf-8",
        )

        self.assertEqual((characters / "CHR01_ref_v01.png").read_bytes(), b"candidate-b")
        self.assertEqual((characters / "CHR01_ref_v02.png").read_bytes(), b"candidate-new")
        self.assertIn("Current reference: v02", character_record.read_text(encoding="utf-8"))
        self.assertIn("CHR01_ref_v01.png", (v1_g / "GENERATION.md").read_text(encoding="utf-8"))
        self.assertIn("CHR01_ref_v01.png", (v2_g / "GENERATION.md").read_text(encoding="utf-8"))
        self.assertNotIn("CHR01_ref_v02.png", (v1_g / "GENERATION.md").read_text(encoding="utf-8"))

    def test_case_three_rework_actual_input_split_returns_and_interrupted_receive_recover(self) -> None:
        generation = self.make_shared_generation("G003", "Original image prompt.\n")
        returns = self.prepare_pack(
            "shared/G003_I01",
            prompt_source="video/shared/generations/G003/prompt_i01.md",
            instructions_source="video/shared/generations/G003/instructions_i01.md",
        )

        actual_prompt = "User changed the image prompt before generation.\n"
        pack_prompt = self.project / ".tmp" / "shared" / "G003_I01" / "prompt.md"
        pack_prompt.write_text(actual_prompt, encoding="utf-8")
        (returns / "first.png").write_bytes(b"first")
        (returns / "second.png").write_bytes(b"second")

        rejected = self.run_cli(
            "receive",
            str(self.project),
            "shared/G003_I01",
            expected=2,
        )
        self.assertIn("pack inputs changed after handoff", str(rejected["error"]))
        self.assertTrue((self.project / ".tmp" / "shared" / "G003_I01").exists())
        self.assertFalse((generation / "take01.png").exists())

        (generation / "prompt_i02.md").write_text(actual_prompt, encoding="utf-8")
        with (generation / "GENERATION.md").open("a", encoding="utf-8") as handle:
            handle.write("\n## I02\nPrompt: prompt_i02.md\n")

        accepted = self.run_cli(
            "receive",
            str(self.project),
            "shared/G003_I01",
            "--input",
            "I02",
            "--actual-source",
            "prompt.md=video/shared/generations/G003/prompt_i02.md",
        )
        self.assertEqual([item["take"] for item in accepted["takes"]], ["take01.png", "take02.png"])
        self.assertFalse((self.project / ".tmp" / "shared" / "G003_I01").exists())

        returns = self.prepare_pack(
            "shared/G003_I02",
            prompt_source="video/shared/generations/G003/prompt_i02.md",
            instructions_source="video/shared/generations/G003/instructions_i01.md",
        )
        (returns / "third.png").write_bytes(b"third")

        generation_md = generation / "GENERATION.md"
        generation_backup = generation / "GENERATION.md.interrupted"
        generation_md.rename(generation_backup)
        interrupted = self.run_cli(
            "receive",
            str(self.project),
            "shared/G003_I02",
            expected=2,
        )
        self.assertIn("GENERATION.md is required", str(interrupted["error"]))
        self.assertTrue((generation / "take03.png").is_file())
        self.assertTrue((self.project / ".tmp" / "shared" / "G003_I02").exists())

        generation_backup.rename(generation_md)
        recovered = self.run_cli("receive", str(self.project), "shared/G003_I02")
        self.assertEqual([item["take"] for item in recovered["takes"]], ["take03.png"])
        self.assertFalse(recovered["cleanup_pending"])
        self.assertFalse((self.project / ".tmp" / "shared" / "G003_I02").exists())
        self.assertFalse((generation / "take04.png").exists())

        repeated = self.run_cli("receive", str(self.project), "shared/G003_I02")
        self.assertTrue(repeated["already_received"])
        self.assertFalse((generation / "take04.png").exists())


if __name__ == "__main__":
    unittest.main()
