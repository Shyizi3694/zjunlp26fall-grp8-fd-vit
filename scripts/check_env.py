#!/usr/bin/env python3
"""Inspect the local FD-VIT Python/CUDA environment."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, display_path, emit, utc_now, write_json


MODULES = [
    "torch",
    "torchvision",
    "transformers",
    "accelerate",
    "peft",
    "bitsandbytes",
    "qwen_vl_utils",
    "huggingface_hub",
    "datasets",
    "PIL",
    "yaml",
    "jsonschema",
]

DIST_NAMES = {
    "PIL": "Pillow",
    "yaml": "PyYAML",
    "qwen_vl_utils": "qwen-vl-utils",
    "huggingface_hub": "huggingface-hub",
}


def module_status(name: str) -> dict[str, Any]:
    result: dict[str, Any] = {"available": False, "version": None, "error": None}
    try:
        module = importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001 - environment probe must not fail hard.
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result
    result["available"] = True
    try:
        result["version"] = package_version(DIST_NAMES.get(name, name))
    except PackageNotFoundError:
        result["version"] = getattr(module, "__version__", None)
    return result


def collect_torch_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "available": False,
        "version": None,
        "cuda_available": False,
        "cuda_version": None,
        "device_count": 0,
        "devices": [],
        "error": None,
    }
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"{type(exc).__name__}: {exc}"
        return info

    info["available"] = True
    info["version"] = getattr(torch, "__version__", None)
    info["cuda_available"] = bool(torch.cuda.is_available())
    info["cuda_version"] = getattr(torch.version, "cuda", None)
    if not info["cuda_available"]:
        return info

    try:
        info["device_count"] = torch.cuda.device_count()
        for index in range(info["device_count"]):
            props = torch.cuda.get_device_properties(index)
            info["devices"].append(
                {
                    "index": index,
                    "name": props.name,
                    "total_memory_gb": round(props.total_memory / (1024**3), 2),
                    "major": props.major,
                    "minor": props.minor,
                }
            )
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


def collect_nvidia_smi() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader",
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=10)
    except FileNotFoundError:
        return {"available": False, "error": "nvidia-smi not found", "gpus": []}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"{type(exc).__name__}: {exc}", "gpus": []}
    if completed.returncode != 0:
        return {"available": False, "error": completed.stderr.strip(), "gpus": []}
    gpus = []
    for line in completed.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) >= 3:
            gpus.append({"name": parts[0], "memory_total": parts[1], "driver_version": parts[2]})
    return {"available": True, "error": None, "gpus": gpus}


def build_report() -> dict[str, Any]:
    modules = {name: module_status(name) for name in MODULES}
    return {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "working_directory": Path.cwd().as_posix(),
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "implementation": platform.python_implementation(),
        },
        "os": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "torch": collect_torch_info(),
        "nvidia_smi": collect_nvidia_smi(),
        "modules": modules,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=None, help="optional JSON output path, e.g. logs/env_check.json")
    parser.add_argument("--overwrite", action="store_true", help="overwrite --output if it already exists")
    parser.add_argument("--log_file", default=None, help="optional text log path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.output:
        target = write_json(args.output, report, overwrite=args.overwrite)
        emit(f"wrote {display_path(target)}", log_file=args.log_file)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
