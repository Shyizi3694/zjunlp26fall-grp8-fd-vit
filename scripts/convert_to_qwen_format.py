#!/usr/bin/env python3
"""Convert unified VQA JSONL/JSON records into Qwen3-VL training JSON format."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from fdvit.prompts import PromptError, load_template_library, pick_template, render_prompt
from fdvit_prep_common import append_log, display_path, emit, repo_path, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input unified JSONL/JSON records")
    parser.add_argument("--output", required=True, help="Output Qwen training JSON file")
    parser.add_argument("--template_file", required=True, help="Prompt template library JSON file")
    parser.add_argument("--template_id", default=None, help="Optional fixed template_id")
    parser.add_argument(
        "--template_mode",
        choices=("single", "multi"),
        default="single",
        help="single uses one fixed/deterministic template; multi cycles deterministically across templates",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic template assignment")
    parser.add_argument("--limit", type=int, default=0, help="Max number of records to convert (0 means all)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it already exists")
    parser.add_argument("--log_file", default=None, help="Optional log file path")
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


def clean_short_answer(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def validate_record(record: dict[str, Any], *, index: int) -> None:
    required = ("sample_id", "image_path", "question", "answer")
    missing = [key for key in required if not str(record.get(key, "")).strip()]
    if missing:
        raise ValueError(f"record {index}: missing required fields: {', '.join(missing)}")


def choose_template(templates: list[Any], *, args: argparse.Namespace, position: int) -> Any:
    if args.template_mode == "single":
        return pick_template(templates, template_id=args.template_id, seed=args.seed, position=0)
    return pick_template(templates, template_id=args.template_id, seed=args.seed, position=position)


def convert_record(record: dict[str, Any], *, template: Any) -> dict[str, Any]:
    question = str(record.get("question", "") or "").strip()
    prompt = render_prompt(template, question=question)
    answer = clean_short_answer(record.get("answer", ""))
    metadata = {
        "dataset": record.get("dataset"),
        "split": record.get("split"),
        "question_id": record.get("question_id"),
        "image_id": record.get("image_id"),
        "template_id": template.template_id,
        "source_sample_id": record.get("sample_id"),
    }
    answers = record.get("answers")
    if isinstance(answers, list):
        metadata["answers"] = answers

    return {
        "id": str(record["sample_id"]),
        "image": str(record["image_path"]),
        "conversations": [
            {"from": "human", "value": prompt},
            {"from": "gpt", "value": answer},
        ],
        "metadata": metadata,
    }


def main() -> int:
    args = parse_args()
    try:
        templates = load_template_library(args.template_file, task="vqa", log_file=args.log_file)
        rows = read_json_like(args.input)
        selected_rows = rows[: args.limit] if args.limit > 0 else rows

        converted: list[dict[str, Any]] = []
        template_usage: dict[str, int] = {}
        for idx, record in enumerate(selected_rows):
            validate_record(record, index=idx + 1)
            template = choose_template(templates, args=args, position=idx)
            item = convert_record(record, template=template)
            converted.append(item)
            template_usage[template.template_id] = template_usage.get(template.template_id, 0) + 1

        output_path = repo_path(args.output)
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {display_path(output_path)}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(converted, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        append_log(
            args.log_file,
            json.dumps(
                {
                    "created_at": utc_now(),
                    "input": display_path(repo_path(args.input)),
                    "output": display_path(output_path),
                    "template_mode": args.template_mode,
                    "template_id": args.template_id,
                    "seed": args.seed,
                    "num_records": len(converted),
                    "template_usage": template_usage,
                },
                ensure_ascii=False,
            ),
        )
        emit(
            f"wrote {display_path(output_path)} with {len(converted)} records "
            f"using {len(template_usage)} template(s)",
            log_file=args.log_file,
        )
        return 0
    except (PromptError, ValueError, FileExistsError, FileNotFoundError) as exc:
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {type(exc).__name__}: {exc}")
        append_log(args.log_file, f"ERROR: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
