from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "video" / "video-editing" / "scripts" / "delivery_qc.py"
FIXTURE_VIDEO = (
    REPO
    / "tests"
    / "blackbox"
    / "fixtures"
    / "video-review-001"
    / "source"
    / "returned"
    / "SC01_SH010_candidate-a.mp4"
)


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"),
    "ffmpeg and ffprobe are required for delivery QC CLI tests",
)
class DeliveryQcCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(dir=REPO / "tests")
        self.root = Path(self.tempdir.name)
        self.project = self.root / "project"
        self.media = self.project / "video" / "edit" / "master.mp4"
        self.media.parent.mkdir(parents=True)
        shutil.copy2(FIXTURE_VIDEO, self.media)

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

    def test_verify_matches_explicit_delivery_requirements_and_fully_decodes(self) -> None:
        result = self.run_cli(
            "verify",
            str(self.project),
            "video/edit/master.mp4",
            "--width",
            "640",
            "--height",
            "360",
            "--aspect",
            "16:9",
            "--duration-min",
            "3.9",
            "--duration-max",
            "4.1",
            "--fps",
            "12",
            "--audio",
            "forbidden",
            "--require-square-pixels",
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["decode_ok"])
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["actual"]["width"], 640)
        self.assertEqual(result["actual"]["height"], 360)
        self.assertAlmostEqual(float(result["actual"]["duration"]), 4.0, places=3)
        self.assertAlmostEqual(float(result["actual"]["avg_fps"]), 12.0, places=3)
        self.assertEqual(result["actual"]["audio_stream_count"], 0)
        self.assertIn("不能替代从头到尾观看成片", str(result["review_note"]))

    def test_decimal_aspect_is_supported(self) -> None:
        result = self.run_cli(
            "verify",
            str(self.project),
            "video/edit/master.mp4",
            "--aspect",
            "1.7777778",
        )
        self.assertTrue(result["ok"])

    def test_requirement_mismatch_returns_verification_failure(self) -> None:
        result = self.run_cli(
            "verify",
            str(self.project),
            "video/edit/master.mp4",
            "--width",
            "1920",
            "--audio",
            "required",
            expected=1,
        )
        self.assertFalse(result["ok"])
        failures = "\n".join(str(item) for item in result["failures"])
        self.assertIn("width mismatch", failures)
        self.assertIn("audio stream required", failures)
        self.assertTrue(result["decode_ok"])

    def test_external_media_and_external_symlink_are_rejected(self) -> None:
        outside = self.root / "outside.mp4"
        shutil.copy2(FIXTURE_VIDEO, outside)

        error = self.run_cli(
            "verify",
            str(self.project),
            str(outside),
            expected=2,
        )
        self.assertIn("escapes project root", str(error["error"]))

        disguised = self.project / "video" / "edit" / "external.mp4"
        disguised.symlink_to(outside)
        error = self.run_cli(
            "verify",
            str(self.project),
            "video/edit/external.mp4",
            expected=2,
        )
        self.assertIn("escapes project root", str(error["error"]))

    def test_repository_internal_media_is_rejected(self) -> None:
        git_media = self.project / ".git" / "secret.mp4"
        git_media.parent.mkdir()
        shutil.copy2(FIXTURE_VIDEO, git_media)

        error = self.run_cli(
            "verify",
            str(self.project),
            ".git/secret.mp4",
            expected=2,
        )
        self.assertIn("must not come from .git", str(error["error"]))


if __name__ == "__main__":
    unittest.main()
