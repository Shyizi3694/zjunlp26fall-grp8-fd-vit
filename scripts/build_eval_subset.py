#!/usr/bin/env python3
"""Build deterministic evaluation subsets for FD-VIT (e.g., val_1k)."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, append_log, display_path, emit, repo_path, utc_now, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input JSONL/JSON processed dataset file")
    parser.add_argument("--split", default="val", choices=["train", "val", "test"], help="Split to sample from")
    parser.add_argument("--size", type=int, default=1000, help="Subset size")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSONL path (default: data/processed/okvqa/{split}_1k.jsonl)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file")
    parser.add_argument("--dry_run", action="store_true", help="Show actions without writing files")
    parser.add_argument("--log_file", default=None, help="Optional log file path")
    return parser.parse_args()


def _read_records(path: Path) -> list[dict[str, Any]]:
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    records: list[dict[str, Any]] = []
    if content[0] == "[":
        payload = json.loads(content)
        if not isinstance(payload, list):
            raise ValueError("input JSON payload must be a list")
        for item in payload:
            if isinstance(item, dict):
                records.append(item)
        return records

    for line_no, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"line {line_no}: failed to parse json: {exc}") from exc
        if isinstance(obj, dict):
            records.append(obj)
    return records


def _write_records(path: Path, rows: list[dict[str, Any]], *, dry_run: bool, overwrite: bool) -> None:
    if dry_run:
        emit(f"[dry_run] would write {len(rows)} rows to {display_path(path)}", log_file=None)
        return
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {display_path(path)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    input_path = repo_path(args.input)
    if not input_path.exists():
        emit(f"input not found: {display_path(input_path)}")
        return 1

    split = args.split
    output_path = (
        Path(args.output).expanduser()
        if args.output
        else Path(input_path.parent) / f"{split}_1k.jsonl"
    )
    output_path = repo_path(output_path)

    rows = _read_records(input_path)
    subset = [row for row in rows if row.get("split") == split]
    if not subset:
        emit(f"no rows found for split={split} in {display_path(input_path)}")
        return 1

    rng = random.Random(args.seed)
    rng.shuffle(subset)
    target = min(max(args.size, 0), len(subset))
    sampled = subset[:target]

    summary = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "input": display_path(input_path),
        "split": split,
        "seed": args.seed,
        "requested_size": args.size,
        "actual_size": len(sampled),
        "available_size": len(subset),
        "dry_run": args.dry_run,
        "output": display_path(output_path),
    }
    write_json(
        output_path.with_suffix(".summary.json"),
        summary,
        overwrite=True,
    )
    append_log(args.log_file, f"wrote {summary}")
    _write_records(output_path, sampled, dry_run=args.dry_run, overwrite=args.overwrite)
    emit(f"sampled {len(sampled)} rows from {display_path(input_path)} -> {display_path(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
