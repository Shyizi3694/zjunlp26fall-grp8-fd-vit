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


def selected_python_command(args: argparse.Namespace, venv_dir: Path, *, created_env: bool) -> list[str]:
    if args.env_backend == "conda":
        return [args.conda_executable, "run", "-n", args.conda_env, "python"]
    if created_env:
        return [venv_python(venv_dir).as_posix()]
    return [sys.executable]


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
    parser.add_argument("--env_backend", choices=["venv", "conda"], default="venv", help="environment backend to use")
    parser.add_argument("--venv", default=".venv", help="virtualenv directory")
    parser.add_argument("--conda_env", default="fd-vit", help="conda environment name when --env_backend conda")
    parser.add_argument("--conda_executable", default="conda", help="conda executable when --env_backend conda")
    parser.add_argument("--python_version", default=f"{sys.version_info.major}.{sys.version_info.minor}", help="Python version for conda env creation")
    parser.add_argument("--create_env", action="store_true", help="create the selected environment backend")
    parser.add_argument("--create_venv", action="store_true", help="legacy alias for --create_env with --env_backend venv")
    parser.add_argument("--install", action="store_true", help="install --requirements into the selected env or current env")
    parser.add_argument("--run_check_env", action="store_true", help="run scripts/check_env.py after preparation")
    parser.add_argument("--output", default="logs/environment_prepare.json", help="JSON summary path")
    parser.add_argument("--overwrite", action="store_true", help="overwrite --output if it already exists")
    parser.add_argument("--dry_run", action="store_true", help="show actions without creating env or installing packages")
    parser.add_argument("--log_file", default=None, help="optional text log path")
    args = parser.parse_args()
    if args.create_venv and args.env_backend != "venv":
        parser.error("--create_venv is only valid with --env_backend venv; use --create_env for conda")
    return args


def main() -> int:
    args = parse_args()
    requirements = repo_path(args.requirements)
    venv_dir = repo_path(args.venv)
    create_env = args.create_env or args.create_venv

    summary: dict[str, Any] = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "dry_run": args.dry_run,
        "env_backend": args.env_backend,
        "requirements": display_path(requirements),
        "venv": display_path(venv_dir),
        "conda_env": args.conda_env,
        "python_version": args.python_version,
        "directories": [],
        "commands": [],
        "ready_for_install": requirements.exists(),
    }

    for directory in REQUIRED_DIRS:
        status = safe_mkdir(directory, dry_run=args.dry_run)
        summary["directories"].append({"path": directory, "status": status})

    if not requirements.exists():
        summary["warnings"] = [f"requirements file not found: {display_path(requirements)}"]

    if create_env:
        if args.env_backend == "conda":
            summary["commands"].append(
                run_command(
                    [args.conda_executable, "create", "-y", "-n", args.conda_env, f"python={args.python_version}"],
                    dry_run=args.dry_run,
                    log_file=args.log_file,
                )
            )
        else:
            summary["commands"].append(
                run_command(
                    [sys.executable, "-m", "venv", venv_dir.as_posix()],
                    dry_run=args.dry_run,
                    log_file=args.log_file,
                )
            )

    python_for_install = selected_python_command(args, venv_dir, created_env=create_env)

    if args.install:
        summary["commands"].append(
            run_command(
                [*python_for_install, "-m", "pip", "install", "--upgrade", "pip"],
                dry_run=args.dry_run,
                log_file=args.log_file,
            )
        )
        summary["commands"].append(
            run_command(
                [*python_for_install, "-m", "pip", "install", "-r", requirements.as_posix()],
                dry_run=args.dry_run,
                log_file=args.log_file,
            )
        )

    if args.run_check_env:
        summary["commands"].append(
            run_command(
                [
                    *python_for_install,
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
