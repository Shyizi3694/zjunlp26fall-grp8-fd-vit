#!/usr/bin/env python3
"""Evaluate VQA predictions and write metrics/errors with full traceability."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit.evaluation import evaluate_records
from fdvit_prep_common import append_log, emit, repo_path, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, help="Input predictions JSONL")
    parser.add_argument("--output", required=True, help="Output metrics JSON")
    parser.add_argument("--error_output", required=True, help="Error sample JSONL output")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs if already exist")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (recorded only)")
    parser.add_argument("--log_file", default=None, help="Optional log file path")
    return parser.parse_args()


def _read_predictions(path: str | Path) -> list[dict]:
    target = repo_path(path)
    if not target.exists():
        raise FileNotFoundError(f"predictions not found: {target}")
    content = target.read_text(encoding="utf-8").strip()
    if not content:
        return []

    records = []
    if content[0] == "[":
        payload = json.loads(content)
        if not isinstance(payload, list):
            raise ValueError("predictions JSON must be a list")
        records = [row for row in payload if isinstance(row, dict)]
    else:
        for line_no, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"line {line_no}: parse error: {exc}") from exc
            if isinstance(obj, dict):
                records.append(obj)
    return records


def main() -> int:
    args = parse_args()
    try:
        rows = _read_predictions(args.predictions)
        report = evaluate_records(rows)
        report["seed"] = args.seed

        if rows:
            first = rows[0]
            for key in ("experiment_id", "model_id", "checkpoint", "dataset", "split", "generation_config"):
                if key in first and key not in report:
                    report[key] = first[key]
        if "created_at" not in report:
            report["created_at"] = utc_now()

        output_path = repo_path(args.output)
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing metrics file: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({k: v for k, v in report.items() if k != "errors"}, indent=2, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )

        error_path = repo_path(args.error_output)
        if error_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing error file: {error_path}")
        error_path.parent.mkdir(parents=True, exist_ok=True)
        with error_path.open("w", encoding="utf-8") as handle:
            for row in report["errors"]:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

        emit(
            f"evaluated {len(rows)} samples; "
            f"acc_any={report['acc_any']:.4f}; acc_soft={report['acc_soft']:.4f}",
            log_file=args.log_file,
        )
        append_log(args.log_file, json.dumps({"num_samples": len(rows), "output": str(output_path)}))
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
