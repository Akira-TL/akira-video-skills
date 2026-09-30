from __future__ import annotations

import hashlib
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

    def test_copy_rejects_repository_and_temporary_internal_sources(self) -> None:
        self.run_cli("init", str(self.project), "internal-pack")
        (self.project / ".git").mkdir()
        (self.project / ".git" / "config").write_text("secret\n", encoding="utf-8")
        (self.project / ".tmp" / "derived.txt").write_text("derived\n", encoding="utf-8")

        for source in (".git/config", ".tmp/derived.txt"):
            error = self.run_cli(
                "copy",
                str(self.project),
                "internal-pack",
                source,
                expected=2,
            )
            self.assertIn("formal project file", str(error["error"]))

        absolute_tmp = self.project / ".tmp" / "derived.txt"
        error = self.run_cli(
            "copy",
            str(self.project),
            "internal-pack",
            str(absolute_tmp),
            expected=2,
        )
        self.assertIn("formal project file", str(error["error"]))

    def test_zip_refuses_pack_after_returns_arrive(self) -> None:
        self.run_cli("init", str(self.project), "video-pack")
        self.run_cli("returns", str(self.project), "video-pack")
        returned = self.project / ".tmp" / "video-pack" / "returns" / "SH010_take01.mp4"
        returned.write_bytes(b"synthetic-return")

        error = self.run_cli("zip", str(self.project), "video-pack", expected=2)
        self.assertFalse(error["ok"])
        self.assertIn("contains returned files", str(error["error"]))

    def test_archive_requires_review_preserves_source_and_refuses_tmp_destination(self) -> None:
        self.run_cli("init", str(self.project), "review-pack")
        self.run_cli("returns", str(self.project), "review-pack")
        returned = self.project / ".tmp" / "review-pack" / "returns" / "candidate.png"
        returned.write_bytes(b"reviewed-candidate")

        error = self.run_cli(
            "archive",
            str(self.project),
            "review-pack",
            "candidate.png",
            "--dest",
            "video/materials/characters/CHR01_identity.png",
            expected=2,
        )
        self.assertIn("--confirm-reviewed", str(error["error"]))

        error = self.run_cli(
            "archive",
            str(self.project),
            "review-pack",
            "candidate.png",
            "--dest",
            ".tmp/not-formal.png",
            "--confirm-reviewed",
            expected=2,
        )
        self.assertIn("must not remain under .tmp", str(error["error"]))

        error = self.run_cli(
            "archive",
            str(self.project),
            "review-pack",
            "candidate.png",
            "--dest",
            "exports/CHR01_identity.png",
            "--confirm-reviewed",
            expected=2,
        )
        self.assertIn("must archive under video/", str(error["error"]))

        result = self.run_cli(
            "archive",
            str(self.project),
            "review-pack",
            "candidate.png",
            "--dest",
            "video/materials/characters/CHR01_identity.png",
            "--confirm-reviewed",
        )
        archived = self.project / "video" / "materials" / "characters" / "CHR01_identity.png"
        self.assertTrue(archived.is_file())
        self.assertTrue(returned.is_file())
        self.assertTrue(result["source_preserved"])
        self.assertEqual(result["sha256"], hashlib.sha256(b"reviewed-candidate").hexdigest())

        error = self.run_cli(
            "archive",
            str(self.project),
            "review-pack",
            "candidate.png",
            "--dest",
            "video/materials/characters/CHR01_identity.png",
            "--confirm-reviewed",
            expected=2,
        )
        self.assertIn("refusing to overwrite", str(error["error"]))

    def test_next_take_is_monotonic_and_does_not_fill_gaps(self) -> None:
        shot = self.project / "video" / "shots" / "SC01_SH010"
        shot.mkdir(parents=True)
        (shot / "take01.mp4").write_bytes(b"one")
        (shot / "take03.mp4").write_bytes(b"three")
        (shot / "prompt_v01.md").write_text("prompt\n", encoding="utf-8")

        result = self.run_cli(
            "next-take",
            str(self.project),
            "video/shots/SC01_SH010",
        )
        self.assertEqual(result["number"], 4)
        self.assertEqual(result["filename"], "take04.mp4")
        self.assertEqual(result["relative_path"], "video/shots/SC01_SH010/take04.mp4")

    def test_next_take_rejects_non_shot_directories(self) -> None:
        error = self.run_cli(
            "next-take",
            str(self.project),
            "video/materials/characters",
            expected=2,
        )
        self.assertIn("must be under video/shots/", str(error["error"]))

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
