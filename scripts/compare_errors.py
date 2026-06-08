#!/usr/bin/env python3
"""Compare error type counts across experiment directories."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "scripts") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mine_failures import detect_error_type
from fdvit_prep_common import append_log, emit, repo_path

ERROR_TYPES = [
    "answer_format",
    "counting",
    "ocr_text",
    "spatial",
    "attribute",
    "commonsense",
    "hallucination",
    "ambiguous",
    "other",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp_dirs", nargs="+", required=True, help="Experiment output directories")
    parser.add_argument("--output_csv", required=True, help="CSV output path")
    parser.add_argument("--output_md", required=True, help="Markdown output path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def load_error_rows(exp_dir: Path) -> tuple[str, dict[str, int]]:
    exp_id = exp_dir.name
    failure_path = exp_dir / "failures_mined.jsonl"
    error_path = exp_dir / "errors.jsonl"
    counts = {key: 0 for key in ERROR_TYPES}

    rows: list[dict]
    if failure_path.exists():
        rows = read_jsonl(failure_path)
        for row in rows:
            key = str(row.get("error_type_manual") or row.get("error_type_auto") or "other")
            counts[key] = counts.get(key, 0) + 1
    elif error_path.exists():
        rows = read_jsonl(error_path)
        for row in rows:
            key = detect_error_type(row)
            counts[key] = counts.get(key, 0) + 1
    else:
        rows = []
    if rows and isinstance(rows[0], dict) and rows[0].get("source_experiment"):
        exp_id = str(rows[0]["source_experiment"])
    return exp_id, counts


def canonical_col(exp_id: str) -> str:
    if exp_id.startswith("E00"):
        return "E00_errors"
    if exp_id.startswith("E01"):
        return "E01_errors"
    if exp_id.startswith("E02"):
        return "E02_errors"
    if exp_id.startswith("E03"):
        return "E03_errors"
    return f"{exp_id}_errors"


def build_observation(row: dict[str, Any]) -> str:
    if "E03_errors" in row and "E02_errors" in row:
        delta = int(row["E03_errors"]) - int(row["E02_errors"])
        if delta < 0:
            return "improved vs random"
        if delta > 0:
            return "worse vs random"
        return "unchanged vs random"
    return ""


def main() -> int:
    args = parse_args()
    try:
        experiments = []
        for exp_dir in args.exp_dirs:
            exp_id, counts = load_error_rows(repo_path(exp_dir))
            experiments.append((exp_id, counts))

        ordered = [(exp_id, canonical_col(exp_id), counts) for exp_id, counts in experiments]
        headers = ["error_type"] + [col for _, col, _ in ordered]
        if any(exp_id.startswith("E03") for exp_id, _, _ in ordered) and any(exp_id.startswith("E02") for exp_id, _, _ in ordered):
            headers.extend(["E03_minus_E02", "observation"])

        csv_path = repo_path(args.output_csv)
        if csv_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {csv_path}")
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            for error_type in ERROR_TYPES:
                row = {"error_type": error_type}
                for exp_id, col, counts in ordered:
                    row[col] = counts.get(error_type, 0)
                if "E03_minus_E02" in headers:
                    e03 = next(counts.get(error_type, 0) for exp_id, _, counts in ordered if exp_id.startswith("E03"))
                    e02 = next(counts.get(error_type, 0) for exp_id, _, counts in ordered if exp_id.startswith("E02"))
                    row["E03_minus_E02"] = e03 - e02
                    row["observation"] = build_observation(row)
                writer.writerow(row)

        md_path = repo_path(args.output_md)
        if md_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {md_path}")
        lines = [
            "| " + " | ".join(headers) + " |",
            "|" + "|".join(["---"] * len(headers)) + "|",
        ]
        with csv_path.open("r", encoding="utf-8") as handle:
            next(handle)
            for line in handle:
                values = line.rstrip("\n").split(",")
                lines.append("| " + " | ".join(values) + " |")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        emit(f"wrote error comparison for {len(experiments)} experiments", log_file=args.log_file)
        append_log(args.log_file, json.dumps({"experiments": [x[0] for x in experiments], "output_csv": args.output_csv}))
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
