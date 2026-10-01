from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Any

from generation_receive import (
    ReceiveError,
    candidate_entries,
    cleanup_received_pack,
    copy_candidate,
    load_receive_log,
    next_take_number,
    render_receive_section,
    take_destination,
    write_receive_log,
)

PACK_PART_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SCOPED_PACK_RE = re.compile(r"^(shared|V\d+)/(G\d+)_(I\d+)$")
INPUT_RE = re.compile(r"^I\d+$")
PACK_META = ".akira-pack.json"
PACK_SNAPSHOT = ".akira-pack-snapshot"

class PackError(RuntimeError):
    pass

def _project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise PackError(f"project root does not exist: {root}")
    return root

def _pack_name(raw: str) -> str:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise PackError("pack name must be a project-local relative path without '..'")
    for part in path.parts:
        if not PACK_PART_RE.fullmatch(part):
            raise PackError(
                "each pack path component must match [A-Za-z0-9][A-Za-z0-9._-]*"
            )
    return path.as_posix()


def _pack_path(project: Path, name: str) -> Path:
    return project / ".tmp" / Path(name)


def _zip_path(project: Path, name: str) -> Path:
    rel = Path(name)
    return project / ".tmp" / rel.parent / f"{rel.name}.zip"


def _ensure_within(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise PackError(f"{label} escapes project root: {path}") from exc
    return resolved


def _safe_relative(raw: str, *, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise PackError(f"{label} must be a project-relative path without '..': {raw}")
    if not path.parts:
        raise PackError(f"{label} cannot be empty")
    return path


def _reject_internal_source(rel_source: Path) -> None:
    if rel_source.parts[0] in {".git", ".tmp"}:
        raise PackError(
            f"source must be a formal project file, not repository or temporary state: {rel_source}"
        )


def _require_video_destination(rel_dest: Path) -> None:
    if not rel_dest.parts or rel_dest.parts[0] != "video":
        raise PackError(f"formal returned media must archive under video/: {rel_dest}")


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


def _walk_files(root: Path, *, include_internal: bool = False) -> list[Path]:
    if not root.exists():
        return []
    result: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not (path.is_file() or path.is_symlink()):
            continue
        rel = path.relative_to(root)
        if not include_internal and rel.parts and rel.parts[0] in {PACK_META, PACK_SNAPSHOT}:
            continue
        result.append(path)
    return result


def _relative_files(root: Path) -> list[str]:
    return [str(path.relative_to(root)) for path in _walk_files(root)]


def _symlinks(root: Path) -> list[str]:
    return [
        str(path.relative_to(root))
        for path in _walk_files(root)
        if path.is_symlink()
    ]


def _returns_files(pack: Path) -> list[str]:
    returns = pack / "returns"
    if not returns.exists():
        return []
    return [str(path.relative_to(pack)) for path in _walk_files(returns)]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _meta_path(pack: Path) -> Path:
    return pack / PACK_META


def _load_meta(pack: Path) -> dict[str, Any]:
    path = _meta_path(pack)
    if not path.is_file():
        raise PackError(f"pack metadata is missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise PackError(f"pack metadata is unreadable: {path}") from exc


def _write_meta(pack: Path, meta: dict[str, Any]) -> None:
    _meta_path(pack).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _visible_input_files(pack: Path) -> list[Path]:
    result: list[Path] = []
    for path in _walk_files(pack):
        rel = path.relative_to(pack)
        if rel.parts and rel.parts[0] == "returns":
            continue
        result.append(path)
    return result


def _seal_pack(pack: Path) -> dict[str, Any]:
    meta = _load_meta(pack)
    if meta.get("sealed"):
        return meta
    if _returns_files(pack):
        raise PackError("cannot seal outbound pack after returned files have arrived")
    symlinks = _symlinks(pack)
    if symlinks:
        raise PackError("pack contains symlinks; make it self-contained before sealing")

    snapshot = pack / PACK_SNAPSHOT
    if snapshot.exists():
        shutil.rmtree(snapshot)
    snapshot.mkdir(parents=True)

    inputs: list[str] = []
    for source in _visible_input_files(pack):
        rel = source.relative_to(pack)
        dest = snapshot / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        inputs.append(str(rel))

    meta["sealed"] = True
    meta["sealed_inputs"] = sorted(inputs)
    _write_meta(pack, meta)
    return meta


def _snapshot_diff(pack: Path) -> dict[str, list[str]]:
    meta = _load_meta(pack)
    if not meta.get("sealed"):
        raise PackError("pack is not sealed; seal or zip it before external generation")
    snapshot = pack / PACK_SNAPSHOT
    if not snapshot.is_dir():
        raise PackError("sealed pack snapshot is missing")

    original = {str(path.relative_to(snapshot)): path for path in _walk_files(snapshot)}
    current = {str(path.relative_to(pack)): path for path in _visible_input_files(pack)}

    added = sorted(set(current) - set(original))
    removed = sorted(set(original) - set(current))
    changed: list[str] = []
    for rel in sorted(set(original) & set(current)):
        left, right = original[rel], current[rel]
        if left.is_symlink() or right.is_symlink() or not filecmp.cmp(left, right, shallow=False):
            changed.append(rel)
    return {"added": added, "removed": removed, "changed": changed}


def _parse_actual_sources(project: Path, values: list[str] | None) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for raw in values or []:
        if "=" not in raw:
            raise PackError("--actual-source must use PACK_REL=PROJECT_REL")
        pack_raw, project_raw = raw.split("=", 1)
        pack_rel = _safe_relative(pack_raw, label="pack input")
        project_rel = _safe_relative(project_raw, label="formal input source")
        _reject_internal_source(project_rel)
        formal = _ensure_within(project / project_rel, project, label="formal input source")
        if not formal.is_file() or formal.is_symlink():
            raise PackError(f"formal input source is not a regular file: {formal}")
        result[pack_rel.as_posix()] = formal
    return result


def _verify_input_drift(
    project: Path,
    pack: Path,
    overrides: dict[str, Path],
) -> dict[str, list[str]]:
    diff = _snapshot_diff(pack)
    if diff["removed"]:
        raise PackError(
            "pack input files were removed after sealing; formalize the actual input before receive: "
            + ", ".join(diff["removed"])
        )
    drifted = set(diff["added"]) | set(diff["changed"])
    missing = sorted(drifted - set(overrides))
    if missing:
        raise PackError(
            "pack inputs changed after handoff; save the actual input formally and map it with "
            "--actual-source before receive: " + ", ".join(missing)
        )
    for rel in sorted(drifted):
        current = pack / rel
        formal = overrides[rel]
        if current.is_symlink() or not current.is_file():
            raise PackError(f"changed pack input is not a regular file: {rel}")
        if not filecmp.cmp(current, formal, shallow=False):
            raise PackError(
                f"changed pack input does not match its formalized source: {rel} != {formal}"
            )
    return diff


def _parse_scoped_pack(name: str) -> tuple[str, str, str]:
    match = SCOPED_PACK_RE.fullmatch(name)
    if not match:
        raise PackError(
            "receive requires scoped pack name like V001/G003_I02 or shared/G003_I02"
        )
    return match.group(1), match.group(2), match.group(3)


def _resolve_id_dir(parent: Path, object_id: str, *, label: str) -> Path:
    if not parent.is_dir():
        raise PackError(f"{label} parent directory does not exist: {parent}")
    matches = [
        path for path in parent.iterdir()
        if path.is_dir() and (path.name == object_id or path.name.startswith(f"{object_id}_"))
    ]
    if not matches:
        raise PackError(f"{label} {object_id} does not exist under {parent}")
    if len(matches) > 1:
        raise PackError(f"{label} {object_id} is ambiguous under {parent}")
    return matches[0]


def _resolve_generation_dir(project: Path, scope: str, generation: str) -> Path:
    if scope == "shared":
        base = project / "video" / "shared"
    else:
        base = _resolve_id_dir(project / "video" / "videos", scope, label="video")
    return _resolve_id_dir(base / "generations", generation, label="generation")


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if pack.exists():
        raise PackError(f"pack already exists; resume or inspect it instead of recreating: {pack}")
    ignored_added = _ensure_tmp_ignored(project)
    pack.mkdir(parents=True)
    _write_meta(
        pack,
        {
            "schema": 1,
            "pack_id": uuid.uuid4().hex,
            "name": name,
            "sealed": False,
            "copies": [],
        },
    )
    return {
        "ok": True,
        "action": "init",
        "project": str(project),
        "pack": str(pack),
        "gitignore_updated": ignored_added,
    }


def cmd_copy(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist; run init first: {pack}")
    meta = _load_meta(pack)
    if meta.get("sealed"):
        raise PackError("pack is already sealed; create a new input version instead of editing it")

    source_arg = Path(args.source).expanduser()
    if source_arg.is_absolute():
        source_input = source_arg
        try:
            rel_source = source_input.resolve().relative_to(project)
        except ValueError as exc:
            raise PackError(f"source escapes project root: {source_input}") from exc
    else:
        rel_source = _safe_relative(args.source, label="source")
        _reject_internal_source(rel_source)
        source_input = project / rel_source
    source = _ensure_within(source_input, project, label="source")
    if source_arg.is_absolute():
        rel_source = source.relative_to(project)
        _reject_internal_source(rel_source)
    if not source.is_file():
        raise PackError(f"source is not a regular file: {source}")

    if args.dest:
        rel_dest = _safe_relative(args.dest, label="destination")
    else:
        rel_dest = Path("materials") / source.name

    dest = pack / rel_dest
    _ensure_within(dest.parent, pack, label="destination")
    if dest.exists() and not args.overwrite:
        raise PackError(f"destination already exists; use --overwrite only when intentional: {dest}")
    if dest.is_symlink():
        raise PackError(f"refusing to overwrite symlink destination: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)

    copies = [item for item in meta.get("copies", []) if item.get("destination") != rel_dest.as_posix()]
    copies.append({"source": rel_source.as_posix(), "destination": rel_dest.as_posix()})
    meta["copies"] = copies
    _write_meta(pack, meta)

    return {
        "ok": True,
        "action": "copy",
        "source": str(source),
        "destination": str(dest),
        "relative_destination": str(rel_dest),
    }


def cmd_returns(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist: {pack}")
    returns = pack / "returns"
    if returns.exists() and returns.is_symlink():
        raise PackError(f"returns path must not be a symlink: {returns}")
    returns.mkdir(exist_ok=True)
    return {"ok": True, "action": "returns", "returns": str(returns)}


def cmd_seal(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist: {pack}")
    meta = _seal_pack(pack)
    return {
        "ok": True,
        "action": "seal",
        "pack": str(pack),
        "pack_id": meta["pack_id"],
        "inputs": meta.get("sealed_inputs", []),
    }


def _status(project: Path, name: str) -> dict[str, Any]:
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist: {pack}")
    meta = _load_meta(pack)
    files = _relative_files(pack)
    symlinks = _symlinks(pack)
    returns_files = _returns_files(pack)
    return {
        "ok": not symlinks,
        "action": "status",
        "project": str(project),
        "pack": str(pack),
        "pack_id": meta["pack_id"],
        "sealed": bool(meta.get("sealed")),
        "files": files,
        "symlinks": symlinks,
        "returns_files": returns_files,
        "zip": str(_zip_path(project, name)) if _zip_path(project, name).exists() else None,
    }


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    return _status(_project_root(args.project), _pack_name(args.name))


def cmd_zip(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    status = _status(project, name)
    if status["symlinks"]:
        raise PackError("pack contains symlinks; make it self-contained before zipping")
    if status["returns_files"]:
        raise PackError("pack contains returned files; do not create an outbound zip after results arrive")

    _seal_pack(pack)
    archive = _zip_path(project, name)
    if archive.exists() and not args.overwrite:
        raise PackError(f"zip already exists; use --overwrite only when intentional: {archive}")

    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in _walk_files(pack):
            rel = path.relative_to(pack)
            if rel.parts and rel.parts[0] == "returns":
                continue
            if path.is_symlink():
                raise PackError(f"pack contains symlink: {path}")
            zf.write(path, rel)

    return {
        "ok": True,
        "action": "zip",
        "pack": str(pack),
        "zip": str(archive),
        "files": _relative_files(pack),
    }


def cmd_receive(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    scope, generation, pack_input = _parse_scoped_pack(name)
    generation_dir = _resolve_generation_dir(project, scope, generation)
    actual_input = args.input or pack_input
    if not INPUT_RE.fullmatch(actual_input):
        raise PackError(f"invalid input version: {actual_input}")

    log = load_receive_log(generation_dir)
    pack = _pack_path(project, name)
    if not pack.exists():
        previous = [
            entry for entry in log["packs"].values()
            if entry.get("pack_name") == name and entry.get("status") == "complete"
        ]
        if previous:
            return {
                "ok": True,
                "action": "receive",
                "already_received": True,
                "cleanup_pending": False,
                "takes": previous[-1].get("takes", []),
            }
        raise PackError(f"pack does not exist: {pack}")

    meta = _load_meta(pack)
    if meta.get("name") != name:
        raise PackError("pack metadata name does not match requested pack")
    if not meta.get("sealed"):
        raise PackError("pack is not sealed; seal or zip it before external generation")

    overrides = _parse_actual_sources(project, args.actual_source)
    drift = _verify_input_drift(project, pack, overrides)

    pack_id = str(meta["pack_id"])
    entry = log["packs"].get(pack_id)
    if entry is not None and entry.get("pack_name") != name:
        raise PackError("receive log pack identity collision")

    if entry is None:
        candidates = candidate_entries(pack / "returns")
        next_number = next_take_number(generation_dir)
        takes: list[dict[str, Any]] = []
        for offset, source in enumerate(candidates):
            dest = take_destination(generation_dir, next_number + offset, source)
            takes.append(
                {
                    "source": source.name,
                    "take": dest.name,
                    "kind": "bundle" if source.is_dir() else "file",
                }
            )
        entry = {
            "pack_name": name,
            "input": actual_input,
            "status": "in_progress",
            "takes": takes,
            "input_drift": drift,
            "actual_sources": {
                key: str(path.relative_to(project)) for key, path in overrides.items()
            },
        }
        log["packs"][pack_id] = entry
        write_receive_log(generation_dir, log)
    else:
        if entry.get("input") != actual_input:
            raise PackError(
                f"pack was already reserved for {entry.get('input')}, not {actual_input}"
            )

    returns = pack / "returns"
    for item in entry["takes"]:
        source = returns / item["source"]
        dest = generation_dir / item["take"]
        if not source.exists():
            if dest.exists():
                continue
            raise PackError(f"reserved returned candidate is missing: {source}")
        copy_candidate(source, dest)

    entry["status"] = "files_saved"
    write_receive_log(generation_dir, log)
    render_receive_section(generation_dir, log)
    entry["status"] = "complete"
    write_receive_log(generation_dir, log)

    cleaned, cleanup_error = cleanup_received_pack(pack, _zip_path(project, name))
    return {
        "ok": True,
        "action": "receive",
        "already_received": False,
        "input": actual_input,
        "takes": entry["takes"],
        "cleanup_pending": not cleaned,
        "cleanup_error": cleanup_error,
    }


def cmd_archive(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist: {pack}")
    if not args.confirm_reviewed:
        raise PackError(
            "archive requires --confirm-reviewed after video-review has accepted this returned file"
        )

    returns = pack / "returns"
    if not returns.is_dir():
        raise PackError(f"returns directory does not exist: {returns}")
    rel_source = _safe_relative(args.source, label="returned source")
    source_input = returns / rel_source
    if source_input.is_symlink():
        raise PackError(f"returned source must be a regular file, not a symlink: {source_input}")
    source = _ensure_within(source_input, returns, label="returned source")
    if not source.is_file():
        raise PackError(f"returned source is not a regular file: {source}")

    rel_dest = _safe_relative(args.dest, label="formal destination")
    if rel_dest.parts[0] == ".tmp":
        raise PackError("formal destination must not remain under .tmp/")
    _require_video_destination(rel_dest)
    dest = project / rel_dest
    _ensure_within(dest.parent, project, label="formal destination")
    if dest.exists() or dest.is_symlink():
        raise PackError(f"formal destination already exists; refusing to overwrite: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)

    return {
        "ok": True,
        "action": "archive",
        "source": str(source),
        "destination": str(dest),
        "relative_destination": str(rel_dest),
        "sha256": _sha256(dest),
        "size": dest.stat().st_size,
        "source_preserved": source.exists(),
    }


def cmd_next_take(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    rel_shot = _safe_relative(args.shot_dir, label="shot directory")
    if len(rel_shot.parts) < 3 or rel_shot.parts[:2] != ("video", "shots"):
        raise PackError(f"shot directory must be under video/shots/: {rel_shot}")
    shot_input = project / rel_shot
    shot = _ensure_within(shot_input, project / "video" / "shots", label="shot directory")
    if not shot.is_dir():
        raise PackError(f"shot directory does not exist: {shot}")

    ext = args.ext.lstrip(".")
    if not re.fullmatch(r"[A-Za-z0-9]+", ext):
        raise PackError(f"invalid file extension: {args.ext}")
    pattern = re.compile(rf"^take(\d+)\.{re.escape(ext)}$")
    numbers: list[int] = []
    for path in shot.iterdir():
        if not path.is_file():
            continue
        match = pattern.fullmatch(path.name)
        if match:
            numbers.append(int(match.group(1)))
    number = max(numbers, default=0) + 1
    filename = f"take{number:02d}.{ext}"
    return {
        "ok": True,
        "action": "next-take",
        "shot": str(shot),
        "number": number,
        "filename": filename,
        "relative_path": str(rel_shot / filename),
    }


def cmd_cleanup(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist: {pack}")
    if not args.confirm_no_unique_info:
        raise PackError(
            "cleanup requires --confirm-no-unique-info after verifying formal project files own all lasting information"
        )

    returns_files = _returns_files(pack)
    if returns_files and not args.confirm_returns_archived:
        raise PackError(
            "returned files still exist; use --confirm-returns-archived only after they are formally archived"
        )

    shutil.rmtree(pack)
    archive = _zip_path(project, name)
    zip_removed = False
    if archive.exists():
        archive.unlink()
        zip_removed = True

    return {
        "ok": True,
        "action": "cleanup",
        "pack_removed": str(pack),
        "zip_removed": zip_removed,
        "returns_files_before_cleanup": returns_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage project-local Akira Video one-time generation packs."
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create .tmp/<name> and ensure .tmp/ is gitignored")
    init.add_argument("project")
    init.add_argument("name")
    init.set_defaults(func=cmd_init)

    copy = sub.add_parser("copy", help="copy one formal project file into an existing pack")
    copy.add_argument("project")
    copy.add_argument("name")
    copy.add_argument("source")
    copy.add_argument("--dest")
    copy.add_argument("--overwrite", action="store_true")
    copy.set_defaults(func=cmd_copy)

    returns = sub.add_parser("returns", help="create the pack-local returns directory")
    returns.add_argument("project")
    returns.add_argument("name")
    returns.set_defaults(func=cmd_returns)

    seal = sub.add_parser("seal", help="freeze outbound pack inputs before external generation")
    seal.add_argument("project")
    seal.add_argument("name")
    seal.set_defaults(func=cmd_seal)

    status = sub.add_parser("status", help="inspect pack files, symlinks, returns, and zip")
    status.add_argument("project")
    status.add_argument("name")
    status.set_defaults(func=cmd_status)

    receive = sub.add_parser(
        "receive",
        help="idempotently import all returned candidates for a scoped G/I and clean the pack",
    )
    receive.add_argument("project")
    receive.add_argument("name", help="V001/G003_I02 or shared/G003_I02")
    receive.add_argument(
        "--input",
        help="actual I used when the user changed inputs after handoff",
    )
    receive.add_argument(
        "--actual-source",
        action="append",
        help="formalize changed input as PACK_REL=PROJECT_REL; repeat as needed",
    )
    receive.set_defaults(func=cmd_receive)

    archive = sub.add_parser(
        "archive",
        help="legacy: copy one reviewed returned file into its formal project destination",
    )
    archive.add_argument("project")
    archive.add_argument("name")
    archive.add_argument("source", help="path relative to pack returns/")
    archive.add_argument("--dest", required=True, help="formal project-relative destination outside .tmp/")
    archive.add_argument("--confirm-reviewed", action="store_true")
    archive.set_defaults(func=cmd_archive)

    next_take = sub.add_parser(
        "next-take",
        help="legacy: return the next monotonic takeNN filename for a formal shot directory",
    )
    next_take.add_argument("project")
    next_take.add_argument("shot_dir", help="project-relative shot directory")
    next_take.add_argument("--ext", default="mp4")
    next_take.set_defaults(func=cmd_next_take)

    zip_cmd = sub.add_parser("zip", help="seal and zip a self-contained outbound pack")
    zip_cmd.add_argument("project")
    zip_cmd.add_argument("name")
    zip_cmd.add_argument("--overwrite", action="store_true")
    zip_cmd.set_defaults(func=cmd_zip)

    cleanup = sub.add_parser("cleanup", help="legacy manual pack cleanup with explicit confirmations")
    cleanup.add_argument("project")
    cleanup.add_argument("name")
    cleanup.add_argument("--confirm-no-unique-info", action="store_true")
    cleanup.add_argument("--confirm-returns-archived", action="store_true")
    cleanup.set_defaults(func=cmd_cleanup)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except (PackError, ReceiveError) as exc:
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
