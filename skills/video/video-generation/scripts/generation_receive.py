from __future__ import annotations

import filecmp
import json
import re
import shutil
from pathlib import Path
from typing import Any


TAKE_RE = re.compile(r"^take(\d+)(?:\..+)?$")
RECEIVE_LOG = ".receive-log.json"
RECEIVE_START = "<!-- akira-video:receive:start -->"
RECEIVE_END = "<!-- akira-video:receive:end -->"


class ReceiveError(RuntimeError):
    pass


def _walk_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() or path.is_symlink())


def load_receive_log(generation_dir: Path) -> dict[str, Any]:
    path = generation_dir / RECEIVE_LOG
    if not path.exists():
        return {"schema": 1, "packs": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ReceiveError(f"receive log is unreadable: {path}") from exc
    if not isinstance(data.get("packs"), dict):
        raise ReceiveError(f"receive log has invalid structure: {path}")
    return data


def write_receive_log(generation_dir: Path, data: dict[str, Any]) -> None:
    path = generation_dir / RECEIVE_LOG
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def next_take_number(generation_dir: Path) -> int:
    numbers: list[int] = []
    for path in generation_dir.iterdir():
        match = TAKE_RE.fullmatch(path.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def candidate_entries(returns: Path) -> list[Path]:
    if not returns.is_dir():
        raise ReceiveError(f"returns directory does not exist: {returns}")
    entries = [path for path in sorted(returns.iterdir()) if not path.name.startswith(".")]
    if not entries:
        raise ReceiveError(f"returns directory is empty: {returns}")
    for path in entries:
        if path.is_symlink():
            raise ReceiveError(f"returned candidate must not be a symlink: {path}")
        if not path.is_file() and not path.is_dir():
            raise ReceiveError(f"unsupported returned candidate: {path}")
        if path.is_dir() and any(item.is_symlink() for item in path.rglob("*")):
            raise ReceiveError(f"returned candidate bundle contains symlink: {path}")
    return entries


def take_destination(generation_dir: Path, number: int, source: Path) -> Path:
    stem = f"take{number:02d}"
    if source.is_dir():
        return generation_dir / stem
    return generation_dir / f"{stem}{source.suffix}"


def paths_equal(left: Path, right: Path) -> bool:
    if left.is_file() and right.is_file():
        return filecmp.cmp(left, right, shallow=False)
    if left.is_dir() and right.is_dir():
        left_files = {str(path.relative_to(left)): path for path in _walk_files(left)}
        right_files = {str(path.relative_to(right)): path for path in _walk_files(right)}
        if set(left_files) != set(right_files):
            return False
        return all(
            filecmp.cmp(left_files[key], right_files[key], shallow=False)
            for key in left_files
        )
    return False


def copy_candidate(source: Path, dest: Path) -> None:
    if dest.exists():
        if paths_equal(source, dest):
            return
        raise ReceiveError(
            f"reserved take destination already exists with different content: {dest}"
        )
    if source.is_dir():
        shutil.copytree(source, dest)
    else:
        shutil.copy2(source, dest)


def render_receive_section(generation_dir: Path, log: dict[str, Any]) -> None:
    generation_md = generation_dir / "GENERATION.md"
    if not generation_md.is_file():
        raise ReceiveError(f"GENERATION.md is required before receive: {generation_md}")

    lines = ["## Returned Takes"]
    entries: list[tuple[int, str]] = []
    for pack in log["packs"].values():
        if pack.get("status") not in {"files_saved", "complete"}:
            continue
        input_id = pack["input"]
        for item in pack.get("takes", []):
            take_name = item["take"]
            match = TAKE_RE.fullmatch(take_name)
            number = int(match.group(1)) if match else 10**9
            source = item["source"]
            entries.append((number, f"- {take_name} — {input_id} — source {source}"))
    for _, line in sorted(entries, key=lambda pair: (pair[0], pair[1])):
        lines.append(line)

    section = RECEIVE_START + "\n" + "\n".join(lines) + "\n" + RECEIVE_END
    text = generation_md.read_text(encoding="utf-8")
    if RECEIVE_START in text and RECEIVE_END in text:
        before, rest = text.split(RECEIVE_START, 1)
        _, after = rest.split(RECEIVE_END, 1)
        updated = before.rstrip() + "\n\n" + section + after
    else:
        updated = text.rstrip() + "\n\n" + section + "\n"
    generation_md.write_text(updated, encoding="utf-8")


def cleanup_received_pack(pack: Path, archive: Path) -> tuple[bool, str | None]:
    try:
        if pack.exists():
            shutil.rmtree(pack)
        if archive.exists():
            archive.unlink()
    except OSError as exc:
        return False, str(exc)
    return True, None
