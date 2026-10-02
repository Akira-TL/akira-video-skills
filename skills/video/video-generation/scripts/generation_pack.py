from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import re
import shutil
import sys
import tarfile
import uuid
from pathlib import Path
from typing import Any

from generation_receive import (
    ReceiveError,
    candidate_entries,
    copy_candidate,
    load_receive_log,
    next_take_number,
    render_receive_section,
    take_destination,
    write_receive_log,
)


BATCH_RE = re.compile(r"^B\d{3}(?:_[A-Za-z0-9._-]+)?$")
INPUT_RE = re.compile(r"^I\d+$")
GENERATION_RE = re.compile(r"^G\d+(?:_[A-Za-z0-9._-]+)?$")
OWNER_RE = re.compile(r"^(V\d+|CHR\d+|LOC\d+|PROP\d+|PROD\d+)")
BATCH_META = ".akira-batch.json"


class PackError(RuntimeError):
    pass


def _project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise PackError(f"project root does not exist: {root}")
    return root


def _batch_name(raw: str) -> str:
    if "/" in raw or "\\" in raw or not BATCH_RE.fullmatch(raw):
        raise PackError("batch name must look like B001 or B001_label")
    return raw


def _batch_root(project: Path, name: str) -> Path:
    return project / "video" / "batches" / name


def _archive_path(project: Path, name: str) -> Path:
    return _batch_root(project, name) / f"{name}.tar.gz"


def _meta_path(batch: Path) -> Path:
    return batch / BATCH_META


