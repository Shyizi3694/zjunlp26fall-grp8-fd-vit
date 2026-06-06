#!/usr/bin/env python3
"""Prepare the FD-VIT local Python environment and project directories."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, display_path, emit, repo_path, safe_mkdir, utc_now, write_json


REQUIRED_DIRS = [
    "configs",
    "data/raw/okvqa",
    "data/raw/coco/train2014",
    "data/raw/coco/val2014",
    "data/interim",
    "data/processed/okvqa",
    "data/samples",
    "models",
    "checkpoints",
    "outputs",
    "logs",
    "prompts",
    "src/fdvit",
]


def venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts/python.exe"
    return venv_dir / "bin/python"


def run_command(command: list[str], *, dry_run: bool, log_file: str | None) -> dict[str, Any]:
    printable = " ".join(command)
    if dry_run:
        emit(f"planned: {printable}", log_file=log_file)
        return {"command": command, "status": "planned", "returncode": None}
    emit(f"running: {printable}", log_file=log_file)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.stdout.strip():
        emit(completed.stdout.strip(), log_file=log_file)
    if completed.stderr.strip():
        emit(completed.stderr.strip(), log_file=log_file)
    return {
        "command": command,
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", default="requirements.txt", help="requirements file to install")
    parser.add_argument("--venv", default=".venv", help="virtualenv directory")
    parser.add_argument("--create_venv", action="store_true", help="create --venv with the current Python")
    parser.add_argument("--install", action="store_true", help="install --requirements into --venv or current env")
    parser.add_argument("--run_check_env", action="store_true", help="run scripts/check_env.py after preparation")
    parser.add_argument("--output", default="logs/environment_prepare.json", help="JSON summary path")
    parser.add_argument("--overwrite", action="store_true", help="overwrite --output if it already exists")
    parser.add_argument("--dry_run", action="store_true", help="show actions without creating env or installing packages")
    parser.add_argument("--log_file", default=None, help="optional text log path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requirements = repo_path(args.requirements)
    venv_dir = repo_path(args.venv)

    summary: dict[str, Any] = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "dry_run": args.dry_run,
        "requirements": display_path(requirements),
        "venv": display_path(venv_dir),
        "directories": [],
        "commands": [],
        "ready_for_install": requirements.exists(),
    }

    for directory in REQUIRED_DIRS:
        status = safe_mkdir(directory, dry_run=args.dry_run)
        summary["directories"].append({"path": directory, "status": status})

    if not requirements.exists():
        summary["warnings"] = [f"requirements file not found: {display_path(requirements)}"]

    python_for_install = Path(sys.executable)
    if args.create_venv:
        summary["commands"].append(
            run_command([sys.executable, "-m", "venv", venv_dir.as_posix()], dry_run=args.dry_run, log_file=args.log_file)
        )
        python_for_install = venv_python(venv_dir)

    if args.install:
        summary["commands"].append(
            run_command(
                [python_for_install.as_posix(), "-m", "pip", "install", "--upgrade", "pip"],
                dry_run=args.dry_run,
                log_file=args.log_file,
            )
        )
        summary["commands"].append(
            run_command(
                [python_for_install.as_posix(), "-m", "pip", "install", "-r", requirements.as_posix()],
                dry_run=args.dry_run,
                log_file=args.log_file,
            )
        )

    if args.run_check_env:
        summary["commands"].append(
            run_command(
                [
                    python_for_install.as_posix(),
                    "scripts/check_env.py",
                    "--output",
                    "logs/env_check.json",
                    "--overwrite",
                ],
                dry_run=args.dry_run,
                log_file=args.log_file,
            )
        )

    failed = [item for item in summary["commands"] if item["status"] == "failed"]
    summary["status"] = "failed" if failed else "passed"
    target = write_json(args.output, summary, overwrite=args.overwrite)
    emit(f"wrote {display_path(target)}", log_file=args.log_file)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
