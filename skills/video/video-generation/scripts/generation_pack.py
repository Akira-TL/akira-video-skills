from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any


PACK_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class PackError(RuntimeError):
    pass


def _project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise PackError(f"project root does not exist: {root}")
    return root


def _pack_name(raw: str) -> str:
    if not PACK_NAME_RE.fullmatch(raw):
        raise PackError(
            "pack name must match [A-Za-z0-9][A-Za-z0-9._-]* and contain no path separators"
        )
    return raw


def _pack_path(project: Path, name: str) -> Path:
    return project / ".tmp" / name


def _zip_path(project: Path, name: str) -> Path:
    return project / ".tmp" / f"{name}.zip"


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


def _walk_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() or path.is_symlink())


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
    return [
        str(path.relative_to(pack))
        for path in _walk_files(returns)
        if path.is_file() and not path.is_symlink()
    ]


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _pack_name(args.name)
    pack = _pack_path(project, name)
    if pack.exists():
        raise PackError(f"pack already exists; resume or inspect it instead of recreating: {pack}")
    ignored_added = _ensure_tmp_ignored(project)
    pack.mkdir(parents=True)
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

    source_input = Path(args.source).expanduser()
    if not source_input.is_absolute():
        source_input = project / source_input
    source = _ensure_within(source_input, project, label="source")
    if not source.is_file():
        raise PackError(f"source is not a regular file: {source}")
    if source_input.is_symlink() and source != source_input.absolute():
        # _ensure_within already guarantees the target remains inside project.
        pass

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
    return {
        "ok": True,
        "action": "returns",
        "returns": str(returns),
    }


def _status(project: Path, name: str) -> dict[str, Any]:
    pack = _pack_path(project, name)
    if not pack.is_dir():
        raise PackError(f"pack does not exist: {pack}")
    files = _relative_files(pack)
    symlinks = _symlinks(pack)
    returns_files = _returns_files(pack)
    return {
        "ok": not symlinks,
        "action": "status",
        "project": str(project),
        "pack": str(pack),
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
        raise PackError(
            "pack contains returned files; do not create an outbound zip after results arrive"
        )

    archive = _zip_path(project, name)
    if archive.exists() and not args.overwrite:
        raise PackError(f"zip already exists; use --overwrite only when intentional: {archive}")

    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in _walk_files(pack):
            if path.is_symlink():
                raise PackError(f"pack contains symlink: {path}")
            zf.write(path, path.relative_to(pack))

    return {
        "ok": True,
        "action": "zip",
        "pack": str(pack),
        "zip": str(archive),
        "files": status["files"],
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

    status = sub.add_parser("status", help="inspect pack files, symlinks, returns, and zip")
    status.add_argument("project")
    status.add_argument("name")
    status.set_defaults(func=cmd_status)

    zip_cmd = sub.add_parser("zip", help="create .tmp/<name>.zip from a self-contained pack")
    zip_cmd.add_argument("project")
    zip_cmd.add_argument("name")
    zip_cmd.add_argument("--overwrite", action="store_true")
    zip_cmd.set_defaults(func=cmd_zip)

    cleanup = sub.add_parser("cleanup", help="delete pack and companion zip with explicit safety confirmations")
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
    except PackError as exc:
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
