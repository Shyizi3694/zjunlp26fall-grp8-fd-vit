#!/usr/bin/env python3
"""Prepare and validate raw OK-VQA/COCO assets for FD-VIT."""

from __future__ import annotations

import argparse
import json
import random
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from fdvit_prep_common import ROOT, display_path, emit, repo_path, safe_mkdir, utc_now, write_json


OKVQA_FILES = [
    {
        "split": "train",
        "kind": "questions",
        "file": "OpenEnded_mscoco_train2014_questions.json",
        "url": "https://okvqa.allenai.org/static/data/OpenEnded_mscoco_train2014_questions.json.zip",
        "top_level_key": "questions",
    },
    {
        "split": "train",
        "kind": "annotations",
        "file": "mscoco_train2014_annotations.json",
        "url": "https://okvqa.allenai.org/static/data/mscoco_train2014_annotations.json.zip",
        "top_level_key": "annotations",
    },
    {
        "split": "val",
        "kind": "questions",
        "file": "OpenEnded_mscoco_val2014_questions.json",
        "url": "https://okvqa.allenai.org/static/data/OpenEnded_mscoco_val2014_questions.json.zip",
        "top_level_key": "questions",
    },
    {
        "split": "val",
        "kind": "annotations",
        "file": "mscoco_val2014_annotations.json",
        "url": "https://okvqa.allenai.org/static/data/mscoco_val2014_annotations.json.zip",
        "top_level_key": "annotations",
    },
]

COCO_IMAGES = [
    {
        "split": "train",
        "archive": "train2014.zip",
        "url": "http://images.cocodataset.org/zips/train2014.zip",
        "directory": "train2014",
    },
    {
        "split": "val",
        "archive": "val2014.zip",
        "url": "http://images.cocodataset.org/zips/val2014.zip",
        "directory": "val2014",
    },
]


