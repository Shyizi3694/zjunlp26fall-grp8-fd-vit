#!/usr/bin/env python3
"""Validate random/failure-driven train subsets and optional Qwen-formatted output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from fdvit_prep_common import append_log, emit, repo_path, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Subset JSONL/JSON input")
    parser.add_argument("--qwen_input", default=None, help="Optional Qwen JSON input to cross-check")
    parser.add_argument("--output", required=True, help="Validation summary JSON output")
    parser.add_argument("--check_images", action="store_true", help="Check that image paths exist")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
    return parser.parse_args()


def read_json_like(path: str | Path) -> list[dict[str, Any]]:
    target = repo_path(path)
    raw = target.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw[0] == "[":
        payload = json.loads(raw)
        return [row for row in payload if isinstance(row, dict)]
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> int:
    args = parse_args()
    try:
        rows = read_json_like(args.input)
        sample_ids = []
        split_ok = True
        metadata_ok = True
        missing_images = []
        for row in rows:
            sample_ids.append(str(row.get("sample_id", "")))
            split_ok = split_ok and row.get("split") == "train"
            metadata = row.get("metadata")
            metadata_ok = metadata_ok and isinstance(metadata, dict) and metadata.get("sampling_strategy") in {"random", "failure_driven"}
            if args.check_images:
                image_path = row.get("image_path")
                if isinstance(image_path, str) and not repo_path(image_path).exists():
                    missing_images.append(image_path)

        qwen_summary: dict[str, Any] | None = None
        if args.qwen_input:
            qwen_rows = read_json_like(args.qwen_input)
            qwen_summary = {
                "num_rows": len(qwen_rows),
                "all_have_image": all(isinstance(row.get("image"), str) and row.get("image") for row in qwen_rows),
                "all_have_conversations": all(isinstance(row.get("conversations"), list) and len(row.get("conversations", [])) >= 2 for row in qwen_rows),
            }

        summary = {
            "num_rows": len(rows),
            "unique_sample_ids": len(set(sample_ids)),
            "duplicate_sample_ids": len(sample_ids) - len(set(sample_ids)),
            "all_train_split": split_ok,
            "metadata_ok": metadata_ok,
            "missing_images": missing_images,
            "qwen_summary": qwen_summary,
            "status": "passed" if len(sample_ids) == len(set(sample_ids)) and split_ok and metadata_ok and not missing_images else "failed",
        }
        write_json(args.output, summary, overwrite=args.overwrite)
        emit(f"validated {len(rows)} subset rows: status={summary['status']}", log_file=args.log_file)
        append_log(args.log_file, json.dumps(summary, ensure_ascii=False))
        return 0 if summary["status"] == "passed" else 1
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
