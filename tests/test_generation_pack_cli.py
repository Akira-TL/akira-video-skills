from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "video" / "video-generation" / "scripts" / "generation_pack.py"


class GenerationPackCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(dir=REPO / "tests")
        self.root = Path(self.tempdir.name)
        self.project = self.root / "project"
        (self.project / "video" / "materials" / "characters").mkdir(parents=True)
        (self.project / "video" / "materials" / "characters" / "CHR01_prompt.md").write_text(
            "# CHR01 prompt\n",
            encoding="utf-8",
        )

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

    def test_init_copy_status_and_zip(self) -> None:
        result = self.run_cli("init", str(self.project), "character-pack")
        self.assertTrue(result["ok"])
        self.assertIn(".tmp/", (self.project / ".gitignore").read_text(encoding="utf-8"))

        copy_result = self.run_cli(
            "copy",
            str(self.project),
            "character-pack",
            "video/materials/characters/CHR01_prompt.md",
            "--dest",
            "CHR01.md",
        )
        self.assertEqual(copy_result["relative_destination"], "CHR01.md")
        self.assertEqual(
            (self.project / ".tmp" / "character-pack" / "CHR01.md").read_text(encoding="utf-8"),
            "# CHR01 prompt\n",
        )

        (self.project / ".tmp" / "character-pack" / "README.md").write_text(
            "# Pack\n",
            encoding="utf-8",
        )
        status = self.run_cli("status", str(self.project), "character-pack")
        self.assertTrue(status["ok"])
        self.assertEqual(status["symlinks"], [])
        self.assertEqual(status["returns_files"], [])

        zipped = self.run_cli("zip", str(self.project), "character-pack")
        archive = Path(str(zipped["zip"]))
        self.assertTrue(archive.is_file())
        with zipfile.ZipFile(archive) as zf:
            self.assertEqual(sorted(zf.namelist()), ["CHR01.md", "README.md"])

    def test_copy_rejects_outside_project_and_external_symlink(self) -> None:
        self.run_cli("init", str(self.project), "safe-pack")
        outside = self.root / "outside-secret.txt"
        outside.write_text("secret\n", encoding="utf-8")

        error = self.run_cli(
            "copy",
            str(self.project),
            "safe-pack",
            str(outside),
            expected=2,
        )
        self.assertFalse(error["ok"])
        self.assertIn("escapes project root", str(error["error"]))

        link = self.project / "video" / "materials" / "characters" / "external.txt"
        link.symlink_to(outside)
        error = self.run_cli(
            "copy",
            str(self.project),
            "safe-pack",
            "video/materials/characters/external.txt",
            expected=2,
        )
        self.assertFalse(error["ok"])
        self.assertIn("escapes project root", str(error["error"]))

    def test_zip_refuses_pack_after_returns_arrive(self) -> None:
        self.run_cli("init", str(self.project), "video-pack")
        self.run_cli("returns", str(self.project), "video-pack")
        returned = self.project / ".tmp" / "video-pack" / "returns" / "SH010_take01.mp4"
        returned.write_bytes(b"synthetic-return")

        error = self.run_cli("zip", str(self.project), "video-pack", expected=2)
        self.assertFalse(error["ok"])
        self.assertIn("contains returned files", str(error["error"]))

    def test_cleanup_requires_explicit_confirmations(self) -> None:
        self.run_cli("init", str(self.project), "cleanup-pack")
        self.run_cli("returns", str(self.project), "cleanup-pack")
        returned = self.project / ".tmp" / "cleanup-pack" / "returns" / "result.png"
        returned.write_bytes(b"result")

        error = self.run_cli(
            "cleanup",
            str(self.project),
            "cleanup-pack",
            expected=2,
        )
        self.assertIn("--confirm-no-unique-info", str(error["error"]))

        error = self.run_cli(
            "cleanup",
            str(self.project),
            "cleanup-pack",
            "--confirm-no-unique-info",
            expected=2,
        )
        self.assertIn("--confirm-returns-archived", str(error["error"]))

        result = self.run_cli(
            "cleanup",
            str(self.project),
            "cleanup-pack",
            "--confirm-no-unique-info",
            "--confirm-returns-archived",
        )
        self.assertTrue(result["ok"])
        self.assertFalse((self.project / ".tmp" / "cleanup-pack").exists())

    def test_init_refuses_to_recreate_existing_pack(self) -> None:
        self.run_cli("init", str(self.project), "existing-pack")
        error = self.run_cli(
            "init",
            str(self.project),
            "existing-pack",
            expected=2,
        )
        self.assertIn("resume or inspect it instead of recreating", str(error["error"]))


if __name__ == "__main__":
    unittest.main()
