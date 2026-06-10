#!/usr/bin/env python3
"""Summarize experiment metrics into report-ready CSV and Markdown tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from fdvit_prep_common import append_log, emit, repo_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exp_dirs",
        nargs="+",
        default=None,
        help="One or more experiment output directories, e.g. outputs/E00_zero_shot_basic",
    )
    parser.add_argument(
        "--outputs",
        default=None,
        help="Outputs root directory (backward-compatible fallback; scans **/metrics.json under this root)",
    )
    parser.add_argument("--output_csv", required=True, help="CSV output path")
    parser.add_argument("--output_md", required=True, help="Markdown output path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
    args = parser.parse_args()
    if not args.exp_dirs and not args.outputs:
        parser.error("one of --exp_dirs or --outputs is required")
    return args


def exp_sort_key(exp_id: str) -> tuple[int, str]:
    match = re.match(r"E(\d+)", exp_id)
    if match:
        return int(match.group(1)), exp_id
    return 9999, exp_id


def infer_setting(exp_id: str) -> tuple[str, str, str]:
    lower = exp_id.lower()
    if "zero_shot" in lower:
        return "Zero-shot", "-", "-"
    if "prompt" in lower:
        return "Prompt-only", "-", "-"
    if "random" in lower:
        return "LoRA-random", "random", "8"
    if "failure" in lower:
        return "LoRA-failure", "failure", "8"
    return exp_id, "-", "-"


def infer_train_n(exp_id: str, metrics: dict[str, Any]) -> str:
    match = re.search(r"_(\d+)k", exp_id.lower())
    if match:
        return str(int(match.group(1)) * 1000)
    return "0"


def _iter_metrics_paths(*, exp_dirs: list[str] | None, outputs_root: str | None) -> list[Path]:
    metrics_paths: list[Path] = []
    seen: set[Path] = set()

    if exp_dirs:
        for raw_dir in exp_dirs:
            exp_dir = repo_path(raw_dir)
            metrics_path = exp_dir / "metrics.json"
            if not metrics_path.exists():
                raise FileNotFoundError(f"metrics not found for exp dir: {exp_dir}")
            resolved = metrics_path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                metrics_paths.append(metrics_path)
        return metrics_paths

    if outputs_root:
        root = repo_path(outputs_root)
        for metrics_path in sorted(root.glob("**/metrics.json")):
            resolved = metrics_path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                metrics_paths.append(metrics_path)
    return metrics_paths


def load_metrics(*, exp_dirs: list[str] | None, outputs_root: str | None) -> list[dict[str, Any]]:
    rows = []
    for metrics_path in _iter_metrics_paths(exp_dirs=exp_dirs, outputs_root=outputs_root):
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        exp_id = str(payload.get("experiment_id") or metrics_path.parent.name)
        setting, sampling, lora_r = infer_setting(exp_id)
        rows.append(
            {
                "exp_id": exp_id,
                "setting": setting,
                "train_n": infer_train_n(exp_id, payload),
                "sampling": sampling,
                "lora_r": lora_r,
                "acc_any": float(payload.get("acc_any", 0.0)),
                "acc_soft": float(payload.get("acc_soft", 0.0)),
                "format_error_rate": float(payload.get("format_error_rate", 0.0)),
                "num_samples": int(payload.get("num_samples", 0)),
                "metrics_path": str(metrics_path),
            }
        )
    rows.sort(key=lambda row: exp_sort_key(row["exp_id"]))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "exp_id",
        "setting",
        "train_n",
        "sampling",
        "lora_r",
        "acc_any",
        "acc_soft",
        "format_error_rate",
        "delta_acc_soft_vs_E00",
        "delta_acc_soft_vs_E02",
        "num_samples",
        "metrics_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_md(path: Path, rows: list[dict[str, Any]], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| Exp | Setting | Train n | Sampling | LoRA r | acc_any | acc_soft | format_error_rate | Δacc_soft vs E00 | Δacc_soft vs E02 |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['exp_id']} | {row['setting']} | {row['train_n']} | {row['sampling']} | "
            f"{row['lora_r']} | {row['acc_any']:.4f} | {row['acc_soft']:.4f} | "
            f"{row['format_error_rate']:.4f} | {row['delta_acc_soft_vs_E00']:.4f} | "
            f"{row['delta_acc_soft_vs_E02']:.4f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        rows = load_metrics(exp_dirs=args.exp_dirs, outputs_root=args.outputs)
        zero_soft = next((row["acc_soft"] for row in rows if row["exp_id"].startswith("E00")), 0.0)
        random_soft = next((row["acc_soft"] for row in rows if row["exp_id"].startswith("E02")), 0.0)
        for row in rows:
            row["delta_acc_soft_vs_E00"] = row["acc_soft"] - zero_soft
            row["delta_acc_soft_vs_E02"] = row["acc_soft"] - random_soft

        write_csv(repo_path(args.output_csv), rows, overwrite=args.overwrite)
        write_md(repo_path(args.output_md), rows, overwrite=args.overwrite)
        emit(f"wrote {len(rows)} summarized rows", log_file=args.log_file)
        append_log(
            args.log_file,
            json.dumps(
                {
                    "rows": len(rows),
                    "exp_dirs": args.exp_dirs,
                    "outputs": args.outputs,
                    "output_csv": args.output_csv,
                    "output_md": args.output_md,
                }
            ),
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
