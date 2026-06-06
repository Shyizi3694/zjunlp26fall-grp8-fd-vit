#!/usr/bin/env python3
"""Prepare or validate the Qwen3-VL base model for FD-VIT."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, display_path, emit, repo_path, utc_now, write_json


DEFAULT_MODEL_ID = "Qwen/Qwen3-VL-4B-Instruct"
DEFAULT_FALLBACK_MODEL_ID = "Qwen/Qwen3-VL-2B-Instruct"

REQUIRED_CONFIG_FILES = ["config.json", "tokenizer_config.json"]
OPTIONAL_CONFIG_FILES = [
    "generation_config.json",
    "preprocessor_config.json",
    "processor_config.json",
    "chat_template.json",
]


def default_model_dir(model_id: str) -> str:
    return f"models/{model_id.split('/')[-1]}"


def inspect_model_dir(model_dir: Path) -> dict[str, Any]:
    config_files = {}
    for name in REQUIRED_CONFIG_FILES + OPTIONAL_CONFIG_FILES:
        path = model_dir / name
        config_files[name] = {"exists": path.exists(), "path": display_path(path)}

    safetensors = sorted(model_dir.glob("*.safetensors"))
    index_files = sorted(model_dir.glob("*.safetensors.index.json"))
    shard_files = sorted(model_dir.glob("model-*.safetensors"))
    return {
        "path": display_path(model_dir),
        "exists": model_dir.exists(),
        "config_files": config_files,
        "safetensors_count": len(safetensors),
        "index_files": [display_path(path) for path in index_files],
        "shard_files_sample": [display_path(path) for path in shard_files[:5]],
        "has_weights": bool(safetensors or index_files or shard_files),
        "ready_for_transformers": all(config_files[name]["exists"] for name in REQUIRED_CONFIG_FILES)
        and bool(safetensors or index_files or shard_files),
    }


def download_model(
    *,
    model_id: str,
    revision: str,
    model_dir: Path,
    local_files_only: bool,
    token_env: str,
    dry_run: bool,
    log_file: str | None,
) -> dict[str, Any]:
    if dry_run:
        return {
            "model_id": model_id,
            "revision": revision,
            "local_dir": display_path(model_dir),
            "status": "planned",
        }
    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:  # noqa: BLE001
        return {
            "model_id": model_id,
            "revision": revision,
            "local_dir": display_path(model_dir),
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }

    token = os.environ.get(token_env) if token_env else None
    emit(f"downloading {model_id} to {display_path(model_dir)}", log_file=log_file)
    try:
        path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=model_dir.as_posix(),
            token=token,
            local_files_only=local_files_only,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "model_id": model_id,
            "revision": revision,
            "local_dir": display_path(model_dir),
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {
        "model_id": model_id,
        "revision": revision,
        "local_dir": display_path(model_dir),
        "snapshot_path": path,
        "status": "downloaded" if not local_files_only else "resolved_local_files",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model_id", default=DEFAULT_MODEL_ID, help="Hugging Face model id")
    parser.add_argument("--fallback_model_id", default=DEFAULT_FALLBACK_MODEL_ID, help="low-VRAM fallback model id")
    parser.add_argument("--use_fallback", action="store_true", help="use --fallback_model_id instead of --model_id")
    parser.add_argument("--model_dir", default=None, help="local model directory; default derives from model id")
    parser.add_argument("--revision", default="main", help="model revision")
    parser.add_argument("--download", action="store_true", help="download or resolve model files with huggingface_hub")
    parser.add_argument("--local_files_only", action="store_true", help="do not access network when resolving model files")
    parser.add_argument("--token_env", default="HF_TOKEN", help="environment variable containing Hugging Face token")
    parser.add_argument("--output", default="logs/model_prepare.json", help="JSON summary path")
    parser.add_argument("--overwrite", action="store_true", help="overwrite --output if it already exists")
    parser.add_argument("--dry_run", action="store_true", help="show actions without downloading")
    parser.add_argument("--log_file", default=None, help="optional text log path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_id = args.fallback_model_id if args.use_fallback else args.model_id
    model_dir = repo_path(args.model_dir or default_model_dir(model_id))

    summary: dict[str, Any] = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "dry_run": args.dry_run,
        "model_id": model_id,
        "revision": args.revision,
        "model_dir": display_path(model_dir),
        "download": None,
    }

    if args.download:
        summary["download"] = download_model(
            model_id=model_id,
            revision=args.revision,
            model_dir=model_dir,
            local_files_only=args.local_files_only,
            token_env=args.token_env,
            dry_run=args.dry_run,
            log_file=args.log_file,
        )

    summary["inspection"] = inspect_model_dir(model_dir)
    summary["ready_for_baseline"] = bool(summary["inspection"]["ready_for_transformers"])
    summary["status"] = "passed" if summary["ready_for_baseline"] else "needs_model"
    if summary["download"] and summary["download"]["status"] == "failed":
        summary["status"] = "failed"

    target = write_json(args.output, summary, overwrite=args.overwrite)
    emit(f"wrote {display_path(target)}", log_file=args.log_file)
    if summary["status"] != "passed":
        emit("model is not ready yet; inspect the JSON summary for missing files", log_file=args.log_file)
    return 1 if summary["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
