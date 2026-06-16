#!/usr/bin/env python3
"""Paired bootstrap and randomization tests for VQA prediction files."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit.evaluation import normalize_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pairs",
        nargs=3,
        action="append",
        metavar=("NAME", "BASELINE", "TREATMENT"),
        required=True,
        help="Comparison name and two prediction JSONL files.",
    )
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--output_md", required=True)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    rows: list[dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"{target}:{line_no}: {exc}") from exc
            if isinstance(row, dict):
                rows.append(row)
    return rows


def record_key(row: dict[str, Any]) -> str:
    for key in ("sample_id", "question_id"):
        value = row.get(key)
        if value is not None:
            return f"{key}:{value}"
    raise ValueError("record missing sample_id/question_id")


def score_record(row: dict[str, Any]) -> tuple[float, float]:
    pred = normalize_answer(row.get("prediction", row.get("prediction_raw", "")))
    answers = row.get("answers", [])
    if not isinstance(answers, list):
        answers = []
    gt = [normalize_answer(a) for a in answers if isinstance(a, str)]
    gt = [a for a in gt if a]
    if not gt:
        return 0.0, 0.0
    acc_any = 1.0 if pred in gt else 0.0
    acc_soft = min(gt.count(pred) / 3.0, 1.0)
    return acc_any, acc_soft


def align_scores(base_path: str, treatment_path: str) -> dict[str, list[float]]:
    base_rows = {record_key(row): row for row in read_jsonl(base_path)}
    treatment_rows = {record_key(row): row for row in read_jsonl(treatment_path)}
    keys = sorted(set(base_rows) & set(treatment_rows))
    if not keys:
        raise ValueError(f"no overlapping samples: {base_path} vs {treatment_path}")

    base_any: list[float] = []
    treatment_any: list[float] = []
    base_soft: list[float] = []
    treatment_soft: list[float] = []
    for key in keys:
        b_any, b_soft = score_record(base_rows[key])
        t_any, t_soft = score_record(treatment_rows[key])
        base_any.append(b_any)
        treatment_any.append(t_any)
        base_soft.append(b_soft)
        treatment_soft.append(t_soft)
    return {
        "base_any": base_any,
        "treatment_any": treatment_any,
        "base_soft": base_soft,
        "treatment_soft": treatment_soft,
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    pos = (len(sorted_values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def paired_randomization_pvalue(deltas: list[float], observed: float, *, rng: random.Random, n: int) -> float:
    if not deltas:
        return 1.0
    if observed == 0:
        return 1.0
    hits = 0
    threshold = abs(observed)
    for _ in range(n):
        signed = [delta if rng.random() < 0.5 else -delta for delta in deltas]
        if abs(mean(signed)) >= threshold:
            hits += 1
    return (hits + 1) / (n + 1)


def summarize_metric(
    name: str,
    base_values: list[float],
    treatment_values: list[float],
    *,
    rng: random.Random,
    bootstrap_n: int,
    permutation_n: int,
) -> dict[str, Any]:
    deltas = [t - b for b, t in zip(base_values, treatment_values, strict=True)]
    observed = mean(deltas)
    boot: list[float] = []
    sample_n = len(deltas)
    for _ in range(bootstrap_n):
        indices = [rng.randrange(sample_n) for _ in range(sample_n)]
        boot.append(mean([deltas[i] for i in indices]))
    boot.sort()
    wins = sum(1 for delta in deltas if delta > 0)
    losses = sum(1 for delta in deltas if delta < 0)
    ties = sample_n - wins - losses
    return {
        "metric": name,
        "n": sample_n,
        "baseline_mean": mean(base_values),
        "treatment_mean": mean(treatment_values),
        "diff_treatment_minus_baseline": observed,
        "bootstrap_ci_low": percentile(boot, 0.025),
        "bootstrap_ci_high": percentile(boot, 0.975),
        "paired_randomization_p": paired_randomization_pvalue(
            deltas,
            observed,
            rng=rng,
            n=permutation_n,
        ),
        "wins": wins,
        "losses": losses,
        "ties": ties,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "comparison",
        "metric",
        "n",
        "baseline_mean",
        "treatment_mean",
        "diff_treatment_minus_baseline",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "paired_randomization_p",
        "wins",
        "losses",
        "ties",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_md(path: Path, rows: list[dict[str, Any]], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Paired Significance Analysis",
        "",
        "| Comparison | Metric | n | Baseline | Treatment | Diff | 95% bootstrap CI | p | Wins/Losses/Ties |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['comparison']} | {row['metric']} | {row['n']} | "
            f"{row['baseline_mean']:.4f} | {row['treatment_mean']:.4f} | "
            f"{row['diff_treatment_minus_baseline']:+.4f} | "
            f"[{row['bootstrap_ci_low']:+.4f}, {row['bootstrap_ci_high']:+.4f}] | "
            f"{row['paired_randomization_p']:.4f} | "
            f"{row['wins']}/{row['losses']}/{row['ties']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)
    rows: list[dict[str, Any]] = []
    for comparison, baseline, treatment in args.pairs:
        scores = align_scores(baseline, treatment)
        for metric, base_key, treatment_key in [
            ("acc_any", "base_any", "treatment_any"),
            ("acc_soft", "base_soft", "treatment_soft"),
        ]:
            row = summarize_metric(
                metric,
                scores[base_key],
                scores[treatment_key],
                rng=rng,
                bootstrap_n=args.bootstrap,
                permutation_n=args.permutations,
            )
            row["comparison"] = comparison
            rows.append(row)

    write_csv(Path(args.output_csv), rows, overwrite=args.overwrite)
    write_md(Path(args.output_md), rows, overwrite=args.overwrite)
    print(f"wrote {len(rows)} paired significance rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

