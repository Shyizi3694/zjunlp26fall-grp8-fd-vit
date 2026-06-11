#!/usr/bin/env python3
"""Prepare a small ScreenSpot-Pro GUI grounding split for the optional bonus."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit.gui_grounding import bbox_center, coerce_bbox, coerce_image_size
from fdvit_prep_common import ROOT, append_log, display_path, emit, repo_path, utc_now, write_json


DEFAULT_REPO_ID = "likaixin/ScreenSpot-Pro"
DEFAULT_TASKS = ["vscode_macos"]
DEFAULT_RAW_DIR = "data/raw/gui/screenspot_pro"
DEFAULT_OUTPUT = "data/processed/gui/val_small.jsonl"
DEFAULT_SAMPLE_OUTPUT = "data/samples/gui_grounding_5.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo_id", default=DEFAULT_REPO_ID, help="Hugging Face dataset repo id")
    parser.add_argument("--raw_dir", default=DEFAULT_RAW_DIR, help="Raw dataset directory")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Processed GUI JSONL output")
    parser.add_argument("--sample_output", default=DEFAULT_SAMPLE_OUTPUT, help="Small sample JSONL output")
    parser.add_argument("--tasks", nargs="+", default=DEFAULT_TASKS, help="Annotation task names, or 'all'")
    parser.add_argument("--split", default="val", choices=["train", "val", "test", "dev"], help="Project split label")
    parser.add_argument("--limit", type=int, default=50, help="Maximum processed examples (0 means all selected tasks)")
    parser.add_argument("--sample_size", type=int, default=5, help="Number of records for data/samples")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic shuffling")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle examples before applying --limit")
    parser.add_argument("--download", action="store_true", help="Download annotation files from Hugging Face")
    parser.add_argument("--download_images", action="store_true", help="Download selected images from Hugging Face")
    parser.add_argument("--local_files_only", action="store_true", help="Use only cached Hugging Face files")
    parser.add_argument("--check_images", action="store_true", help="Open selected images and verify/repair image_size")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs if they already exist")
    parser.add_argument("--dry_run", action="store_true", help="Plan work without writing outputs")
    parser.add_argument("--log_file", default=None, help="Optional text log")
    return parser.parse_args()


def _import_hf() -> tuple[Any, Any]:
    try:
        from huggingface_hub import HfApi, hf_hub_download
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"huggingface_hub import failed: {exc}") from exc
    return HfApi, hf_hub_download


def discover_tasks(repo_id: str, *, local_files_only: bool) -> list[str]:
    if local_files_only:
        raise ValueError("--tasks all requires network access to list repo files")
    HfApi, _ = _import_hf()
    files = HfApi().list_repo_files(repo_id=repo_id, repo_type="dataset")
    tasks = []
    for name in files:
        if name.startswith("annotations/") and name.endswith(".json"):
            tasks.append(Path(name).stem)
    if not tasks:
        raise ValueError(f"no annotation tasks found in {repo_id}")
    return sorted(tasks)


def resolve_tasks(raw_tasks: list[str], *, repo_id: str, local_files_only: bool) -> list[str]:
    if len(raw_tasks) == 1 and raw_tasks[0].lower() == "all":
        return discover_tasks(repo_id, local_files_only=local_files_only)
    return [task[:-5] if task.endswith(".json") else task for task in raw_tasks]


def download_repo_file(
    *,
    repo_id: str,
    filename: str,
    raw_dir: Path,
    local_files_only: bool,
    dry_run: bool,
    log_file: str | None,
) -> Path:
    target = raw_dir / filename
    if dry_run:
        emit(f"[dry_run] would download {repo_id}:{filename} -> {display_path(target)}", log_file=log_file)
        return target
    _, hf_hub_download = _import_hf()
    path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        repo_type="dataset",
        local_dir=raw_dir.as_posix(),
        local_files_only=local_files_only,
    )
    return Path(path)


def annotation_path(raw_dir: Path, task: str) -> Path:
    return raw_dir / "annotations" / f"{task}.json"


def load_annotation(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"annotation not found: {display_path(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"annotation must be a list: {display_path(path)}")
    return [item for item in payload if isinstance(item, dict)]


def image_repo_path(record: dict[str, Any]) -> str:
    filename = str(record.get("img_filename") or record.get("image") or record.get("image_path") or "").strip()
    if not filename:
        raise ValueError("annotation record missing img_filename")
    if filename.startswith("images/"):
        return filename
    return f"images/{filename}"


def local_image_path(raw_dir: Path, record: dict[str, Any]) -> Path:
    return raw_dir / image_repo_path(record)


def normalized_instruction(record: dict[str, Any]) -> str:
    for key in ("instruction", "query", "task", "text"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    raise ValueError("annotation record missing instruction")


def read_bbox(record: dict[str, Any]) -> list[float]:
    bbox = coerce_bbox(record.get("bbox"))
    if bbox is None:
        raise ValueError("annotation record has invalid bbox")
    return bbox


def read_image_size(record: dict[str, Any], image_path: Path | None, *, check_images: bool) -> list[int]:
    image_size = coerce_image_size(record.get("img_size") or record.get("image_size"))
    if check_images and image_path is not None and image_path.exists():
        try:
            from PIL import Image

            with Image.open(image_path) as image:
                return [int(image.width), int(image.height)]
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"failed to inspect image {display_path(image_path)}: {exc}") from exc
    if image_size is None:
        raise ValueError("annotation record has invalid image size")
    return image_size


def control_type(record: dict[str, Any]) -> str:
    for key in ("ui_type", "control_type", "type"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def convert_record(
    record: dict[str, Any],
    *,
    idx: int,
    task: str,
    repo_id: str,
    split: str,
    raw_dir: Path,
    check_images: bool,
) -> dict[str, Any]:
    image_path = local_image_path(raw_dir, record)
    bbox = read_bbox(record)
    image_size = read_image_size(record, image_path, check_images=check_images)
    point = bbox_center(bbox)
    sample_id = f"gui_{split}_{idx:06d}"
    return {
        "sample_id": sample_id,
        "dataset": "screenspot_pro",
        "split": split,
        "image_path": display_path(image_path),
        "instruction": normalized_instruction(record),
        "bbox": [round(x, 4) for x in bbox],
        "point": [round(point[0], 4), round(point[1], 4)],
        "image_size": image_size,
        "control_type": control_type(record),
        "metadata": {
            "source_repo": repo_id,
            "source_task": task,
            "source_id": record.get("id"),
            "img_filename": record.get("img_filename"),
            "group": record.get("group"),
            "platform": record.get("platform"),
            "application": record.get("application"),
            "language": record.get("language"),
        },
    }


def write_jsonl(path: str | Path, records: list[dict[str, Any]], *, overwrite: bool, dry_run: bool) -> None:
    target = repo_path(path)
    if dry_run:
        emit(f"[dry_run] would write {len(records)} records to {display_path(target)}")
        return
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    try:
        raw_dir = repo_path(args.raw_dir)
        tasks = resolve_tasks(args.tasks, repo_id=args.repo_id, local_files_only=args.local_files_only)
        if not args.dry_run:
            raw_dir.mkdir(parents=True, exist_ok=True)

        annotation_counts: dict[str, int] = {}
        raw_records: list[tuple[str, dict[str, Any]]] = []
        for task in tasks:
            if args.download:
                download_repo_file(
                    repo_id=args.repo_id,
                    filename=f"annotations/{task}.json",
                    raw_dir=raw_dir,
                    local_files_only=args.local_files_only,
                    dry_run=args.dry_run,
                    log_file=args.log_file,
                )
            rows = [] if args.dry_run else load_annotation(annotation_path(raw_dir, task))
            annotation_counts[task] = len(rows)
            raw_records.extend((task, row) for row in rows)

        rng = random.Random(args.seed)
        if args.shuffle:
            rng.shuffle(raw_records)
        if args.limit > 0:
            raw_records = raw_records[: args.limit]

        if args.download_images:
            seen_images: set[str] = set()
            for _, record in raw_records:
                filename = image_repo_path(record)
                if filename in seen_images:
                    continue
                seen_images.add(filename)
                download_repo_file(
                    repo_id=args.repo_id,
                    filename=filename,
                    raw_dir=raw_dir,
                    local_files_only=args.local_files_only,
                    dry_run=args.dry_run,
                    log_file=args.log_file,
                )

        processed = [
            convert_record(
                record,
                idx=idx,
                task=task,
                repo_id=args.repo_id,
                split=args.split,
                raw_dir=raw_dir,
                check_images=args.check_images,
            )
            for idx, (task, record) in enumerate(raw_records, start=1)
        ]

        write_jsonl(args.output, processed, overwrite=args.overwrite, dry_run=args.dry_run)
        sample_records = processed[: max(0, args.sample_size)]
        write_jsonl(args.sample_output, sample_records, overwrite=args.overwrite, dry_run=args.dry_run)

        summary = {
            "created_at": utc_now(),
            "repo_root": ROOT.as_posix(),
            "repo_id": args.repo_id,
            "raw_dir": display_path(raw_dir),
            "tasks": tasks,
            "annotation_counts": annotation_counts,
            "seed": args.seed,
            "shuffle": args.shuffle,
            "limit": args.limit,
            "num_records": len(processed),
            "output": display_path(args.output),
            "sample_output": display_path(args.sample_output),
            "download": args.download,
            "download_images": args.download_images,
            "dry_run": args.dry_run,
        }
        summary_path = repo_path(args.output).with_suffix(".summary.json")
        if args.dry_run:
            emit(f"[dry_run] would write summary to {display_path(summary_path)}", log_file=args.log_file)
        else:
            write_json(summary_path, summary, overwrite=args.overwrite)
        append_log(args.log_file, json.dumps(summary, ensure_ascii=False))
        emit(f"prepared {len(processed)} GUI grounding records -> {display_path(args.output)}", log_file=args.log_file)
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {type(exc).__name__}: {exc}")
        append_log(args.log_file, f"ERROR: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
