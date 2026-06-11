#!/usr/bin/env python3
"""Validate FD-VIT processed/Qwen data files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, append_log, display_path, repo_path, utc_now, write_json


REQUIRED_FIELDS = [
    "sample_id",
    "dataset",
    "split",
    "question_id",
    "image_id",
    "image_path",
    "question",
    "answers",
    "answer",
]
GUI_REQUIRED_FIELDS = [
    "sample_id",
    "dataset",
    "split",
    "image_path",
    "instruction",
    "bbox",
    "point",
    "image_size",
    "control_type",
]
VALID_SPLITS = {"train", "val", "test", "dev"}
OVERLAP_KEYS = {"question_id", "image_id"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input JSONL/JSON file for validation")
    parser.add_argument("--check_images", action="store_true", help="Validate image_path exists")
    parser.add_argument("--train", default=None, help="Optional train input file for overlap checking")
    parser.add_argument("--eval", default=None, help="Optional eval input file for overlap checking")
    parser.add_argument("--check_overlap", action="store_true", help="Enable overlap check when --train and --eval are provided")
    parser.add_argument(
        "--expect_split",
        choices=["train", "val", "test", "dev"],
        default=None,
        help="If set, verify every record's split equals this value",
    )
    parser.add_argument("--output", required=True, help="Path to write validation summary JSON")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file")
    parser.add_argument("--log_file", default=None, help="Optional log file path")
    return parser.parse_args()


def parse_file(path: str | Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    file_path = repo_path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"input not found: {display_path(file_path)}")

    content = file_path.read_text(encoding="utf-8").strip()
    errors: list[dict[str, Any]] = []
    if not content:
        return [], [{"type": "empty_file", "message": "file is empty"}]

    if content.startswith("["):
        try:
            payload = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            return [], [{"type": "json_parse_error", "message": str(exc)}]
        if not isinstance(payload, list):
            return [], [{"type": "invalid_payload", "message": "JSON payload is not a list"}]
        records = []
        for idx, item in enumerate(payload):
            if not isinstance(item, dict):
                errors.append({"type": "invalid_record", "index": idx, "message": "record is not an object"})
                continue
            records.append(item)
        return records, errors

    records = []
    for idx, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                errors.append(
                    {
                        "type": "invalid_record",
                        "index": idx,
                        "message": "record is not an object",
                    }
                )
                continue
            records.append(item)
        except Exception as exc:  # noqa: BLE001
            errors.append({"type": "json_parse_error", "index": idx, "message": f"{type(exc).__name__}: {exc}"})
    return records, errors


def check_records(records: list[dict[str, Any]], check_images: bool, expect_split: str | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    stats = {
        "field_coverage": Counter(),
        "non_empty_question": 0,
        "non_empty_answers": 0,
        "num_records": len(records),
        "qwen_records": 0,
        "legacy_records": 0,
        "gui_records": 0,
        "non_empty_instruction": 0,
    }

    sample_id_counter = Counter()
    image_missing = 0

    for idx, record in enumerate(records):
        if {"sample_id", "instruction", "bbox", "image_size"} <= record.keys():
            schema = "gui"
            missing = [field for field in GUI_REQUIRED_FIELDS if record.get(field) in (None, "", [])]
            sid = record.get("sample_id")
            if missing:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "missing_required_field",
                        "field": missing[0],
                        "message": f"missing or empty GUI field: {missing[0]}",
                    }
                )
            if sid is not None:
                sample_id_counter[sid] += 1
            else:
                errors.append({"index": idx, "type": "missing_sample_id", "message": "sample_id missing"})
            if record.get("split") not in VALID_SPLITS:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "invalid_split",
                        "message": f"invalid split: {record.get('split')}",
                    }
                )
            if expect_split and record.get("split") != expect_split:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "wrong_split",
                        "message": f"split expected {expect_split}, got {record.get('split')}",
                    }
                )
            if isinstance(record.get("instruction"), str) and record["instruction"].strip():
                stats["non_empty_instruction"] += 1
            else:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "empty_instruction",
                        "message": "instruction is empty",
                    }
                )
            for field, expected_len in (("bbox", 4), ("point", 2), ("image_size", 2)):
                value = record.get(field)
                if not isinstance(value, list) or len(value) != expected_len:
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "invalid_gui_geometry",
                            "field": field,
                            "message": f"{field} must be a list of length {expected_len}",
                        }
                    )
                    continue
                try:
                    numbers = [float(item) for item in value]
                except (TypeError, ValueError):
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "invalid_gui_geometry",
                            "field": field,
                            "message": f"{field} must contain numeric values",
                        }
                    )
                    continue
                if field == "bbox" and (numbers[2] < numbers[0] or numbers[3] < numbers[1]):
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "invalid_gui_geometry",
                            "field": field,
                            "message": "bbox must satisfy x2 >= x1 and y2 >= y1",
                        }
                    )
                if field == "image_size" and (numbers[0] <= 0 or numbers[1] <= 0):
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "invalid_gui_geometry",
                            "field": field,
                            "message": "image_size values must be positive",
                        }
                    )
            if check_images:
                image_path = record.get("image_path")
                if not isinstance(image_path, str):
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "invalid_image_path",
                            "message": "image_path missing or not a string",
                        }
                    )
                else:
                    path = Path(image_path)
                    if not path.is_absolute():
                        path = repo_path(path)
                    if not path.exists():
                        image_missing += 1
                        errors.append(
                            {
                                "index": idx,
                                "sample_id": sid,
                                "type": "image_not_found",
                                "message": f"missing image: {image_path}",
                            }
                        )
            for field in GUI_REQUIRED_FIELDS:
                if record.get(field):
                    stats["field_coverage"][field] += 1
            stats["gui_records"] += 1

        elif "sample_id" in record:
            schema = "legacy"
            missing = [field for field in REQUIRED_FIELDS if not record.get(field)]
            if missing:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": record.get("sample_id"),
                        "type": "missing_required_field",
                        "field": missing[0],
                        "message": f"missing or empty field: {missing[0]}",
                    }
                )
            if record.get("question", "").strip() == "":
                errors.append(
                    {
                        "index": idx,
                        "sample_id": record.get("sample_id"),
                        "type": "empty_question",
                        "message": "question is empty",
                    }
                )
            else:
                stats["non_empty_question"] += 1
            if not isinstance(record.get("answers"), list) or not any(
                isinstance(ans, str) and ans.strip() for ans in record.get("answers", [])
            ):
                errors.append(
                    {
                        "index": idx,
                        "sample_id": record.get("sample_id"),
                        "type": "empty_answers",
                        "message": "answers is missing or empty",
                    }
                )
            else:
                stats["non_empty_answers"] += 1
            if expect_split and record.get("split") != expect_split:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": record.get("sample_id"),
                        "type": "wrong_split",
                        "message": f"split expected {expect_split}, got {record.get('split')}",
                    }
                )
            if record.get("split") not in VALID_SPLITS:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": record.get("sample_id"),
                        "type": "invalid_split",
                        "message": f"invalid split: {record.get('split')}",
                    }
                )
            stats["legacy_records"] += 1
            sid = record.get("sample_id")
            if sid is not None:
                sample_id_counter[sid] += 1
            else:
                errors.append(
                    {
                        "index": idx,
                        "type": "missing_sample_id",
                        "message": "sample_id missing",
                    }
                )
            if check_images:
                image_path = record.get("image_path")
                if not isinstance(image_path, str):
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "invalid_image_path",
                            "message": "image_path missing or not a string",
                        }
                    )
                else:
                    path = Path(image_path)
                    if not path.is_absolute():
                        path = repo_path(path)
                    if not path.exists():
                        image_missing += 1
                        errors.append(
                            {
                                "index": idx,
                                "sample_id": sid,
                                "type": "image_not_found",
                                "message": f"missing image: {image_path}",
                            }
                        )
            for field in REQUIRED_FIELDS:
                if record.get(field):
                    stats["field_coverage"][field] += 1

        elif {"id", "image", "conversations"} <= record.keys():
            schema = "qwen"
            sid = record.get("id")
            if sid is None:
                errors.append(
                    {
                        "index": idx,
                        "type": "missing_sample_id",
                        "message": "Qwen sample id missing",
                    }
                )
            else:
                sample_id_counter[sid] += 1
            if not record.get("image"):
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "missing_image",
                        "message": "qwen record missing image",
                    }
                )
            elif check_images and not repo_path(record["image"]).exists():
                image_missing += 1
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "image_not_found",
                        "message": f"missing image: {record['image']}",
                    }
                )

            conversations = record.get("conversations")
            if not isinstance(conversations, list) or not conversations:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "missing_conversations",
                        "message": "conversations missing or empty",
                    }
                )
            else:
                human_values = []
                for message in conversations:
                    if not isinstance(message, dict):
                        continue
                    if message.get("from") == "human":
                        value = message.get("value", "")
                        if isinstance(value, str):
                            human_values.append(value)
                if not any("<image>" in item for item in human_values):
                    errors.append(
                        {
                            "index": idx,
                            "sample_id": sid,
                            "type": "qwen_missing_image_token",
                            "message": "human prompt missing <image>",
                        }
                    )
            if sid is not None and expect_split is not None and record.get("dataset_split") != expect_split:
                errors.append(
                    {
                        "index": idx,
                        "sample_id": sid,
                        "type": "wrong_split",
                        "message": f"dataset_split expected {expect_split}, got {record.get('dataset_split')}",
                    }
                )
            stats["qwen_records"] += 1

        else:
            errors.append(
                {
                    "index": idx,
                    "type": "unsupported_schema",
                    "message": "record does not match processed or qwen schema",
                }
            )
            schema = "unknown"
            sample_id_counter[None] += 1

        # Keep this for debugging only; no functional need.
        # (kept as a stable variable to ease future extension)
        _ = schema

    duplicate_count = sum(1 for item in sample_id_counter.values() if item > 1)
    return (
        errors,
        {
            "unique_sample_id_count": len(sample_id_counter),
            "duplicate_sample_ids": duplicate_count,
            "image_not_found_count": image_missing,
            "sample_stats": stats,
            "sample_id_over_count": [sid for sid, count in sample_id_counter.items() if count > 1][:20],
        },
    )


def collect_ids(records: list[dict[str, Any]], keys: set[str]) -> dict[str, set[Any]]:
    data: dict[str, set[Any]] = {key: set() for key in keys}
    for item in records:
        for key in keys:
            value = item.get(key)
            if value is not None:
                data[key].add(value)
    return data


def check_overlap(train_file: str | Path, eval_file: str | Path) -> dict[str, Any]:
    train_records, train_parse_errors = parse_file(train_file)
    eval_records, eval_parse_errors = parse_file(eval_file)
    overlap = {}
    if train_parse_errors or eval_parse_errors:
        return {
            "status": "failed",
            "train_parse_errors": train_parse_errors,
            "eval_parse_errors": eval_parse_errors,
            "overlap": {},
        }

    train_ids = collect_ids(train_records, OVERLAP_KEYS)
    eval_ids = collect_ids(eval_records, OVERLAP_KEYS)

    for key in OVERLAP_KEYS:
        overlap_values = sorted(train_ids[key] & eval_ids[key])
        overlap[key] = {
            "count": len(overlap_values),
            "samples": overlap_values[:20],
        }
    return {"status": "passed", "overlap": overlap}


def emit(msg: str, log_file: str | None) -> None:
    print(msg)
    append_log(log_file, msg)


def main() -> int:
    args = parse_args()

    all_errors: list[dict[str, Any]] = []
    input_records, parse_errors = parse_file(args.input)
    all_errors.extend(parse_errors)

    check_errors: list[dict[str, Any]]
    extra_stats: dict[str, Any]
    check_errors, extra_stats = check_records(input_records, args.check_images, args.expect_split)
    all_errors.extend(check_errors)

    overlap_result: dict[str, Any] | None = None
    if args.check_overlap:
        if not args.train or not args.eval:
            all_errors.append(
                {
                    "type": "overlap_config_error",
                    "message": "both --train and --eval are required when --check_overlap is set",
                }
            )
        else:
            overlap_result = check_overlap(args.train, args.eval)
            if overlap_result.get("status") != "passed":
                overlap_errors = overlap_result.get("train_parse_errors") or overlap_result.get("eval_parse_errors")
                if overlap_errors:
                    for item in overlap_errors:
                        item["type"] = "overlap_parse_error"
                        all_errors.append(item)
                else:
                    all_errors.append({"type": "overlap_check_failed", "message": "overlap check failed"})

    summary = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "input": display_path(args.input),
        "status": "failed" if all_errors else "passed",
        "num_records": len(input_records),
        "num_errors": len(all_errors),
        "errors": all_errors,
        "checks": {
            "parseable": len(parse_errors) == 0,
            "required_fields": not any(
                e["type"]
                in {
                    "missing_required_field",
                    "empty_question",
                    "empty_answers",
                    "empty_instruction",
                    "invalid_split",
                    "invalid_gui_geometry",
                }
                for e in all_errors
            ),
            "sample_id_unique": extra_stats["duplicate_sample_ids"] == 0,
            "images_exist": extra_stats["image_not_found_count"] == 0,
            "check_images": args.check_images,
            "schema_stats": {
                "qwen_records": extra_stats["sample_stats"]["qwen_records"],
                "legacy_records": extra_stats["sample_stats"]["legacy_records"],
                "gui_records": extra_stats["sample_stats"]["gui_records"],
            },
            "legacy_field_coverage": dict(extra_stats["sample_stats"]["field_coverage"]),
            "question_non_empty": extra_stats["sample_stats"]["non_empty_question"],
            "answers_non_empty": extra_stats["sample_stats"]["non_empty_answers"],
            "instruction_non_empty": extra_stats["sample_stats"]["non_empty_instruction"],
        },
        "stats": extra_stats,
    }
    if overlap_result is not None:
        summary["train_eval_overlap"] = overlap_result

    write_json(args.output, summary, overwrite=args.overwrite)
    emit(f"wrote {display_path(args.output)}", args.log_file)
    if summary["status"] == "passed":
        emit("validation passed", args.log_file)
        return 0
    emit(f"validation failed with {summary['num_errors']} errors", args.log_file)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
