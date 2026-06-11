#!/usr/bin/env python3
"""Evaluate optional GUI grounding predictions."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit.gui_grounding import evaluate_gui_record
from fdvit_prep_common import append_log, display_path, emit, repo_path, utc_now, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, help="GUI predictions JSONL/JSON")
    parser.add_argument("--output", required=True, help="Output metrics JSON")
    parser.add_argument("--error_output", default=None, help="Optional JSONL for parse failures or misses")
    parser.add_argument(
        "--coordinate_mode",
        choices=["auto", "pixel", "normalized", "qwen_1000"],
        default="auto",
        help="How to convert parsed coordinates before scoring",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs if they exist")
    parser.add_argument("--seed", type=int, default=42, help="Recorded for traceability")
    parser.add_argument("--log_file", default=None, help="Optional text log")
    return parser.parse_args()


def read_json_like(path: str | Path) -> list[dict[str, Any]]:
    target = repo_path(path)
    if not target.exists():
        raise FileNotFoundError(f"input not found: {display_path(target)}")
    raw = target.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw[0] == "[":
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("input JSON must be a list")
        return [row for row in payload if isinstance(row, dict)]

    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"line {line_no}: parse error: {exc}") from exc
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def summarize_by_control(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get("control_type") or "unknown")].append(record)
    summary = {}
    for control_type, rows in sorted(grouped.items()):
        total = len(rows)
        parsed = sum(1 for row in rows if row.get("parse_success"))
        hits = sum(1 for row in rows if row.get("point_in_bbox"))
        distances = [
            float(row["center_distance_norm"])
            for row in rows
            if isinstance(row.get("center_distance_norm"), (int, float))
        ]
        summary[control_type] = {
            "num_samples": total,
            "parse_success_rate": _rate(parsed, total),
            "point_in_bbox_acc": _rate(hits, total),
            "center_distance_norm": _mean(distances),
        }
    return summary


def write_jsonl(path: str | Path, rows: list[dict[str, Any]], *, overwrite: bool) -> None:
    target = repo_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    try:
        rows = read_json_like(args.predictions)
        evaluated: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        distances: list[float] = []
        parse_sources: Counter[str] = Counter()
        parse_modes: Counter[str] = Counter()

        for row in rows:
            result = evaluate_gui_record(row, coordinate_mode=args.coordinate_mode)
            enriched = {**row, **result}
            evaluated.append(enriched)
            parse_sources[str(result.get("parse_source") or "unknown")] += 1
            parse_modes[str(result.get("parse_mode") or "unknown")] += 1
            if isinstance(result.get("center_distance_norm"), (int, float)):
                distances.append(float(result["center_distance_norm"]))
            if not result.get("parse_success") or not result.get("point_in_bbox"):
                errors.append(enriched)

        total = len(evaluated)
        parse_success = sum(1 for row in evaluated if row.get("parse_success"))
        hits = sum(1 for row in evaluated if row.get("point_in_bbox"))
        inference_errors = sum(1 for row in evaluated if row.get("error"))
        first = evaluated[0] if evaluated else {}
        metrics = {
            "experiment_id": first.get("experiment_id", "B01_gui_grounding_demo"),
            "dataset": first.get("dataset", "screenspot_pro"),
            "split": first.get("split", "val"),
            "num_samples": total,
            "num_valid_predictions": total - inference_errors,
            "parse_success_count": parse_success,
            "parse_success_rate": _rate(parse_success, total),
            "point_in_bbox_count": hits,
            "point_in_bbox_acc": _rate(hits, total),
            "point_in_bbox_acc_parsed": _rate(hits, parse_success),
            "center_distance_norm": _mean(distances),
            "center_distance_norm_median": sorted(distances)[len(distances) // 2] if distances else None,
            "inference_error_rate": _rate(inference_errors, total),
            "control_type_metrics": summarize_by_control(evaluated),
            "parse_sources": dict(parse_sources),
            "parse_modes": dict(parse_modes),
            "coordinate_mode": args.coordinate_mode,
            "seed": args.seed,
            "created_at": utc_now(),
        }
        write_json(args.output, metrics, overwrite=args.overwrite)

        if args.error_output:
            write_jsonl(args.error_output, errors, overwrite=args.overwrite)

        emit(
            f"evaluated {total} GUI samples; point_in_bbox_acc={metrics['point_in_bbox_acc']:.4f}; "
            f"parse_success_rate={metrics['parse_success_rate']:.4f}",
            log_file=args.log_file,
        )
        append_log(args.log_file, json.dumps({"output": display_path(args.output), "errors": len(errors)}))
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {type(exc).__name__}: {exc}")
        append_log(args.log_file, f"ERROR: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
