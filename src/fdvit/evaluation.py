"""Evaluation utilities for FD-VIT VQA predictions."""

from __future__ import annotations

import re
from typing import Any


NUM_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def normalize_answer(text: str | None) -> str:
    if not isinstance(text, str):
        return ""
    value = text.strip().lower()
    value = value.replace("\t", " ").replace("\n", " ")

    prefix_patterns = [
        r"^the answer is\s+",
        r"^answer is\s+",
        r"^answer:\s*",
        r"^it is\s+",
        r"^it's\s+",
    ]
    for pattern in prefix_patterns:
        value = re.sub(pattern, "", value)

    for word, num in NUM_WORDS.items():
        value = re.sub(rf"\\b{word}\\b", num, value)

    value = re.sub(r"[^\w\s%.-]", "", value, flags=re.UNICODE)
    value = re.sub(r"\b(a|an|the)\b", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def is_format_error(prediction: str) -> bool:
    if not isinstance(prediction, str):
        return True
    v = prediction.strip()
    if not v:
        return True
    if len(v) > 80:
        return True
    lowered = v.lower()
    flag_tokens = (
        " because ",
        " i think ",
        "the answer is",
        "it is",
        "as far as",
    )
    flag = (
        lowered.startswith(("because ", "i think ", "the answer is", "it is", "as far as"))
        or any(token in lowered for token in flag_tokens)
    )
    return bool(flag or "\n" in v)


def evaluate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    valid = 0
    match_any = 0
    soft_sum = 0.0
    format_errors = 0
    empty = 0
    lengths = []
    errors = []

    for idx, record in enumerate(records):
        pred_raw = normalize_answer(record.get("prediction", record.get("prediction_raw", "")))
        answers = record.get("answers", [])
        if not isinstance(answers, list):
            answers = []
        gt = [normalize_answer(a) for a in answers if isinstance(a, str)]
        gt = [a for a in gt if a]

        is_empty = pred_raw == ""
        is_fmt = is_format_error(pred_raw)
        if is_fmt:
            format_errors += 1
        if is_empty:
            empty += 1
            lengths.append(0)
        else:
            lengths.append(len(pred_raw.split()))
            valid += 1

        item_is_correct = False
        if gt:
            if pred_raw in gt:
                match_any += 1
                item_is_correct = True
            soft = min(gt.count(pred_raw) / 3.0, 1.0)
            soft_sum += soft
        else:
            soft_sum += 0.0

        record["normalized_prediction"] = pred_raw
        record["normalized_answers"] = gt
        if not item_is_correct:
            errors.append(
                {
                    "index": idx,
                    "sample_id": record.get("sample_id"),
                    "question_id": record.get("question_id"),
                    "prediction_raw": record.get("prediction_raw", ""),
                    "prediction": pred_raw,
                    "normalized_prediction": pred_raw,
                    "answers": answers,
                    "normalized_answers": gt,
                    "is_correct": False,
                    "format_error": is_fmt,
                    "error": record.get("error"),
                }
            )

    num = total if total else 1
    return {
        "num_samples": total,
        "num_valid_predictions": valid,
        "acc_any": match_any / num,
        "acc_soft": soft_sum / num,
        "format_error_rate": format_errors / num,
        "empty_prediction_rate": empty / num,
        "avg_prediction_length_tokens": round(sum(lengths) / max(1, len(lengths)), 4),
        "errors": errors,
        "error_count": len(errors),
    }
