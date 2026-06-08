#!/usr/bin/env python3
"""Build random or failure-driven training subsets for FD-VIT."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from fdvit.prompts import load_template_library, pick_template, render_prompt
from fdvit_prep_common import ROOT, append_log, display_path, emit, repo_path, utc_now, write_json


DEFAULT_ERROR_WEIGHTS = {
    "commonsense": 1.4,
    "counting": 1.2,
    "spatial": 1.2,
    "ocr_text": 1.1,
    "attribute": 1.0,
    "answer_format": 0.7,
    "hallucination": 1.0,
    "other": 0.8,
    "ambiguous": 0.3,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, help="Processed train JSONL/JSON input")
    parser.add_argument("--failures", default=None, help="Failure JSONL/JSON for failure-driven sampling")
    parser.add_argument("--strategy", required=True, choices=("random", "failure_driven"), help="Sampling strategy")
    parser.add_argument("--n", type=int, required=True, help="Target subset size")
    parser.add_argument("--output", required=True, help="Subset JSONL output path")
    parser.add_argument("--stats_output", default=None, help="Optional stats JSON output path")
    parser.add_argument("--template_file", default=None, help="Optional prompt template file to also emit Qwen JSON")
    parser.add_argument("--template_id", default=None, help="Optional fixed prompt template id for Qwen output")
    parser.add_argument(
        "--template_mode",
        choices=("single", "multi"),
        default="multi",
        help="Prompt assignment mode when writing Qwen output",
    )
    parser.add_argument("--qwen_output", default=None, help="Optional Qwen training JSON output path")
    parser.add_argument(
        "--error_weight",
        action="append",
        default=[],
        help="Override error type weight, e.g. --error_weight counting=1.5",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs if they exist")
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


def parse_error_weights(values: list[str]) -> dict[str, float]:
    weights = dict(DEFAULT_ERROR_WEIGHTS)
    for item in values:
        if "=" not in item:
            raise ValueError(f"invalid --error_weight format: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"invalid empty error type in --error_weight: {item}")
        try:
            weights[key] = float(value)
        except ValueError as exc:
            raise ValueError(f"invalid weight for {key}: {value}") from exc
    return weights


def ensure_train_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered = []
    seen_ids: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        split = str(row.get("split", "") or "")
        if split != "train":
            continue
        sample_id = str(row.get("sample_id", "") or "").strip()
        if not sample_id:
            raise ValueError(f"train row {idx}: missing sample_id")
        if sample_id in seen_ids:
            raise ValueError(f"duplicate sample_id in train data: {sample_id}")
        seen_ids.add(sample_id)
        filtered.append(row)
    if not filtered:
        raise ValueError("no train rows found in input")
    return filtered


def build_train_indexes(rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_sample_id = {str(row["sample_id"]): row for row in rows}
    by_question_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        qid = row.get("question_id")
        if qid is not None:
            by_question_id[str(qid)].append(row)
    return by_sample_id, by_question_id


def enrich_subset_record(
    row: dict[str, Any],
    *,
    strategy: str,
    seed: int,
    source_error_type: str | None = None,
    source_probe_experiment: str | None = None,
) -> dict[str, Any]:
    cloned = json.loads(json.dumps(row, ensure_ascii=False))
    metadata = cloned.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata["sampling_strategy"] = strategy
    metadata["sampling_seed"] = seed
    if source_error_type is not None:
        metadata["source_error_type"] = source_error_type
    if source_probe_experiment is not None:
        metadata["source_probe_experiment"] = source_probe_experiment
    cloned["metadata"] = metadata
    return cloned


def sample_random_subset(rows: list[dict[str, Any]], *, n: int, rng: random.Random, seed: int) -> list[dict[str, Any]]:
    shuffled = list(rows)
    rng.shuffle(shuffled)
    selected = shuffled[: min(n, len(shuffled))]
    return [enrich_subset_record(row, strategy="random", seed=seed) for row in selected]


def choose_failure_candidates(
    failures: list[dict[str, Any]],
    *,
    by_sample_id: dict[str, dict[str, Any]],
    by_question_id: dict[str, list[dict[str, Any]]],
    weights: dict[str, float],
    rng: random.Random,
) -> tuple[list[dict[str, Any]], dict[str, int], int]:
    candidates = []
    missing_matches = 0
    matched_counter: Counter[str] = Counter()
    for failure in failures:
        error_type = str(
            failure.get("error_type_manual")
            or failure.get("error_type_auto")
            or "other"
        ).strip() or "other"

        source_row = None
        sample_id = failure.get("sample_id")
        if sample_id is not None:
            source_row = by_sample_id.get(str(sample_id))
        if source_row is None and failure.get("question_id") is not None:
            matches = by_question_id.get(str(failure.get("question_id")), [])
            if matches:
                source_row = rng.choice(matches)
        if source_row is None:
            missing_matches += 1
            continue

        candidates.append(
            {
                "row": source_row,
                "sample_id": str(source_row["sample_id"]),
                "error_type": error_type,
                "weight": max(0.0, float(weights.get(error_type, 1.0))),
                "source_probe_experiment": failure.get("source_experiment"),
            }
        )
        matched_counter[error_type] += 1
    return candidates, dict(matched_counter), missing_matches


def weighted_unique_sample(
    candidates: list[dict[str, Any]],
    *,
    n: int,
    rng: random.Random,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    pool = list(candidates)
    selected: list[dict[str, Any]] = []
    seen_sample_ids: set[str] = set()
    error_counter: Counter[str] = Counter()

    while pool and len(selected) < n:
        weights = [item["weight"] for item in pool]
        if sum(weights) <= 0:
            rng.shuffle(pool)
            chosen = pool.pop(0)
        else:
            chosen = rng.choices(pool, weights=weights, k=1)[0]
            pool.remove(chosen)

        if chosen["sample_id"] in seen_sample_ids:
            continue
        seen_sample_ids.add(chosen["sample_id"])
        error_type = chosen["error_type"]
        error_counter[error_type] += 1
        selected.append(
            enrich_subset_record(
                chosen["row"],
                strategy="failure_driven",
                seed=seed,
                source_error_type=error_type,
                source_probe_experiment=chosen["source_probe_experiment"],
            )
        )
    return selected, dict(error_counter)


def fill_with_random_remainder(
    current: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    *,
    target_n: int,
    rng: random.Random,
    seed: int,
) -> tuple[list[dict[str, Any]], int]:
    seen = {str(row["sample_id"]) for row in current}
    remainder = [row for row in train_rows if str(row["sample_id"]) not in seen]
    rng.shuffle(remainder)
    fill_needed = max(0, target_n - len(current))
    fillers = remainder[:fill_needed]
    current.extend(
        enrich_subset_record(row, strategy="failure_driven", seed=seed, source_error_type="fallback_random")
        for row in fillers
    )
    return current, len(fillers)


def write_jsonl(path: str | Path, rows: list[dict[str, Any]], *, overwrite: bool) -> Path:
    target = repo_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return target


def build_qwen_rows(
    rows: list[dict[str, Any]],
    *,
    template_file: str,
    template_id: str | None,
    template_mode: str,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    templates = load_template_library(template_file, task="vqa")
    usage: Counter[str] = Counter()
    converted = []
    for idx, row in enumerate(rows):
        position = 0 if template_mode == "single" else idx
        template = pick_template(templates, template_id=template_id, seed=seed, position=position)
        usage[template.template_id] += 1
        prompt = render_prompt(template, question=str(row.get("question", "") or "").strip())
        answer = " ".join(str(row.get("answer", "") or "").split())
        metadata = {
            "dataset": row.get("dataset"),
            "split": row.get("split"),
            "question_id": row.get("question_id"),
            "image_id": row.get("image_id"),
            "template_id": template.template_id,
            "source_sample_id": row.get("sample_id"),
        }
        row_meta = row.get("metadata")
        if isinstance(row_meta, dict):
            metadata.update(row_meta)
        converted.append(
            {
                "id": str(row.get("sample_id")),
                "image": str(row.get("image_path")),
                "conversations": [
                    {"from": "human", "value": prompt},
                    {"from": "gpt", "value": answer},
                ],
                "metadata": metadata,
            }
        )
    return converted, dict(usage)


def write_qwen_json(path: str | Path, rows: list[dict[str, Any]], *, overwrite: bool) -> Path:
    target = repo_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {display_path(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def derive_default_stats_output(output_path: Path) -> Path:
    return output_path.with_suffix(".stats.json")


def derive_default_qwen_output(output_path: Path) -> Path:
    return output_path.with_suffix("").with_name(output_path.stem + "_qwen.json")


def compute_stats(
    subset: list[dict[str, Any]],
    *,
    strategy: str,
    n_requested: int,
    seed: int,
    train_rows: list[dict[str, Any]],
    failures_seen: int,
    matched_failure_counts: dict[str, int] | None,
    selected_failure_counts: dict[str, int] | None,
    fallback_random_count: int,
    missing_failure_matches: int,
    qwen_output: str | None,
    qwen_template_usage: dict[str, int] | None,
) -> dict[str, Any]:
    sample_ids = [str(row.get("sample_id")) for row in subset]
    question_ids = [str(row.get("question_id")) for row in subset if row.get("question_id") is not None]
    split_counts = Counter(str(row.get("split")) for row in subset)
    image_exists = 0
    for row in subset:
        image_path = row.get("image_path")
        if isinstance(image_path, str) and repo_path(image_path).exists():
            image_exists += 1
    source_error_type_counts = Counter()
    for row in subset:
        metadata = row.get("metadata")
        if isinstance(metadata, dict) and metadata.get("source_error_type"):
            source_error_type_counts[str(metadata["source_error_type"])] += 1

    return {
        "created_at": utc_now(),
        "repo_root": ROOT.as_posix(),
        "strategy": strategy,
        "seed": seed,
        "requested_n": n_requested,
        "actual_n": len(subset),
        "train_available": len(train_rows),
        "unique_sample_ids": len(set(sample_ids)),
        "duplicate_sample_id_count": len(sample_ids) - len(set(sample_ids)),
        "unique_question_ids": len(set(question_ids)),
        "split_counts": dict(split_counts),
        "image_exists_count": image_exists,
        "image_exists_ratio": image_exists / max(1, len(subset)),
        "failures_seen": failures_seen,
        "matched_failure_counts": matched_failure_counts or {},
        "selected_failure_counts": selected_failure_counts or {},
        "selected_source_error_type_counts": dict(source_error_type_counts),
        "fallback_random_count": fallback_random_count,
        "missing_failure_matches": missing_failure_matches,
        "qwen_output": qwen_output,
        "qwen_template_usage": qwen_template_usage or {},
    }


def main() -> int:
    args = parse_args()
    try:
        rng = random.Random(args.seed)
        train_rows = ensure_train_rows(read_json_like(args.train))
        weights = parse_error_weights(args.error_weight)

        if args.n <= 0:
            raise ValueError("--n must be positive")

        matched_failure_counts = None
        selected_failure_counts = None
        fallback_random_count = 0
        failures_seen = 0
        missing_failure_matches = 0

        if args.strategy == "random":
            subset = sample_random_subset(train_rows, n=min(args.n, len(train_rows)), rng=rng, seed=args.seed)
        else:
            if not args.failures:
                raise ValueError("--failures is required when --strategy failure_driven")
            failure_rows = read_json_like(args.failures)
            failures_seen = len(failure_rows)
            by_sample_id, by_question_id = build_train_indexes(train_rows)
            candidates, matched_failure_counts, missing_failure_matches = choose_failure_candidates(
                failure_rows,
                by_sample_id=by_sample_id,
                by_question_id=by_question_id,
                weights=weights,
                rng=rng,
            )
            subset, selected_failure_counts = weighted_unique_sample(
                candidates,
                n=min(args.n, len(train_rows)),
                rng=rng,
                seed=args.seed,
            )
            subset, fallback_random_count = fill_with_random_remainder(
                subset,
                train_rows,
                target_n=min(args.n, len(train_rows)),
                rng=rng,
                seed=args.seed,
            )

        output_path = write_jsonl(args.output, subset, overwrite=args.overwrite)

        qwen_output_path = None
        qwen_template_usage = None
        if args.template_file:
            qwen_output = args.qwen_output or derive_default_qwen_output(output_path).as_posix()
            qwen_rows, qwen_template_usage = build_qwen_rows(
                subset,
                template_file=args.template_file,
                template_id=args.template_id,
                template_mode=args.template_mode,
                seed=args.seed,
            )
            qwen_output_path = write_qwen_json(qwen_output, qwen_rows, overwrite=args.overwrite)

        stats = compute_stats(
            subset,
            strategy=args.strategy,
            n_requested=args.n,
            seed=args.seed,
            train_rows=train_rows,
            failures_seen=failures_seen,
            matched_failure_counts=matched_failure_counts,
            selected_failure_counts=selected_failure_counts,
            fallback_random_count=fallback_random_count,
            missing_failure_matches=missing_failure_matches,
            qwen_output=display_path(qwen_output_path) if qwen_output_path else None,
            qwen_template_usage=qwen_template_usage,
        )

        stats_output = args.stats_output or derive_default_stats_output(output_path).as_posix()
        stats_path = write_json(stats_output, stats, overwrite=args.overwrite)

        emit(
            f"wrote {display_path(output_path)} with {len(subset)} rows "
            f"(strategy={args.strategy}, qwen={'yes' if qwen_output_path else 'no'})",
            log_file=args.log_file,
        )
        append_log(
            args.log_file,
            json.dumps(
                {
                    "train": display_path(repo_path(args.train)),
                    "failures": display_path(repo_path(args.failures)) if args.failures else None,
                    "output": display_path(output_path),
                    "stats_output": display_path(stats_path),
                    "qwen_output": display_path(qwen_output_path) if qwen_output_path else None,
                    "strategy": args.strategy,
                    "n": args.n,
                    "seed": args.seed,
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
