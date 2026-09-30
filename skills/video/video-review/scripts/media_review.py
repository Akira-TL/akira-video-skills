from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


class MediaReviewError(RuntimeError):
    pass


def _project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise MediaReviewError(f"project root does not exist: {root}")
    return root


def _safe_relative(raw: str, *, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise MediaReviewError(
            f"{label} must be a non-empty project-relative path without '..': {raw}"
        )
    return path


def _inside(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise MediaReviewError(f"{label} escapes project root: {path}") from exc
    return resolved


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _review_root(project: Path) -> Path:
    raw = project / ".tmp" / "review"
    resolved = _inside(raw, project, label="review root")
    if raw.exists() and raw.is_symlink():
        raise MediaReviewError(f"review root must not be a symlink: {raw}")
    return resolved


def _ensure_tmp_ignored(project: Path) -> bool:
    gitignore = project / ".gitignore"
    current = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    lines = current.splitlines()
    if ".tmp/" in lines:
        return False
    text = current
    if text and not text.endswith("\n"):
        text += "\n"
    text += ".tmp/\n"
    gitignore.write_text(text, encoding="utf-8")
    return True


def _media_path(project: Path, raw: str) -> tuple[Path, Path]:
    source_arg = Path(raw).expanduser()
    if source_arg.is_absolute():
        resolved = _inside(source_arg, project, label="media")
        rel = resolved.relative_to(project)
    else:
        rel = _safe_relative(raw, label="media")
        resolved = _inside(project / rel, project, label="media")
    git_root = project / ".git"
    if rel.parts[0] == ".git" or _is_within(resolved, git_root):
        raise MediaReviewError(f"media must not come from .git/: {rel}")
    if not resolved.is_file():
        raise MediaReviewError(f"media is not a regular file: {resolved}")
    return resolved, rel


def _require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise MediaReviewError(f"required executable is not available: {name}")
    return path


def _run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        raise MediaReviewError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr.strip()}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise MediaReviewError("command returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise MediaReviewError("command returned unexpected JSON shape")
    return payload


def _fraction_float(raw: str | None) -> float | None:
    if not raw or raw in {"0/0", "N/A"}:
        return None
    try:
        return float(Fraction(raw))
    except (ValueError, ZeroDivisionError):
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_media(project: Path, raw_media: str) -> dict[str, Any]:
    ffprobe = _require_tool("ffprobe")
    media, rel = _media_path(project, raw_media)
    payload = _run_json(
        [
            ffprobe,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(media),
        ]
    )
    format_data = payload.get("format") or {}
    streams = payload.get("streams") or []
    video_streams: list[dict[str, Any]] = []
    audio_streams: list[dict[str, Any]] = []

    for stream in streams:
        if not isinstance(stream, dict):
            continue
        codec_type = stream.get("codec_type")
        if codec_type == "video":
            video_streams.append(
                {
                    "index": stream.get("index"),
                    "codec": stream.get("codec_name"),
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "pix_fmt": stream.get("pix_fmt"),
                    "avg_fps": _fraction_float(stream.get("avg_frame_rate")),
                    "r_fps": _fraction_float(stream.get("r_frame_rate")),
                    "duration": _float_or_none(stream.get("duration")),
                    "nb_frames": _int_or_none(stream.get("nb_frames")),
                }
            )
        elif codec_type == "audio":
            audio_streams.append(
                {
                    "index": stream.get("index"),
                    "codec": stream.get("codec_name"),
                    "sample_rate": _int_or_none(stream.get("sample_rate")),
                    "channels": stream.get("channels"),
                    "channel_layout": stream.get("channel_layout"),
                    "duration": _float_or_none(stream.get("duration")),
                }
            )

    duration = _float_or_none(format_data.get("duration"))
    return {
        "ok": True,
        "action": "probe",
        "media": str(media),
        "relative_media": str(rel),
        "sha256": _sha256(media),
        "size": media.stat().st_size,
        "format": format_data.get("format_name"),
        "duration": duration,
        "video_streams": video_streams,
        "audio_streams": audio_streams,
        "review_note": (
            "元数据和抽样帧只用于辅助定位，不能替代完整播放；动作、时间稳定性、声音和口型仍必须按实际媒体验收。"
        ),
    }


def _float_or_none(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _review_name(raw: str) -> str:
    if not raw or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for ch in raw):
        raise MediaReviewError(
            "review name must contain only letters, numbers, '.', '_' or '-'"
        )
    if raw.startswith("."):
        raise MediaReviewError("review name must not start with '.'")
    return raw


def _sample_timestamps(duration: float, count: int) -> list[float]:
    if duration <= 0:
        raise MediaReviewError("media duration must be positive for sampling")
    if count < 2 or count > 24:
        raise MediaReviewError("sample count must be between 2 and 24")
    margin = min(0.1, duration / 10.0)
    last = max(duration - margin, 0.0)
    if count == 2:
        return [0.0, last]
    return [last * i / (count - 1) for i in range(count)]


def cmd_probe(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    return probe_media(project, args.media)


def cmd_sample(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    _ensure_tmp_ignored(project)
    ffmpeg = _require_tool("ffmpeg")
    probed = probe_media(project, args.media)
    if not probed["video_streams"]:
        raise MediaReviewError("media has no video stream to sample")
    duration = probed["duration"]
    if duration is None:
        durations = [
            stream.get("duration")
            for stream in probed["video_streams"]
            if stream.get("duration") is not None
        ]
        duration = max(durations) if durations else None
    if duration is None:
        raise MediaReviewError("could not determine media duration for sampling")

    name = _review_name(args.name)
    review_root = _review_root(project)
    output = review_root / name
    _inside(output, review_root, label="review output")
    if output.exists():
        if not args.replace:
            raise MediaReviewError(
                f"review sample directory already exists; use --replace only when intentional: {output}"
            )
        if output.is_symlink():
            raise MediaReviewError(f"refusing to replace symlink review directory: {output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)

    timestamps = _sample_timestamps(float(duration), args.count)
    frames: list[dict[str, Any]] = []
    for index, timestamp in enumerate(timestamps, start=1):
        filename = f"frame-{index:02d}-{timestamp:08.3f}s.png"
        target = output / filename
        completed = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(probed["media"]),
                "-ss",
                f"{timestamp:.6f}",
                "-frames:v",
                "1",
                "-vsync",
                "0",
                str(target),
            ],
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0 or not target.is_file():
            raise MediaReviewError(
                f"failed to sample frame at {timestamp:.3f}s: {completed.stderr.strip()}"
            )
        frames.append(
            {
                "timestamp": round(timestamp, 6),
                "file": str(target),
                "relative_file": str(target.relative_to(project)),
                "sha256": _sha256(target),
            }
        )

    manifest = {
        "media": probed["relative_media"],
        "media_sha256": probed["sha256"],
        "duration": duration,
        "count": len(frames),
        "frames": frames,
        "review_note": probed["review_note"],
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "action": "sample",
        "review": str(output),
        "relative_review": str(output.relative_to(project)),
        "manifest": str(manifest_path),
        "frames": frames,
        "review_note": probed["review_note"],
    }


def cmd_cleanup(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _review_name(args.name)
    review_root = _review_root(project)
    output = review_root / name
    _inside(output, review_root, label="review output")
    if not output.exists():
        raise MediaReviewError(f"review sample directory does not exist: {output}")
    if not args.confirm:
        raise MediaReviewError("cleanup requires --confirm")
    if output.is_symlink():
        raise MediaReviewError(f"refusing to delete symlink review directory: {output}")
    shutil.rmtree(output)
    return {
        "ok": True,
        "action": "cleanup",
        "review_removed": str(output),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe and sample project-local media for Akira Video review."
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="read ffprobe metadata and SHA-256")
    probe.add_argument("project")
    probe.add_argument("media")
    probe.set_defaults(func=cmd_probe)

    sample = sub.add_parser(
        "sample",
        help="extract evenly spaced review frames into project .tmp/review/<name>/",
    )
    sample.add_argument("project")
    sample.add_argument("media")
    sample.add_argument("name")
    sample.add_argument("--count", type=int, default=7)
    sample.add_argument("--replace", action="store_true")
    sample.set_defaults(func=cmd_sample)

    cleanup = sub.add_parser("cleanup", help="remove one project-local review sample directory")
    cleanup.add_argument("project")
    cleanup.add_argument("name")
    cleanup.add_argument("--confirm", action="store_true")
    cleanup.set_defaults(func=cmd_cleanup)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except MediaReviewError as exc:
        payload = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        for key, value in result.items():
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
