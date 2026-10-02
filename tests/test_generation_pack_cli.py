from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "video" / "video-generation" / "scripts" / "generation_pack.py"


class GenerationBatchCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(dir=REPO / "tests")
        self.root = Path(self.tempdir.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.video_g1 = self.make_generation(
            "video/V001_short/generations/G001",
            "V001 shot generation\n",
        )
        self.video_g2 = self.make_generation(
            "video/V001_short/generations/G002",
            "V001 second shot generation\n",
        )
        self.reference = (
            self.project
            / "video"
            / "shared"
            / "characters"
            / "CHR01"
            / "G001"
            / "take01.png"
        )
        self.reference.parent.mkdir(parents=True)
        self.reference.write_bytes(b"character-reference")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def make_generation(self, relative: str, prompt: str) -> Path:
        generation = self.project / relative
        generation.mkdir(parents=True)
        (generation / "GENERATION.md").write_text(
            f"# {generation.name}\n\n## I01\nPrompt: prompt_i01.md\n",
            encoding="utf-8",
        )
        (generation / "prompt_i01.md").write_text(prompt, encoding="utf-8")
        return generation

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

    def add_task(
        self,
        batch: str,
        generation: str,
        *,
        reference: str | None = None,
    ) -> dict[str, object]:
        args = [
            "add",
            str(self.project),
            batch,
            generation,
            "--input",
            "I01",
        ]
        if reference:
            args += ["--reference", reference]
        return self.run_cli(*args)

    def test_build_one_batch_for_multiple_generations_as_tar_gz(self) -> None:
        init = self.run_cli("init", str(self.project), "B001")
        batch = self.project / "video" / "batches" / "B001"
        self.assertEqual(Path(str(init["batch"])), batch)
        self.assertTrue(batch.is_dir())
        self.assertFalse((self.project / ".tmp").exists())
        self.assertIn("video/batches/", (self.project / ".gitignore").read_text(encoding="utf-8"))

        first = self.add_task(
            "B001",
            "video/V001_short/generations/G001",
            reference="video/shared/characters/CHR01/G001/take01.png",
        )
        second = self.add_task(
            "B001",
            "video/V001_short/generations/G002",
            reference="video/shared/characters/CHR01/G001/take01.png",
        )
        self.assertNotEqual(first["task"], second["task"])

        built = self.run_cli("build", str(self.project), "B001")
        archive = Path(str(built["archive"]))
        self.assertEqual(archive, batch / "B001.tar.gz")
        self.assertTrue(archive.is_file())
        self.assertTrue(batch.is_dir())

        with tarfile.open(archive, "r:gz") as tf:
            names = sorted(tf.getnames())
        self.assertIn("B001/README.md", names)
        self.assertTrue(any(name.endswith("/prompt.md") for name in names))
        self.assertEqual(
            sum(name.endswith("references/take01.png") for name in names),
            1,
        )
        self.assertFalse(any("handoff" in name.lower() for name in names))
        self.assertFalse(any(name.endswith(".akira-batch.json") for name in names))

    def test_receive_imports_multiple_tasks_and_keeps_batch_and_archive(self) -> None:
        self.run_cli("init", str(self.project), "B002")
        first = self.add_task("B002", "video/V001_short/generations/G001")
        second = self.add_task("B002", "video/V001_short/generations/G002")
        built = self.run_cli("build", str(self.project), "B002")

        batch = self.project / "video" / "batches" / "B002"
        returns = batch / "returns"
        first_returns = returns / str(first["task"])
        second_returns = returns / str(second["task"])
        first_returns.mkdir(parents=True, exist_ok=True)
        second_returns.mkdir(parents=True, exist_ok=True)
        (first_returns / "candidate-a.mp4").write_bytes(b"first")
        (second_returns / "candidate-b.mp4").write_bytes(b"second")

        result = self.run_cli("receive", str(self.project), "B002")
        self.assertEqual(set(result["received_tasks"]), {first["task"], second["task"]})
        self.assertEqual((self.video_g1 / "take01.mp4").read_bytes(), b"first")
        self.assertEqual((self.video_g2 / "take01.mp4").read_bytes(), b"second")
        self.assertTrue(batch.is_dir())
        self.assertTrue(Path(str(built["archive"])).is_file())

        repeated = self.run_cli("receive", str(self.project), "B002")
        self.assertTrue(repeated["already_received"])
        self.assertFalse((self.video_g1 / "take02.mp4").exists())
        self.assertFalse((self.video_g2 / "take02.mp4").exists())

    def test_build_refuses_package_drift_after_build(self) -> None:
        self.run_cli("init", str(self.project), "B003")
        task = self.add_task("B003", "video/V001_short/generations/G001")
        self.run_cli("build", str(self.project), "B003")
        batch = self.project / "video" / "batches" / "B003"
        prompt = batch / "tasks" / str(task["task"]) / "prompt.md"
        prompt.write_text("changed after build\n", encoding="utf-8")
        returns = batch / "returns" / str(task["task"])
        returns.mkdir(parents=True, exist_ok=True)
        (returns / "candidate.mp4").write_bytes(b"candidate")

        error = self.run_cli("receive", str(self.project), "B003", expected=2)
        self.assertIn("batch inputs changed after build", str(error["error"]))

    def test_reference_must_be_formal_project_file(self) -> None:
        self.run_cli("init", str(self.project), "B004")
        outside = self.root / "outside.png"
        outside.write_bytes(b"outside")

        error = self.run_cli(
            "add",
            str(self.project),
            "B004",
            "video/V001_short/generations/G001",
            "--input",
            "I01",
            "--reference",
            str(outside),
            expected=2,
        )
        self.assertIn("escapes project root", str(error["error"]))

    def test_cli_does_not_expose_per_generation_zip_or_cleanup_flow(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            cwd=REPO,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("build", completed.stdout)
        self.assertIn("receive", completed.stdout)
        self.assertNotIn("zip", completed.stdout)
        self.assertNotIn("seal", completed.stdout)
        self.assertNotIn("cleanup", completed.stdout)

    def test_init_refuses_existing_batch(self) -> None:
        self.run_cli("init", str(self.project), "B005")
        error = self.run_cli(
            "init",
            str(self.project),
            "B005",
            expected=2,
        )
        self.assertIn("batch already exists", str(error["error"]))


if __name__ == "__main__":
    unittest.main()
