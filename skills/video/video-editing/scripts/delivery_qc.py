from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


class DeliveryQcError(RuntimeError):
    pass


def _project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise DeliveryQcError(f"project root does not exist: {root}")
    return root


def _safe_relative(raw: str, *, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise DeliveryQcError(
            f"{label} must be a non-empty project-relative path without '..': {raw}"
        )
    return path


def _inside(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise DeliveryQcError(f"{label} escapes project root: {path}") from exc
    return resolved


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _media_path(project: Path, raw: str) -> tuple[Path, Path]:
    source = Path(raw).expanduser()
    if source.is_absolute():
        resolved = _inside(source, project, label="media")
        rel = resolved.relative_to(project)
    else:
        rel = _safe_relative(raw, label="media")
        resolved = _inside(project / rel, project, label="media")
    if rel.parts[0] == ".git" or _is_within(resolved, project / ".git"):
        raise DeliveryQcError(f"media must not come from .git/: {rel}")
    if not resolved.is_file():
        raise DeliveryQcError(f"media is not a regular file: {resolved}")
    return resolved, rel


def _require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise DeliveryQcError(f"required executable is not available: {name}")
    return path


def _run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        raise DeliveryQcError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr.strip()}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise DeliveryQcError("command returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise DeliveryQcError("command returned unexpected JSON shape")
    return payload


def _float_or_none(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fraction(raw: str | None) -> Fraction | None:
    if not raw or raw in {"0/0", "0:0", "N/A"}:
        return None
    try:
        return Fraction(raw.replace(":", "/"))
    except (ValueError, ZeroDivisionError):
        return None


def _fraction_float(raw: str | None) -> float | None:
    value = _fraction(raw)
    return float(value) if value is not None else None


def _parse_aspect(raw: str) -> float:
    decimal = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*", raw)
    if decimal:
        value = float(decimal.group(1))
        if value <= 0:
            raise DeliveryQcError(f"aspect must be positive: {raw}")
        return value

    ratio = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*[:/]\s*(\d+(?:\.\d+)?)\s*", raw)
    if not ratio:
        raise DeliveryQcError(
            f"aspect must look like 16:9, 16/9, or 1.777, got: {raw}"
        )
    numerator = float(ratio.group(1))
    denominator = float(ratio.group(2))
    if numerator <= 0 or denominator <= 0:
        raise DeliveryQcError(f"aspect values must be positive: {raw}")
    return numerator / denominator


def _probe(project: Path, raw_media: str) -> dict[str, Any]:
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
    video_streams = [
        stream for stream in streams
        if isinstance(stream, dict) and stream.get("codec_type") == "video"
    ]
    audio_streams = [
        stream for stream in streams
        if isinstance(stream, dict) and stream.get("codec_type") == "audio"
    ]
    return {
        "media_path": media,
        "relative_media": rel,
        "format": format_data,
        "video_streams": video_streams,
        "audio_streams": audio_streams,
    }


def _decode_check(media: Path) -> tuple[bool, str]:
    ffmpeg = _require_tool("ffmpeg")
    completed = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(media),
            "-map",
            "0:v?",
            "-map",
            "0:a?",
            "-f",
            "null",
            "-",
        ],
        text=True,
        capture_output=True,
    )
    return completed.returncode == 0, completed.stderr.strip()


def cmd_verify(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    probed = _probe(project, args.media)
    video_streams = probed["video_streams"]
    audio_streams = probed["audio_streams"]
    failures: list[str] = []
    warnings: list[str] = []

    if not video_streams:
        failures.append("no video stream found")
        main_video: dict[str, Any] = {}
    else:
        main_video = video_streams[0]
        if len(video_streams) > 1:
            warnings.append(f"multiple video streams found: {len(video_streams)}; checks use the first stream")

    width = main_video.get("width")
    height = main_video.get("height")
    video_codec = main_video.get("codec_name")
    fps = _fraction_float(main_video.get("avg_frame_rate"))
    sample_aspect_raw = main_video.get("sample_aspect_ratio")
    sample_aspect = _fraction_float(sample_aspect_raw)
    display_aspect_raw = main_video.get("display_aspect_ratio")
    format_name_raw = probed["format"].get("format_name") or ""
    format_names = [item.strip() for item in str(format_name_raw).split(",") if item.strip()]
    main_audio = audio_streams[0] if audio_streams else {}
    audio_codec = main_audio.get("codec_name")
    audio_channels = main_audio.get("channels")
    audio_sample_rate = main_audio.get("sample_rate")
    try:
        audio_sample_rate = int(audio_sample_rate) if audio_sample_rate not in (None, "", "N/A") else None
    except (TypeError, ValueError):
        audio_sample_rate = None

    duration = _float_or_none(probed["format"].get("duration"))
    if duration is None:
        duration = _float_or_none(main_video.get("duration"))

    if args.width is not None and args.width <= 0:
        raise DeliveryQcError("expected width must be positive")
    if args.height is not None and args.height <= 0:
        raise DeliveryQcError("expected height must be positive")
    if args.duration_min is not None and args.duration_min < 0:
        raise DeliveryQcError("duration minimum must be >= 0")
    if args.duration_max is not None and args.duration_max < 0:
        raise DeliveryQcError("duration maximum must be >= 0")
    if (
        args.duration_min is not None
        and args.duration_max is not None
        and args.duration_min > args.duration_max
    ):
        raise DeliveryQcError("duration minimum must not exceed duration maximum")
    if args.fps is not None and args.fps <= 0:
        raise DeliveryQcError("expected fps must be positive")
    if args.channels is not None and args.channels <= 0:
        raise DeliveryQcError("expected channel count must be positive")
    if args.sample_rate is not None and args.sample_rate <= 0:
        raise DeliveryQcError("expected sample rate must be positive")

    if args.width is not None and width != args.width:
        failures.append(f"width mismatch: expected {args.width}, got {width}")
    if args.height is not None and height != args.height:
        failures.append(f"height mismatch: expected {args.height}, got {height}")

    if args.aspect is not None:
        expected_aspect = _parse_aspect(args.aspect)
        actual_aspect = None
        display_fraction = _fraction(display_aspect_raw)
        if display_fraction is not None:
            actual_aspect = float(display_fraction)
        elif isinstance(width, int) and isinstance(height, int) and height:
            sar = sample_aspect if sample_aspect not in (None, 0) else 1.0
            actual_aspect = (width * sar) / height
        if actual_aspect is None or not math.isclose(
            actual_aspect,
            expected_aspect,
            rel_tol=0.0,
            abs_tol=args.aspect_tolerance,
        ):
            failures.append(
                f"aspect mismatch: expected {args.aspect}, got "
                f"{display_aspect_raw or actual_aspect}"
            )

    if args.duration_min is not None:
        if duration is None or duration < args.duration_min:
            failures.append(
                f"duration below minimum: expected >= {args.duration_min}, got {duration}"
            )
    if args.duration_max is not None:
        if duration is None or duration > args.duration_max:
            failures.append(
                f"duration above maximum: expected <= {args.duration_max}, got {duration}"
            )

    if args.fps is not None:
        if fps is None or not math.isclose(
            fps,
            args.fps,
            rel_tol=0.0,
            abs_tol=args.fps_tolerance,
        ):
            failures.append(f"fps mismatch: expected {args.fps}, got {fps}")

    if args.container is not None:
        expected_container = args.container.lower()
        if expected_container not in {item.lower() for item in format_names}:
            failures.append(
                f"container mismatch: expected {args.container}, got {format_name_raw or None}"
            )

    if args.video_codec is not None and video_codec != args.video_codec:
        failures.append(
            f"video codec mismatch: expected {args.video_codec}, got {video_codec}"
        )

    if args.audio == "required" and not audio_streams:
        failures.append("audio stream required but none found")
    elif args.audio == "forbidden" and audio_streams:
        failures.append(f"audio stream forbidden but found {len(audio_streams)}")

    if args.audio_codec is not None and audio_codec != args.audio_codec:
        failures.append(
            f"audio codec mismatch: expected {args.audio_codec}, got {audio_codec}"
        )
    if args.channels is not None and audio_channels != args.channels:
        failures.append(
            f"audio channel mismatch: expected {args.channels}, got {audio_channels}"
        )
    if args.sample_rate is not None and audio_sample_rate != args.sample_rate:
        failures.append(
            f"audio sample rate mismatch: expected {args.sample_rate}, got {audio_sample_rate}"
        )

    if args.require_square_pixels:
        if sample_aspect_raw not in (None, "1:1", "1/1"):
            failures.append(
                f"square pixels required but sample aspect ratio is {sample_aspect_raw}"
            )

    decode_ok, decode_error = _decode_check(probed["media_path"])
    if not decode_ok:
        failures.append("full decode check failed")

    result = {
        "ok": not failures,
        "action": "verify",
        "media": str(probed["media_path"]),
        "relative_media": str(probed["relative_media"]),
        "actual": {
            "format": format_name_raw or None,
            "format_names": format_names,
            "duration": duration,
            "width": width,
            "height": height,
            "video_codec": video_codec,
            "avg_fps": fps,
            "sample_aspect_ratio": sample_aspect_raw,
            "display_aspect_ratio": display_aspect_raw,
            "video_stream_count": len(video_streams),
            "audio_stream_count": len(audio_streams),
            "audio_codec": audio_codec,
            "audio_channels": audio_channels,
            "audio_sample_rate": audio_sample_rate,
        },
        "expected": {
            "width": args.width,
            "height": args.height,
            "aspect": args.aspect,
            "container": args.container,
            "video_codec": args.video_codec,
            "duration_min": args.duration_min,
            "duration_max": args.duration_max,
            "fps": args.fps,
            "audio": args.audio,
            "audio_codec": args.audio_codec,
            "channels": args.channels,
            "sample_rate": args.sample_rate,
            "require_square_pixels": args.require_square_pixels,
        },
        "decode_ok": decode_ok,
        "decode_error": decode_error or None,
        "failures": failures,
        "warnings": warnings,
        "review_note": (
            "技术 QC 只确认媒体文件与显式交付参数；不能替代从头到尾观看成片、听完整音轨或核对字幕 / Logo / 产品内容。"
        ),
    }
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify project-local final video files against explicit delivery requirements."
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser(
        "verify",
        help="fully decode one project-local video and compare explicit delivery requirements",
    )
    verify.add_argument("project")
    verify.add_argument("media")
    verify.add_argument("--width", type=int)
    verify.add_argument("--height", type=int)
    verify.add_argument("--aspect")
    verify.add_argument("--container")
    verify.add_argument("--video-codec")
    verify.add_argument("--aspect-tolerance", type=float, default=0.01)
    verify.add_argument("--duration-min", type=float)
    verify.add_argument("--duration-max", type=float)
    verify.add_argument("--fps", type=float)
    verify.add_argument("--fps-tolerance", type=float, default=0.02)
    verify.add_argument(
        "--audio",
        choices=("any", "required", "forbidden"),
        default="any",
    )
    verify.add_argument("--audio-codec")
    verify.add_argument("--channels", type=int)
    verify.add_argument("--sample-rate", type=int)
    verify.add_argument("--require-square-pixels", action="store_true")
    verify.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except DeliveryQcError as exc:
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
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