def _ensure_within(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise PackError(f"{label} escapes project root: {path}") from exc
    return resolved


def _safe_relative(raw: str, *, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise PackError(f"{label} must be a project-relative path without '..': {raw}")
    return path


def _ensure_batches_ignored(project: Path) -> bool:
    gitignore = project / ".gitignore"
    current = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    lines = current.splitlines()
    marker = "video/batches/"
    if marker in lines:
        return False
    text = current
    if text and not text.endswith("\n"):
        text += "\n"
    text += marker + "\n"
    gitignore.write_text(text, encoding="utf-8")
    return True


def _load_meta(batch: Path) -> dict[str, Any]:
    path = _meta_path(batch)
    if not path.is_file():
        raise PackError(f"batch metadata is missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise PackError(f"batch metadata is unreadable: {path}") from exc
    if data.get("schema") != 2 or not isinstance(data.get("tasks"), dict):
        raise PackError(f"batch metadata has invalid structure: {path}")
    return data


def _write_meta(batch: Path, meta: dict[str, Any]) -> None:
    _meta_path(batch).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _formal_file(project: Path, raw: str, *, label: str) -> tuple[Path, Path]:
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        resolved = _ensure_within(candidate, project, label=label)
        rel = resolved.relative_to(project)
    else:
        rel = _safe_relative(raw, label=label)
        if rel.parts[0] in {".git", ".tmp"} or rel.parts[:2] == ("video", "batches"):
            raise PackError(f"{label} must be a formal project file: {rel}")
        resolved = _ensure_within(project / rel, project, label=label)
    if not resolved.is_file():
        raise PackError(f"{label} is not a regular file: {resolved}")
    return resolved, rel


def _generation_dir(project: Path, raw: str) -> tuple[Path, Path]:
    rel = _safe_relative(raw, label="generation directory")
    if rel.parts[0] != "video" or rel.parts[:2] == ("video", "batches"):
        raise PackError("generation directory must be a formal path under video/")
    generation = _ensure_within(project / rel, project / "video", label="generation directory")
    if not generation.is_dir():
        raise PackError(f"generation directory does not exist: {generation}")
    if not GENERATION_RE.fullmatch(generation.name):
        raise PackError(f"generation directory must use a Gxxx identity: {generation.name}")
    if not (generation / "GENERATION.md").is_file():
        raise PackError(f"GENERATION.md is required: {generation}")
    return generation, rel


def _task_key(generation_rel: Path, input_id: str) -> str:
    generation_id = generation_rel.name.split("_", 1)[0]
    owner = None
    for part in reversed(generation_rel.parts[:-1]):
        match = OWNER_RE.match(part)
        if match:
            owner = match.group(1)
            break
    prefix = f"{owner}_" if owner else ""
    return f"{prefix}{generation_id}_{input_id}"


def _reference_spec(raw: str) -> tuple[Path | None, str]:
    if "=" not in raw:
        return None, raw
    left, right = raw.split("=", 1)
    dest = _safe_relative(left, label="reference destination")
    if dest.parts[0] == "references":
        dest = Path(*dest.parts[1:])
    if not dest.parts:
        raise PackError("reference destination cannot be empty")
    return dest, right


def _copy_reference(
    project: Path,
    batch: Path,
    meta: dict[str, Any],
    raw: str,
) -> str:
    requested_dest, source_raw = _reference_spec(raw)
    source, source_rel = _formal_file(project, source_raw, label="reference")
    existing = meta.setdefault("references", {})
    source_key = source_rel.as_posix()
    if source_key in existing:
        return str(existing[source_key])

    rel_dest = requested_dest or Path(source.name)
    dest = batch / "references" / rel_dest
    _ensure_within(dest.parent, batch / "references", label="reference destination")
    if dest.exists():
        if dest.is_file() and filecmp.cmp(source, dest, shallow=False):
            existing[source_key] = (Path("references") / rel_dest).as_posix()
            return str(existing[source_key])
        raise PackError(
            f"reference destination collision; use DEST=SOURCE to disambiguate: {rel_dest}"
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    stored = (Path("references") / rel_dest).as_posix()
    existing[source_key] = stored
    return stored


def _package_files(batch: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in ("README.md", "tasks", "references"):
        root = batch / root_name
        if root.is_file():
            result.append(root)
        elif root.is_dir():
            result.extend(
                sorted(
                    path
                    for path in root.rglob("*")
                    if path.is_file() and not path.is_symlink()
                )
            )
    return result


def _hash_package(batch: Path) -> dict[str, str]:
    return {
        path.relative_to(batch).as_posix(): _sha256(path)
        for path in _package_files(batch)
    }


def _write_readme(batch: Path, name: str, meta: dict[str, Any]) -> None:
    lines = [
        f"# {name} 生成批次",
        "",
        "本目录是一批外部生成任务的执行快照。每个任务只保留本次实际使用的 Prompt；共享参考只保存一份。",
        "",
        "## 任务",
        "",
        "| 任务 | 正式 Generation | Input | Prompt | 参考 | 返回目录 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for task_name, task in meta["tasks"].items():
        refs = ", ".join(task.get("references", [])) or "无"
        lines.append(
            f"| {task_name} | {task['generation']} | {task['input']} | "
            f"tasks/{task_name}/prompt.md | {refs} | returns/{task_name}/ |"
        )
    lines.extend(
        [
            "",
            "## 执行",
            "",
            "1. 按任务读取对应 prompt.md。",
            "2. 任务需要的上传素材从 references/ 取；同一参考不会为每个 Generation 重复复制。",
            "3. 每个任务的所有候选结果放入对应 returns/<任务>/。",
            "4. 返回后运行批次 Receive；正式 Take 会进入原 Generation，并与 Prompt 共置。",
            "",
            "本批次只有这一份执行说明，不为每个 Generation 创建 handoff / instructions 副本。",
            "",
        ]
    )
    (batch / "README.md").write_text("\n".join(lines), encoding="utf-8")


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _batch_name(args.name)
    batch = _batch_root(project, name)
    if batch.exists():
        raise PackError(f"batch already exists: {batch}")
    ignored_added = _ensure_batches_ignored(project)
    batch.mkdir(parents=True)
    _write_meta(
        batch,
        {
            "schema": 2,
            "batch_id": uuid.uuid4().hex,
            "name": name,
            "built": False,
            "tasks": {},
            "references": {},
        },
    )
    return {
        "ok": True,
        "action": "init",
        "batch": str(batch),
        "gitignore_updated": ignored_added,
    }


def cmd_add(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _batch_name(args.name)
    batch = _batch_root(project, name)
    if not batch.is_dir():
        raise PackError(f"batch does not exist: {batch}")
    meta = _load_meta(batch)
    if meta.get("built"):
        raise PackError("batch is already built; create a new Bxxx batch for another external run")

    input_id = args.input
    if not INPUT_RE.fullmatch(input_id):
        raise PackError(f"invalid input version: {input_id}")

    generation, generation_rel = _generation_dir(project, args.generation)
    prompt = generation / f"prompt_{input_id.lower()}.md"
    if not prompt.is_file():
        raise PackError(f"formal prompt does not exist for {input_id}: {prompt}")

    task_name = args.task or _task_key(generation_rel, input_id)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_name):
        raise PackError("task name must contain only letters, numbers, dot, underscore or hyphen")

    tasks = meta["tasks"]
    if task_name in tasks:
        existing = tasks[task_name]
        if existing["generation"] == generation_rel.as_posix() and existing["input"] == input_id:
            return {
                "ok": True,
                "action": "add",
                "task": task_name,
                "already_added": True,
                "references": existing.get("references", []),
            }
        raise PackError(f"task name already belongs to another Generation: {task_name}")

    task_dir = batch / "tasks" / task_name
    task_dir.mkdir(parents=True)
    shutil.copy2(prompt, task_dir / "prompt.md")

    references = [
        _copy_reference(project, batch, meta, raw)
        for raw in (args.reference or [])
    ]
    (batch / "returns" / task_name).mkdir(parents=True, exist_ok=True)
    tasks[task_name] = {
        "generation": generation_rel.as_posix(),
        "input": input_id,
        "prompt_source": prompt.relative_to(project).as_posix(),
        "references": references,
    }
    _write_meta(batch, meta)
    return {
        "ok": True,
        "action": "add",
        "task": task_name,
        "generation": generation_rel.as_posix(),
        "input": input_id,
        "prompt": str(task_dir / "prompt.md"),
        "references": references,
    }


def cmd_build(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _batch_name(args.name)
    batch = _batch_root(project, name)
    if not batch.is_dir():
        raise PackError(f"batch does not exist: {batch}")
    meta = _load_meta(batch)
    if not meta["tasks"]:
        raise PackError("batch has no Generation tasks")

    archive = _archive_path(project, name)
    if meta.get("built") and archive.is_file():
        current = _hash_package(batch)
        if current == meta.get("built_hashes", {}):
            return {
                "ok": True,
                "action": "build",
                "already_built": True,
                "batch": str(batch),
                "archive": str(archive),
                "files": sorted(current),
            }
        if not args.overwrite:
            raise PackError("batch inputs changed after build; create a new batch or use --overwrite intentionally")

    _write_readme(batch, name, meta)
    for path in _package_files(batch):
        if path.is_symlink():
            raise PackError(f"batch contains symlink: {path}")

    hashes = _hash_package(batch)
    if archive.exists() and not args.overwrite:
        raise PackError(f"archive already exists: {archive}")
    if archive.exists():
        archive.unlink()

    with tarfile.open(archive, "w:gz") as tf:
        for path in _package_files(batch):
            rel = path.relative_to(batch)
            tf.add(path, arcname=(Path(name) / rel).as_posix(), recursive=False)

    meta["built"] = True
    meta["built_hashes"] = hashes
    _write_meta(batch, meta)
    return {
        "ok": True,
        "action": "build",
        "batch": str(batch),
        "archive": str(archive),
        "files": sorted(hashes),
    }


def _returns_files(batch: Path, task_name: str) -> list[str]:
    root = batch / "returns" / task_name
    if not root.is_dir():
        return []
    return [
        path.relative_to(root).as_posix()
        for path in sorted(root.iterdir())
        if not path.name.startswith(".")
    ]


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _batch_name(args.name)
    batch = _batch_root(project, name)
    if not batch.is_dir():
        raise PackError(f"batch does not exist: {batch}")
    meta = _load_meta(batch)
    return {
        "ok": True,
        "action": "status",
        "batch": str(batch),
        "built": bool(meta.get("built")),
        "archive": str(_archive_path(project, name)) if _archive_path(project, name).is_file() else None,
        "tasks": {
            key: {
                **value,
                "returns": _returns_files(batch, key),
            }
            for key, value in meta["tasks"].items()
        },
    }


def _verify_built_inputs(batch: Path, meta: dict[str, Any]) -> None:
    if not meta.get("built"):
        raise PackError("batch is not built; build the tar.gz before external generation")
    current = _hash_package(batch)
    expected = meta.get("built_hashes", {})
    if current != expected:
        added = sorted(set(current) - set(expected))
        removed = sorted(set(expected) - set(current))
        changed = sorted(
            key for key in set(current) & set(expected) if current[key] != expected[key]
        )
        details = []
        if added:
            details.append("added=" + ",".join(added))
        if removed:
            details.append("removed=" + ",".join(removed))
        if changed:
            details.append("changed=" + ",".join(changed))
        raise PackError(
            "batch inputs changed after build; formalize the actual G/I and build a new batch: "
            + "; ".join(details)
        )


def _receive_task(
    project: Path,
    batch: Path,
    meta: dict[str, Any],
    task_name: str,
) -> tuple[bool, list[dict[str, Any]]]:
    task = meta["tasks"][task_name]
    generation, generation_rel = _generation_dir(project, task["generation"])
    if generation_rel.as_posix() != task["generation"]:
        raise PackError(f"Generation path changed unexpectedly: {task['generation']}")

    log = load_receive_log(generation)
    log_key = f"batch:{meta['batch_id']}:{task_name}"
    entry = log["packs"].get(log_key)
    if entry is not None and entry.get("status") == "complete":
        return True, list(entry.get("takes", []))

    returns = batch / "returns" / task_name
    candidates = candidate_entries(returns)
    next_number = next_take_number(generation)
    takes: list[dict[str, Any]] = []
    for offset, source in enumerate(candidates):
        dest = take_destination(generation, next_number + offset, source)
        takes.append(
            {
                "source": source.name,
                "take": dest.name,
                "kind": "bundle" if source.is_dir() else "file",
            }
        )

    entry = {
        "pack_name": f"{meta['name']}/{task_name}",
        "input": task["input"],
        "status": "in_progress",
        "takes": takes,
    }
    log["packs"][log_key] = entry
    write_receive_log(generation, log)

    for item in takes:
        source = returns / item["source"]
        dest = generation / item["take"]
        copy_candidate(source, dest)

    entry["status"] = "files_saved"
    write_receive_log(generation, log)
    render_receive_section(generation, log)
    entry["status"] = "complete"
    write_receive_log(generation, log)
    return False, takes


def cmd_receive(args: argparse.Namespace) -> dict[str, Any]:
    project = _project_root(args.project)
    name = _batch_name(args.name)
    batch = _batch_root(project, name)
    if not batch.is_dir():
        raise PackError(f"batch does not exist: {batch}")
    meta = _load_meta(batch)
    _verify_built_inputs(batch, meta)

    selected = args.task or list(meta["tasks"])
    unknown = [task for task in selected if task not in meta["tasks"]]
    if unknown:
        raise PackError("unknown batch task: " + ", ".join(unknown))

    received_tasks: list[str] = []
    details: dict[str, Any] = {}
    newly_received = False
    for task_name in selected:
        returns = batch / "returns" / task_name
        has_returns = returns.is_dir() and any(
            not path.name.startswith(".") for path in returns.iterdir()
        )
        task = meta["tasks"][task_name]
        generation, _ = _generation_dir(project, task["generation"])
        log = load_receive_log(generation)
        log_key = f"batch:{meta['batch_id']}:{task_name}"
        complete = (
            log_key in log["packs"]
            and log["packs"][log_key].get("status") == "complete"
        )
        if not has_returns and not complete:
            continue
        already, takes = _receive_task(project, batch, meta, task_name)
        received_tasks.append(task_name)
        details[task_name] = {"already_received": already, "takes": takes}
        newly_received = newly_received or not already

    if not received_tasks:
        raise PackError("batch has no returned candidates yet")

    return {
        "ok": True,
        "action": "receive",
        "batch": str(batch),
        "received_tasks": received_tasks,
        "already_received": not newly_received,
        "tasks": details,
        "archive_preserved": _archive_path(project, name).is_file(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and receive retained multi-Generation Akira Video batches."
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create video/batches/Bxxx")
    init.add_argument("project")
    init.add_argument("name")
    init.set_defaults(func=cmd_init)

    add = sub.add_parser("add", help="add one formal G/I task to a batch")
    add.add_argument("project")
    add.add_argument("name")
    add.add_argument("generation", help="formal project-relative Generation directory")
    add.add_argument("--input", required=True, help="I01, I02, ...")
    add.add_argument("--task", help="optional human-readable task key")
    add.add_argument(
        "--reference",
        action="append",
        help="formal project file, or DEST=SOURCE; repeat as needed",
    )
    add.set_defaults(func=cmd_add)

    build = sub.add_parser("build", help="write one retained tar.gz for the whole batch")
    build.add_argument("project")
    build.add_argument("name")
    build.add_argument("--overwrite", action="store_true")
    build.set_defaults(func=cmd_build)

    status = sub.add_parser("status", help="inspect batch tasks, archive and returns")
    status.add_argument("project")
    status.add_argument("name")
    status.set_defaults(func=cmd_status)

    receive = sub.add_parser(
        "receive",
        help="import returned candidates for every ready task without deleting the batch",
    )
    receive.add_argument("project")
    receive.add_argument("name")
    receive.add_argument("--task", action="append", help="receive only this task; repeat as needed")
    receive.set_defaults(func=cmd_receive)

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
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
