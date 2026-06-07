#!/usr/bin/env python3
"""Prepare OK-VQA train/val split into project unified JSONL format."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, display_path, emit, repo_path, utc_now, write_json


QUESTION_FILES = {
    "train": "OpenEnded_mscoco_train2014_questions.json",
    "val": "OpenEnded_mscoco_val2014_questions.json",
}
ANNOTATION_FILES = {
    "train": "mscoco_train2014_annotations.json",
    "val": "mscoco_val2014_annotations.json",
}

VALID_SPLITS = {"train", "val"}
DATASET_NAME = "okvqa"
TOP_ANSWERS_COUNT = 20
DEFAULT_SAMPLE_OUTPUT = "data/samples/okvqa_10.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw_dir", required=True, help="Directory that contains OK-VQA question/annotation JSON files")
    parser.add_argument("--image_root", required=True, help="Root of COCO image dirs, e.g., data/raw/coco")
    parser.add_argument("--output_dir", required=True, help="Output root for processed jsonl files")
    parser.add_argument("--limit", type=int, default=0, help="Max samples per split (0 means no limit)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic sampling/shuffling")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output files if they exist")
    parser.add_argument(
        "--sample_output",
        default=DEFAULT_SAMPLE_OUTPUT,
        help="Output path for smoke-test sample JSONL",
    )
    parser.add_argument("--log_file", default=None, help="Optional log file path")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def canonical_answer(answers: list[str]) -> str:
    cleaned = [ans.strip() for ans in answers if isinstance(ans, str) and ans.strip()]
    if not cleaned:
        return ""
    return Counter(cleaned).most_common(1)[0][0]


def build_image_path(image_root: Path, split: str, image_id: int) -> Path:
    file_name = f"COCO_{split}2014_{image_id:012d}.jpg"
    return image_root / ("train2014" if split == "train" else "val2014") / file_name


def prepare_split(raw_dir: Path, image_root: Path, split: str, rng: random.Random) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    questions = load_json(raw_dir / QUESTION_FILES[split])
    annotations = load_json(raw_dir / ANNOTATION_FILES[split])
    questions_list = questions.get("questions", [])
    annotations_list = annotations.get("annotations", [])

    if not isinstance(questions_list, list):
        raise ValueError(f"{split}: questions is not a list")
    if not isinstance(annotations_list, list):
        raise ValueError(f"{split}: annotations is not a list")

    ann_by_qid = {to_int(item.get("question_id")): item for item in annotations_list if isinstance(item, dict)}
    records: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []

    for q in questions_list:
        if not isinstance(q, dict):
            anomalies.append({"split": split, "issue": "invalid_question_record", "record": q})
            continue

        qid = to_int(q.get("question_id"))
        image_id = to_int(q.get("image_id"))
        if qid is None or image_id is None:
            anomalies.append(
                {
                    "split": split,
                    "question_id": q.get("question_id"),
                    "issue": "missing_question_or_image_id",
                }
            )
            continue

        annotation = ann_by_qid.get(qid)
        if annotation is None:
            anomalies.append({"split": split, "question_id": qid, "issue": "missing_annotation"})
            continue

        answers_raw = annotation.get("answers", [])
        answers = []
        if isinstance(answers_raw, list):
            for item in answers_raw:
                if not isinstance(item, dict):
                    continue
                val = item.get("answer")
                if isinstance(val, str) and val.strip():
                    answers.append(val.strip())

        answer = canonical_answer(answers)
        image_path = build_image_path(image_root, split, image_id)
        records.append(
            {
                "sample_id": f"{DATASET_NAME}_{split}_{len(records)+1:06d}",
                "dataset": DATASET_NAME,
                "split": split,
                "question_id": qid,
                "image_id": image_id,
                "image_path": str(image_path.relative_to(ROOT).as_posix()),
                "question": (q.get("question") or "").strip(),
                "answers": answers,
                "answer": answer,
            }
        )

    rng.shuffle(records)
    return records, {
        "split": split,
        "num_questions": len(questions_list),
        "num_annotations": len(annotations_list),
        "num_records": len(records),
        "num_anomalies": len(anomalies),
        "sample_anomalies": anomalies[:5],
    }


def write_jsonl(path: str | Path, records: list[dict[str, Any]], *, overwrite: bool) -> None:
    target = Path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def compute_stats(records: list[dict[str, Any]], sample_limit: int = 20) -> dict[str, Any]:
    total = len(records)
    empty_answer = sum(1 for r in records if not r.get("answers"))
    empty_question = sum(1 for r in records if not (str(r.get("question", "") or "").strip()))
    answer_lists = [r.get("answers", []) for r in records]
    answer_counter: Counter[str] = Counter()
    for ans_list in answer_lists:
        if isinstance(ans_list, list):
            answer_counter.update([a for a in ans_list if isinstance(a, str) and a.strip()])

    image_checks = []
    missing_images = 0
    checked = 0
    for item in records:
        path = repo_path(item["image_path"]) if isinstance(item.get("image_path"), str) else None
        exists = False
        if path is not None:
            checked += 1
            exists = path.exists()
        if not exists:
            missing_images += 1
        if len(image_checks) < sample_limit:
            image_checks.append({"sample_id": item["sample_id"], "image_path": item["image_path"], "exists": exists})

    question_lengths = [len(str(r.get("question", ""))) for r in records]
    answer_lengths = [len(str(r.get("answer", ""))) for r in records]

    return {
        "num_records": total,
        "empty_answer_count": empty_answer,
        "empty_answer_ratio": empty_answer / total if total else 0.0,
        "empty_question_count": empty_question,
        "empty_question_ratio": empty_question / total if total else 0.0,
        "image_path_checks": {
            "checked": checked,
            "exists": checked - missing_images,
            "missing": missing_images,
            "exist_ratio": (checked - missing_images) / checked if checked else 0.0,
            "samples": image_checks,
        },
        "avg_question_length": round(sum(question_lengths) / total, 2) if total else 0.0,
        "avg_answer_length": round(sum(answer_lengths) / total, 2) if total else 0.0,
        "top_20_answers": answer_counter.most_common(TOP_ANSWERS_COUNT),
    }


def main() -> int:
    args = parse_args()
    raw_dir = repo_path(args.raw_dir)
    image_root = repo_path(args.image_root)
    output_dir = Path(args.output_dir)
    sample_output = Path(args.sample_output)

    if not raw_dir.exists():
        emit(f"raw_dir not found: {display_path(raw_dir)}")
        return 1

    for split in VALID_SPLITS:
        if not (raw_dir / QUESTION_FILES[split]).exists():
            emit(f"missing {split} question file: {display_path(raw_dir / QUESTION_FILES[split])}")
            return 1
        if not (raw_dir / ANNOTATION_FILES[split]).exists():
            emit(f"missing {split} annotation file: {display_path(raw_dir / ANNOTATION_FILES[split])}")
            return 1
    if not image_root.exists():
        emit(f"image_root not found: {display_path(image_root)}")
        return 1

    rng = random.Random(args.seed)
    split_stats: dict[str, Any] = {}
    all_records: list[dict[str, Any]] = []

    for split in sorted(VALID_SPLITS):
        records, stats = prepare_split(raw_dir, image_root, split, rng)
        write_records = records[: args.limit] if args.limit > 0 else records
        output_dir.mkdir(parents=True, exist_ok=True)
        split_path = output_dir / f"{split}.jsonl"
        write_jsonl(split_path, write_records, overwrite=args.overwrite)
        split_stats[split] = {
            **stats,
            "written": display_path(split_path),
            "limit": args.limit,
            "seed": args.seed,
            "written_records": len(write_records),
        }
        all_records.extend(write_records)

    sample_records = list(all_records)
    rng.shuffle(sample_records)
    sample_records = sample_records[:10]
    write_jsonl(sample_output, sample_records, overwrite=args.overwrite)

    train_count = len([r for r in all_records if r["split"] == "train"])
    val_count = len([r for r in all_records if r["split"] == "val"])
    stats = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "raw_dir": display_path(raw_dir),
        "image_root": display_path(image_root),
        "output_dir": display_path(output_dir),
        "seed": args.seed,
        "limit": args.limit,
        "split_stats": split_stats,
        "records": {
            "total": len(all_records),
            "train": train_count,
            "val": val_count,
            "sampled": len(sample_records),
            "sample_path": display_path(sample_output),
        },
        "global": compute_stats(all_records),
    }

    write_json(
        output_dir / "stats.json",
        stats,
        overwrite=args.overwrite,
    )

    emit(f"wrote {display_path(output_dir / 'train.jsonl')}", log_file=args.log_file)
    emit(f"wrote {display_path(output_dir / 'val.jsonl')}", log_file=args.log_file)
    emit(f"wrote {display_path(output_dir / 'stats.json')}", log_file=args.log_file)
    emit(f"wrote {display_path(sample_output)}", log_file=args.log_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
