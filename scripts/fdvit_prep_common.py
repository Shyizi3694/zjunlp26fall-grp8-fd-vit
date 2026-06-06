#!/usr/bin/env python3
"""Shared helpers for FD-VIT preparation scripts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def repo_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path


def display_path(path: str | Path) -> str:
    resolved = repo_path(path)
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def write_json(path: str | Path, payload: dict[str, Any], *, overwrite: bool) -> Path:
    target = repo_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def append_log(path: str | Path | None, message: str) -> None:
    if path is None:
        return
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip() + "\n")


def emit(message: str, *, log_file: str | Path | None = None) -> None:
    print(message)
    append_log(log_file, message)


def safe_mkdir(path: str | Path, *, dry_run: bool) -> str:
    target = repo_path(path)
    if dry_run:
        return "planned"
    target.mkdir(parents=True, exist_ok=True)
    return "created" if target.exists() else "missing"
