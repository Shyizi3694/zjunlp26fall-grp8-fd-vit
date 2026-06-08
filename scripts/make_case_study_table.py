#!/usr/bin/env python3
"""Build qualitative case study markdown from multiple experiment prediction files."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
if str(Path(__file__).resolve().parents[1] / "scripts") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from fdvit.evaluation import normalize_answer
from fdvit_prep_common import append_log, emit, repo_path
from mine_failures import detect_error_type


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp_dirs", nargs="+", required=True, help="Experiment output directories")
    parser.add_argument("--output", required=True, help="Markdown output path")
    parser.add_argument("--num_cases", type=int, default=10, help="Number of cases to export")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def is_correct(row: dict[str, Any]) -> bool:
    pred = normalize_answer(str(row.get("prediction") or row.get("prediction_raw") or ""))
    answers = [normalize_answer(a) for a in row.get("answers", []) if isinstance(a, str)]
    return bool(answers and pred in answers)


def prediction_text(row: dict[str, Any]) -> str:
    return str(row.get("prediction") or row.get("prediction_raw") or "")


def main() -> int:
    args = parse_args()
    try:
        experiments = {}
        for exp_dir in args.exp_dirs:
            pred_path = repo_path(exp_dir) / "predictions.jsonl"
            if pred_path.exists():
                experiments[Path(exp_dir).name] = {row["sample_id"]: row for row in read_jsonl(pred_path)}

        common_ids = None
        for rows in experiments.values():
            ids = set(rows.keys())
            common_ids = ids if common_ids is None else common_ids & ids
        common_ids = sorted(common_ids or [])

        scored = []
        for sample_id in common_ids:
            rows = {name: exp_rows[sample_id] for name, exp_rows in experiments.items()}
            correctness = {name: is_correct(row) for name, row in rows.items()}
            score = sum(1 for value in correctness.values() if value)
            scored.append((sample_id, score, rows, correctness))

        preferred = []
        for item in scored:
            _, _, rows, correctness = item
            e00_ok = next((ok for name, ok in correctness.items() if name.startswith("E00")), False)
            e02_ok = next((ok for name, ok in correctness.items() if name.startswith("E02")), False)
            e03_ok = next((ok for name, ok in correctness.items() if name.startswith("E03")), False)
            if e03_ok and not e02_ok:
                preferred.append((0, item))
            elif not e03_ok:
                preferred.append((1, item))
            elif e03_ok and not e00_ok:
                preferred.append((2, item))
            else:
                preferred.append((3, item))

        rng = random.Random(args.seed)
        rng.shuffle(preferred)
        preferred.sort(key=lambda x: x[0])
        chosen = [item for _, item in preferred[: args.num_cases]]

        lines = [
            "# Case Studies",
            "",
            "| Case | image_path | question | GT answers | " + " | ".join(experiments.keys()) + " | Error Type | Note |",
            "|---|---|---|---|" + "|".join(["---"] * len(experiments)) + "|---|---|",
        ]
        for idx, (_, _, rows, correctness) in enumerate(chosen, start=1):
            any_row = next(iter(rows.values()))
            preds = []
            for name in experiments.keys():
                row = rows[name]
                pred_text = prediction_text(row).replace("|", "\\|")
                suffix = " (correct)" if correctness[name] else ""
                preds.append(pred_text + suffix)
            error_type = detect_error_type(any_row)
            e00_ok = next((ok for name, ok in correctness.items() if name.startswith("E00")), False)
            e02_ok = next((ok for name, ok in correctness.items() if name.startswith("E02")), False)
            e03_ok = next((ok for name, ok in correctness.items() if name.startswith("E03")), False)
            if e03_ok and not e02_ok:
                note = "failure-driven fixes an error that random LoRA misses"
            elif e03_ok and not e00_ok:
                note = "fine-tuning fixes a zero-shot error"
            elif not e03_ok:
                note = "failure-driven still fails; useful for limitation analysis"
            else:
                note = "all stronger systems succeed"
            lines.append(
                f"| {idx} | {str(any_row.get('image_path','')).replace('|','\\\\|')} | "
                f"{str(any_row.get('question','')).replace('|','\\\\|')} | "
                f"{'; '.join(any_row.get('answers', []))[:120].replace('|','\\\\|')} | "
                + " | ".join(preds)
                + f" | {error_type} | {note} |"
            )

        output_path = repo_path(args.output)
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        emit(f"wrote {len(chosen)} case studies", log_file=args.log_file)
        append_log(args.log_file, json.dumps({"cases": len(chosen), "output": args.output}))
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
