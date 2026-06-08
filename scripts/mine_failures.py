#!/usr/bin/env python3
"""Mine failure cases from predictions/errors and assign weak error types."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from fdvit.evaluation import is_format_error, normalize_answer
from fdvit_prep_common import append_log, display_path, emit, repo_path


ERROR_TYPES = (
    "answer_format",
    "counting",
    "ocr_text",
    "spatial",
    "attribute",
    "commonsense",
    "hallucination",
    "ambiguous",
    "other",
)

OCR_KEYWORDS = ("sign", "text", "word", "read", "license", "plate", "menu", "screen", "label", "number on")
SPATIAL_KEYWORDS = ("left", "right", "above", "below", "behind", "in front of", "front of", "next to", "between", "under", "on top of")
ATTRIBUTE_KEYWORDS = ("color", "wearing", "holding", "made of", "type of", "kind of", "what animal", "what is the man doing")
COMMONSENSE_KEYWORDS = (
    "sport",
    "country",
    "flag",
    "brand",
    "use",
    "used for",
    "job",
    "profession",
    "why",
    "purpose",
)
HALLUCINATION_ANSWERS = ("none", "nothing", "no logo", "no text", "no words", "no animal", "no people")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", default=None, help="Predictions JSONL/JSON; failures will be derived from wrong samples")
    parser.add_argument("--errors", default=None, help="Existing errors JSONL/JSON; failures will be enriched directly")
    parser.add_argument("--output", required=True, help="Output failures_mined JSONL")
    parser.add_argument("--summary", required=True, help="Output CSV summary")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs if they already exist")
    parser.add_argument("--seed", type=int, default=42, help="Recorded only for traceability")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
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
            obj = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"line {line_no}: parse error: {exc}") from exc
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _prediction_text(record: dict[str, Any]) -> str:
    if isinstance(record.get("prediction"), str) and record.get("prediction", "").strip():
        return str(record["prediction"])
    return str(record.get("prediction_raw", "") or "")


def _normalized_answers(record: dict[str, Any]) -> list[str]:
    if isinstance(record.get("normalized_answers"), list):
        normalized = [str(x).strip() for x in record["normalized_answers"] if isinstance(x, str) and str(x).strip()]
        if normalized:
            return normalized
    answers = record.get("answers", [])
    if not isinstance(answers, list):
        return []
    return [normalize_answer(x) for x in answers if isinstance(x, str) and normalize_answer(x)]


def _is_correct(record: dict[str, Any]) -> bool:
    prediction = normalize_answer(_prediction_text(record))
    answers = _normalized_answers(record)
    return bool(answers and prediction in answers)


def derive_failures_from_predictions(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    failures: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if _is_correct(row):
            continue
        prediction = normalize_answer(_prediction_text(row))
        answers = row.get("answers", [])
        normalized_answers = _normalized_answers(row)
        failures.append(
            {
                "index": idx,
                "sample_id": row.get("sample_id"),
                "dataset": row.get("dataset"),
                "split": row.get("split"),
                "question_id": row.get("question_id"),
                "image_id": row.get("image_id"),
                "image_path": row.get("image_path"),
                "question": row.get("question"),
                "answers": answers if isinstance(answers, list) else [],
                "prediction_raw": row.get("prediction_raw", _prediction_text(row)),
                "prediction": prediction,
                "normalized_prediction": prediction,
                "normalized_answers": normalized_answers,
                "is_correct": False,
                "format_error": is_format_error(prediction),
                "error": row.get("error"),
                "template_id": row.get("template_id"),
                "source_experiment": row.get("experiment_id"),
            }
        )
    return failures, len(rows)


def explanation_flag(text: str) -> bool:
    lowered = f" {text.lower()} "
    markers = (" because ", " i think ", " the answer is ", " it is ", " there are ", " there is ")
    return any(marker in lowered for marker in markers)


def too_long_flag(text: str) -> bool:
    return len(text.split()) > 6 or len(text) > 80


def maybe_hallucination(record: dict[str, Any], question_lower: str, prediction_lower: str) -> bool:
    answers = {x.lower() for x in record.get("answers", []) if isinstance(x, str)}
    if any(answer in answers for answer in HALLUCINATION_ANSWERS) and prediction_lower and prediction_lower not in answers:
        return True
    if "what animal" in question_lower and prediction_lower in {"dog", "cat", "horse", "bird", "bear", "cow"}:
        return "none" in answers or "nothing" in answers
    return False


def detect_error_type(record: dict[str, Any]) -> str:
    question = str(record.get("question", "") or "")
    prediction = str(record.get("prediction", "") or record.get("prediction_raw", "") or "")
    answers = [str(x).strip() for x in record.get("answers", []) if isinstance(x, str) and str(x).strip()]
    normalized_answers = [str(x).strip() for x in record.get("normalized_answers", []) if isinstance(x, str) and str(x).strip()]
    question_lower = question.lower()
    prediction_lower = normalize_answer(prediction)

    if not prediction_lower or is_format_error(prediction) or explanation_flag(prediction) or too_long_flag(prediction):
        return "answer_format"
    if question_lower.startswith("how many") or "number of" in question_lower or "count " in question_lower:
        return "counting"
    if any(keyword in question_lower for keyword in OCR_KEYWORDS):
        return "ocr_text"
    if any(keyword in question_lower for keyword in SPATIAL_KEYWORDS):
        return "spatial"
    if any(keyword in question_lower for keyword in ATTRIBUTE_KEYWORDS):
        return "attribute"
    if maybe_hallucination(record, question_lower, prediction_lower):
        return "hallucination"
    unique_answers = set(normalized_answers)
    if len(unique_answers) >= 4:
        return "ambiguous"
    if any(keyword in question_lower for keyword in COMMONSENSE_KEYWORDS):
        return "commonsense"
    if question_lower.startswith(("what", "which", "is", "are", "does", "do")) and answers and prediction_lower:
        return "other"
    return "other"


def enrich_failure(record: dict[str, Any], *, fallback_experiment: str | None = None) -> dict[str, Any]:
    prediction = normalize_answer(_prediction_text(record))
    answers = record.get("answers", [])
    if not isinstance(answers, list):
        answers = []
    normalized_answers = _normalized_answers(record)
    flags = {
        "too_long": too_long_flag(str(record.get("prediction_raw", "") or record.get("prediction", "") or "")),
        "has_explanation": explanation_flag(str(record.get("prediction_raw", "") or record.get("prediction", "") or "")),
        "empty": prediction == "",
    }
    error_type = detect_error_type({**record, "prediction": prediction, "normalized_answers": normalized_answers})
    return {
        "sample_id": record.get("sample_id"),
        "dataset": record.get("dataset"),
        "split": record.get("split"),
        "question_id": record.get("question_id"),
        "image_id": record.get("image_id"),
        "image_path": record.get("image_path"),
        "question": record.get("question"),
        "answers": answers,
        "prediction_raw": record.get("prediction_raw", _prediction_text(record)),
        "prediction": prediction,
        "normalized_prediction": prediction,
        "normalized_answers": normalized_answers,
        "is_correct": False,
        "error_type_auto": error_type,
        "error_type_manual": None,
        "note": None,
        "format_flags": flags,
        "source_experiment": record.get("source_experiment") or record.get("experiment_id") or fallback_experiment,
        "error": record.get("error"),
    }


def infer_experiment_id(records: list[dict[str, Any]], source_path: str | None) -> str:
    for record in records:
        for key in ("source_experiment", "experiment_id"):
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    if source_path:
        return Path(source_path).resolve().parent.name or "unknown"
    return "unknown"


def write_failures_jsonl(path: str | Path, records: list[dict[str, Any]], *, overwrite: bool) -> None:
    target = repo_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_summary_csv(
    path: str | Path,
    *,
    experiment_id: str,
    counts: Counter[str],
    total_errors: int,
    num_samples: int,
    overwrite: bool,
) -> None:
    target = repo_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("experiment_id", "error_type", "num_errors", "error_rate", "num_samples", "notes"),
        )
        writer.writeheader()
        for error_type in ERROR_TYPES:
            num_errors = counts.get(error_type, 0)
            writer.writerow(
                {
                    "experiment_id": experiment_id,
                    "error_type": error_type,
                    "num_errors": num_errors,
                    "error_rate": round(num_errors / max(1, total_errors), 6),
                    "num_samples": num_samples,
                    "notes": "",
                }
            )


def main() -> int:
    args = parse_args()
    try:
        if not args.predictions and not args.errors:
            raise ValueError("provide at least one of --predictions or --errors")
        if args.predictions and args.errors:
            raise ValueError("use only one input source at a time: --predictions or --errors")

        source_path = args.predictions or args.errors
        source_records = read_json_like(source_path)

        if args.predictions:
            failures_raw, num_samples = derive_failures_from_predictions(source_records)
        else:
            failures_raw = [row for row in source_records if isinstance(row, dict)]
            num_samples = len(failures_raw)

        experiment_id = infer_experiment_id(failures_raw or source_records, source_path)
        failures = [enrich_failure(row, fallback_experiment=experiment_id) for row in failures_raw]
        counts: Counter[str] = Counter(row["error_type_auto"] for row in failures)

        write_failures_jsonl(args.output, failures, overwrite=args.overwrite)
        write_summary_csv(
            args.summary,
            experiment_id=experiment_id,
            counts=counts,
            total_errors=len(failures),
            num_samples=num_samples,
            overwrite=args.overwrite,
        )

        emit(
            f"wrote {display_path(repo_path(args.output))} with {len(failures)} failures; "
            f"top types: {counts.most_common(4)}",
            log_file=args.log_file,
        )
        append_log(
            args.log_file,
            json.dumps(
                {
                    "source": display_path(repo_path(source_path)),
                    "output": display_path(repo_path(args.output)),
                    "summary": display_path(repo_path(args.summary)),
                    "seed": args.seed,
                    "experiment_id": experiment_id,
                    "num_samples": num_samples,
                    "num_failures": len(failures),
                    "counts": dict(counts),
                },
                ensure_ascii=False,
            ),
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
