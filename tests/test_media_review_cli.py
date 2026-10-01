from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "video" / "video-review" / "scripts" / "media_review.py"
@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"),
    "ffmpeg and ffprobe are required for media review CLI tests",
)
class MediaReviewCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(dir=REPO / "tests")
        self.root = Path(self.tempdir.name)
        self.project = self.root / "project"
        self.media = (
            self.project
            / "video"
            / "videos"
            / "V001_test"
            / "generations"
            / "G001"
            / "take01.mp4"
        )
        self.media.parent.mkdir(parents=True)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=size=640x360:rate=24:duration=4",
                "-an",
                "-c:v",
                "mpeg4",
                "-q:v",
                "5",
                "-y",
                str(self.media),
            ],
            check=True,
        )
        self.image = (
            self.project
            / "video"
            / "shared"
            / "characters"
            / "CHR01_four-view.png"
        )
        self.image.parent.mkdir(parents=True)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "color=c=white:s=768x768:d=1",
                "-frames:v",
                "1",
                "-threads",
                "1",
                "-y",
                str(self.image),
            ],
            check=True,
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

    def test_probe_reports_real_media_metadata_and_hash(self) -> None:
        result = self.run_cli(
            "probe",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["relative_media"], "video/videos/V001_test/generations/G001/take01.mp4")
        self.assertEqual(
            result["sha256"],
            hashlib.sha256(self.media.read_bytes()).hexdigest(),
        )
        self.assertAlmostEqual(float(result["duration"]), 4.0, places=3)
        video_streams = result["video_streams"]
        self.assertEqual(len(video_streams), 1)
        self.assertEqual(video_streams[0]["width"], 640)
        self.assertEqual(video_streams[0]["height"], 360)
        self.assertEqual(result["audio_streams"], [])
        self.assertIn("不能替代完整播放", result["review_note"])

    def test_sample_writes_only_project_local_review_frames_and_manifest(self) -> None:
        result = self.run_cli(
            "sample",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
            "sh010-review",
            "--count",
            "5",
        )
        review = self.project / ".tmp" / "review" / "sh010-review"
        self.assertEqual(result["relative_review"], ".tmp/review/sh010-review")
        self.assertTrue(review.is_dir())
        self.assertIn(".tmp/", (self.project / ".gitignore").read_text(encoding="utf-8"))
        self.assertEqual(len(result["frames"]), 5)
        timestamps = [float(frame["timestamp"]) for frame in result["frames"]]
        self.assertAlmostEqual(timestamps[0], 0.0, places=6)
        self.assertGreaterEqual(timestamps[-1], 3.89)
        for frame in result["frames"]:
            path = Path(str(frame["file"]))
            self.assertTrue(path.is_file())
            self.assertEqual(path.suffix, ".png")
            self.assertTrue(path.resolve().is_relative_to(review.resolve()))

        manifest = json.loads((review / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["count"], 5)
        self.assertEqual(manifest["media"], "video/videos/V001_test/generations/G001/take01.mp4")
        self.assertIn("不能替代完整播放", manifest["review_note"])

        error = self.run_cli(
            "sample",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
            "sh010-review",
            "--count",
            "3",
            expected=2,
        )
        self.assertIn("--replace", str(error["error"]))

        replaced = self.run_cli(
            "sample",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
            "sh010-review",
            "--count",
            "3",
            "--replace",
        )
        self.assertEqual(len(replaced["frames"]), 3)

    def test_split_2x2_writes_equal_review_quadrants_without_claiming_content_pass(self) -> None:
        result = self.run_cli(
            "split-2x2",
            str(self.project),
            "video/shared/characters/CHR01_four-view.png",
            "chr01-grid",
        )
        review = self.project / ".tmp" / "review" / "chr01-grid"
        self.assertEqual(result["relative_review"], ".tmp/review/chr01-grid")
        self.assertEqual(len(result["quadrants"]), 4)
        self.assertIn("仍必须实际看图判断", str(result["review_note"]))
        expected_names = {
            "top-left.png",
            "top-right.png",
            "bottom-left.png",
            "bottom-right.png",
        }
        actual_names = {Path(str(item["file"])).name for item in result["quadrants"]}
        self.assertEqual(actual_names, expected_names)
        for item in result["quadrants"]:
            self.assertEqual(item["width"], 384)
            self.assertEqual(item["height"], 384)
            self.assertTrue(Path(str(item["file"])).is_file())

        manifest = json.loads((review / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["width"], 768)
        self.assertEqual(manifest["height"], 768)
        self.assertEqual(len(manifest["quadrants"]), 4)
        self.assertIn(".tmp/", (self.project / ".gitignore").read_text(encoding="utf-8"))

    def test_split_2x2_rejects_non_square_image(self) -> None:
        wide = self.project / "video" / "videos" / "V001_test" / "materials" / "wide.png"
        wide.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(self.media),
                "-frames:v",
                "1",
                str(wide),
            ],
            check=True,
        )
        error = self.run_cli(
            "split-2x2",
            str(self.project),
            "video/videos/V001_test/materials/wide.png",
            "wide-grid",
            expected=2,
        )
        self.assertIn("expects a 1:1 image", str(error["error"]))

    def test_cleanup_requires_confirmation(self) -> None:
        self.run_cli(
            "sample",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
            "cleanup-review",
            "--count",
            "2",
        )
        error = self.run_cli(
            "cleanup",
            str(self.project),
            "cleanup-review",
            expected=2,
        )
        self.assertIn("--confirm", str(error["error"]))

        result = self.run_cli(
            "cleanup",
            str(self.project),
            "cleanup-review",
            "--confirm",
        )
        self.assertTrue(result["ok"])
        self.assertFalse((self.project / ".tmp" / "review" / "cleanup-review").exists())

    def test_probe_rejects_external_and_repository_internal_media(self) -> None:
        outside = self.root / "outside.mp4"
        shutil.copy2(self.media, outside)
        error = self.run_cli(
            "probe",
            str(self.project),
            str(outside),
            expected=2,
        )
        self.assertIn("escapes project root", str(error["error"]))

        git_media = self.project / ".git" / "secret.mp4"
        git_media.parent.mkdir()
        shutil.copy2(self.media, git_media)
        error = self.run_cli(
            "probe",
            str(self.project),
            ".git/secret.mp4",
            expected=2,
        )
        self.assertIn("must not come from .git", str(error["error"]))

        disguised = self.project / "video" / "videos" / "V001_test" / "generations" / "G001" / "disguised.mp4"
        disguised.symlink_to(git_media)
        error = self.run_cli(
            "probe",
            str(self.project),
            "video/videos/V001_test/generations/G001/disguised.mp4",
            expected=2,
        )
        self.assertIn("must not come from .git", str(error["error"]))

    def test_sample_rejects_external_review_root_symlink(self) -> None:
        outside = self.root / "outside-review"
        outside.mkdir()
        tmp = self.project / ".tmp"
        tmp.mkdir()
        (tmp / "review").symlink_to(outside, target_is_directory=True)

        error = self.run_cli(
            "sample",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
            "unsafe-review",
            expected=2,
        )
        self.assertIn("review root", str(error["error"]))

    def test_review_name_and_sample_count_are_bounded(self) -> None:
        error = self.run_cli(
            "sample",
            str(self.project),
            "video/videos/V001_test/generations/G001/take01.mp4",
            "../escape",
            expected=2,
        )
        self.assertIn("review name", str(error["error"]))

        for count in ("1", "25"):
            error = self.run_cli(
                "sample",
                str(self.project),
                "video/videos/V001_test/generations/G001/take01.mp4",
                f"bad-count-{count}",
                "--count",
                count,
                expected=2,
            )
            self.assertIn("between 2 and 24", str(error["error"]))


if __name__ == "__main__":
    unittest.main()