def download(url: str, target: Path, *, overwrite: bool, dry_run: bool, log_file: str | None) -> dict[str, Any]:
    if target.exists() and not overwrite:
        return {"url": url, "target": display_path(target), "status": "exists"}
    if dry_run:
        return {"url": url, "target": display_path(target), "status": "planned"}
    target.parent.mkdir(parents=True, exist_ok=True)
    emit(f"downloading {url}", log_file=log_file)
    try:
        urllib.request.urlretrieve(url, target)  # noqa: S310 - project setup script downloads known public assets.
    except Exception as exc:  # noqa: BLE001
        return {"url": url, "target": display_path(target), "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
    return {"url": url, "target": display_path(target), "status": "downloaded", "bytes": target.stat().st_size}


def extract_zip(archive: Path, target_dir: Path, *, dry_run: bool, log_file: str | None) -> dict[str, Any]:
    if dry_run:
        return {"archive": display_path(archive), "target_dir": display_path(target_dir), "status": "planned"}
    if not archive.exists():
        return {"archive": display_path(archive), "target_dir": display_path(target_dir), "status": "missing_archive"}
    target_dir.mkdir(parents=True, exist_ok=True)
    emit(f"extracting {display_path(archive)}", log_file=log_file)
    with zipfile.ZipFile(archive) as zipped:
        target_root = target_dir.resolve()
        for member in zipped.infolist():
            destination = (target_dir / member.filename).resolve()
            if target_root != destination and target_root not in destination.parents:
                return {
                    "archive": display_path(archive),
                    "target_dir": display_path(target_dir),
                    "status": "failed",
                    "error": f"unsafe zip member path: {member.filename}",
                }
        zipped.extractall(target_dir)
    return {"archive": display_path(archive), "target_dir": display_path(target_dir), "status": "extracted"}


def inspect_json(path: Path, top_level_key: str) -> dict[str, Any]:
    result: dict[str, Any] = {"path": display_path(path), "exists": path.exists(), "records": None, "error": None}
    if not path.exists():
        return result
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = payload.get(top_level_key)
        result["records"] = len(records) if isinstance(records, list) else None
        result["has_expected_key"] = isinstance(records, list)
        result["bytes"] = path.stat().st_size
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def inspect_images(image_root: Path, *, seed: int, limit: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    checks = []
    for resource in COCO_IMAGES:
        directory = image_root / resource["directory"]
        images = sorted(directory.glob("*.jpg")) if directory.exists() else []
        sample = [display_path(path) for path in rng.sample(images, min(limit, len(images)))] if images else []
        checks.append(
            {
                "split": resource["split"],
                "path": display_path(directory),
                "exists": directory.exists(),
                "jpg_count": len(images),
                "sample": sample,
            }
        )
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw_dir", default="data/raw", help="raw data root")
    parser.add_argument("--image_root", default="data/raw/coco", help="COCO image root")
    parser.add_argument("--download_annotations", action="store_true", help="download OK-VQA question/annotation zip files")
    parser.add_argument("--download_coco", action="store_true", help="download COCO train2014/val2014 image zips")
    parser.add_argument("--seed", type=int, default=42, help="seed for image sample checks")
    parser.add_argument("--limit", type=int, default=10, help="number of image paths sampled per split")
    parser.add_argument("--output", default="logs/raw_data_prepare.json", help="JSON summary path")
    parser.add_argument("--overwrite", action="store_true", help="overwrite downloads and --output when needed")
    parser.add_argument("--dry_run", action="store_true", help="show actions without creating files or downloading")
    parser.add_argument("--log_file", default=None, help="optional text log path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_dir = repo_path(args.raw_dir)
    okvqa_dir = raw_dir / "okvqa"
    image_root = repo_path(args.image_root)
    download_dir = raw_dir / "_downloads"

    summary: dict[str, Any] = {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "dry_run": args.dry_run,
        "raw_dir": display_path(raw_dir),
        "image_root": display_path(image_root),
        "resources": {
            "okvqa": OKVQA_FILES,
            "coco": COCO_IMAGES,
        },
        "directories": [],
        "downloads": [],
        "extractions": [],
        "checks": {},
    }

    for directory in [raw_dir, okvqa_dir, image_root, image_root / "train2014", image_root / "val2014", download_dir]:
        summary["directories"].append({"path": display_path(directory), "status": safe_mkdir(directory, dry_run=args.dry_run)})

    if args.download_annotations:
        for resource in OKVQA_FILES:
            archive = download_dir / Path(resource["url"]).name
            summary["downloads"].append(
                download(resource["url"], archive, overwrite=args.overwrite, dry_run=args.dry_run, log_file=args.log_file)
            )
            summary["extractions"].append(extract_zip(archive, okvqa_dir, dry_run=args.dry_run, log_file=args.log_file))

    if args.download_coco:
        for resource in COCO_IMAGES:
            archive = download_dir / resource["archive"]
            summary["downloads"].append(
                download(resource["url"], archive, overwrite=args.overwrite, dry_run=args.dry_run, log_file=args.log_file)
            )
            summary["extractions"].append(extract_zip(archive, image_root, dry_run=args.dry_run, log_file=args.log_file))

    okvqa_checks = []
    for resource in OKVQA_FILES:
        okvqa_checks.append(inspect_json(okvqa_dir / resource["file"], resource["top_level_key"]))
    image_checks = inspect_images(image_root, seed=args.seed, limit=args.limit)
    summary["checks"] = {"okvqa_files": okvqa_checks, "coco_images": image_checks}

    missing_okvqa = [item["path"] for item in okvqa_checks if not item["exists"]]
    missing_images = [item["path"] for item in image_checks if not item["exists"] or item["jpg_count"] == 0]
    summary["ready_for_prepare_okvqa"] = not missing_okvqa and not missing_images
    summary["missing"] = {"okvqa_files": missing_okvqa, "coco_image_dirs": missing_images}
    failed_downloads = [item for item in summary["downloads"] if item["status"] == "failed"]
    failed_extractions = [item for item in summary["extractions"] if item["status"] == "failed"]
    summary["status"] = "passed" if summary["ready_for_prepare_okvqa"] else "needs_data"
    if failed_downloads or failed_extractions:
        summary["status"] = "failed"

    target = write_json(args.output, summary, overwrite=args.overwrite)
    emit(f"wrote {display_path(target)}", log_file=args.log_file)
    if summary["status"] != "passed":
        emit("raw data is not complete yet; inspect the JSON summary for missing files", log_file=args.log_file)
    return 1 if summary["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
