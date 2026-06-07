#!/usr/bin/env python3
"""Run FD-VIT batch inference for baseline and downstream experiments."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit.evaluation import normalize_answer
from fdvit.inference import build_inference_config, load_records, run_inference
from fdvit.model_qwen import load_qwen
from fdvit.prompts import load_template_library, pick_template, render_prompt
from fdvit_prep_common import append_log, display_path, emit, repo_path, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to inference config YAML/JSON")
    parser.add_argument("--input", required=True, help="Input JSONL/JSON file")
    parser.add_argument("--output", required=True, help="Output predictions JSONL")
    parser.add_argument("--template_id", default=None, help="Force template id")
    parser.add_argument("--template_file", default=None, help="Override prompt template file")
    parser.add_argument("--lora_checkpoint", default=None, help="Optional LoRA checkpoint")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--limit", type=int, default=0, help="Maximum samples")
    parser.add_argument("--resume", action="store_true", help="Resume from existing output file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if exists")
    parser.add_argument("--batch_size", type=int, default=None, help="Override batch size")
    parser.add_argument("--log_file", default=None, help="Optional log file path")
    return parser.parse_args()


def _load_yaml_or_json(path: str | Path) -> dict[str, Any]:
    target = repo_path(path)
    content = target.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    if target.suffix in {".yml", ".yaml"}:
        try:
            import yaml
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"PyYAML import failed: {exc}")
        cfg = yaml.safe_load(content)
    else:
        cfg = json.loads(content)
    if not isinstance(cfg, dict):
        raise ValueError("config must be a mapping")
    return cfg


def _read_existing_output_ids(path: Path) -> set[str]:
    seen: set[str] = set()
    if not path.exists():
        return seen
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        sid = row.get("sample_id")
        if isinstance(sid, str):
            seen.add(sid)
    return seen


def _resolve_output_path(raw_output: str) -> tuple[Path, bool]:
    output_path = repo_path(raw_output)
    return output_path, output_path.exists()


def _write_artifacts(
    output_path: Path,
    args: argparse.Namespace,
    cfg: dict[str, Any],
    model_id: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    run_config_path = output_path.parent / "run_config.yaml"
    try:
        import yaml

        run_config_text = yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True)
    except Exception:
        run_config_text = json.dumps(cfg, ensure_ascii=False, indent=2)
    run_config_path.write_text(run_config_text, encoding="utf-8")

    command_path = output_path.parent / "command.txt"
    command_path.write_text(
        "python " + " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:]) + "\n",
        encoding="utf-8",
    )

    environment_path = output_path.parent / "environment.txt"
    environment_path.write_text(
        json.dumps(
            {
                "created_at": utc_now(),
                "python": sys.version,
                "model_id": model_id,
                "config": str(Path(args.config)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    try:
        cfg = _load_yaml_or_json(args.config)
        model_cfg = cfg.get("model", {}) or {}
        infer_cfg = cfg.get("inference", {}) or {}

        model_id = str(model_cfg.get("model_id", "Qwen/Qwen3-VL-4B-Instruct"))
        generation = build_inference_config(model_cfg.get("generation", {}))

        template_file = args.template_file or infer_cfg.get("template_file") or "prompts/okvqa_templates.json"
        templates = load_template_library(template_file, task="vqa", log_file=args.log_file)

        records = load_records(repo_path(args.input))
        if args.limit and args.limit > 0:
            records = records[: args.limit]

        output_path, output_exists = _resolve_output_path(args.output)
        if output_exists and not (args.overwrite or args.resume):
            raise FileExistsError(f"output exists: {display_path(output_path)}")

        done_ids: set[str] = set()
        if args.resume:
            done_ids = _read_existing_output_ids(output_path)

        selected_records = []
        rendered_prompts = []
        for idx, record in enumerate(records):
            sample_id = record.get("sample_id")
            if isinstance(sample_id, str) and sample_id in done_ids:
                continue

            template = pick_template(
                templates,
                template_id=args.template_id or infer_cfg.get("template_id"),
                seed=args.seed,
                position=idx,
            )
            prompt = render_prompt(template, question=str(record.get("question", "")))
            record["template_id"] = template.template_id
            selected_records.append(record)
            rendered_prompts.append(prompt)

        if not selected_records:
            emit(f"no new samples to run (input={len(records)}, done={len(done_ids)}), skipping inference", log_file=args.log_file)
            return 0

        checkpoint = args.lora_checkpoint or infer_cfg.get("checkpoint")
        bundle = load_qwen(
            model_id=model_id,
            local_dir=model_cfg.get("local_dir"),
            revision=model_cfg.get("revision"),
            device=model_cfg.get("device", "auto"),
            torch_dtype=str(model_cfg.get("torch_dtype", "auto")) if model_cfg.get("torch_dtype") else None,
            lora_checkpoint=checkpoint,
            trust_remote_code=model_cfg.get("trust_remote_code", True),
            device_map=infer_cfg.get("device_map"),
            log_file=args.log_file,
        )

        batch_size = max(1, args.batch_size or int(infer_cfg.get("batch_size", 1)))
        predictions = run_inference(
            records=selected_records,
            prompts=rendered_prompts,
            model_bundle=bundle,
            infer_config=generation,
            model_id=model_id,
            checkpoint=checkpoint,
            seed=args.seed,
            batch_size=batch_size,
            log_file=args.log_file,
        )

        for pred in predictions:
            if pred.get("prediction_raw"):
                pred["normalized_answers"] = [normalize_answer(a) for a in pred.get("answers", []) if isinstance(a, str)]
                pred["prediction"] = pred.get("prediction_raw", "").strip().split("\n")[0].strip()
                pred["normalized_prediction"] = normalize_answer(pred["prediction"])

        if args.overwrite:
            append_mode = "w"
        else:
            append_mode = "a" if (args.resume and output_exists) else "w"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open(append_mode, encoding="utf-8") as handle:
            for row in predictions:
                handle.write(json.dumps(row, ensure_ascii=False) + "\\n")

        _write_artifacts(output_path, args, cfg, model_id)
        emit(f"wrote {len(predictions)} predictions -> {output_path}", log_file=args.log_file)
        append_log(
            args.log_file,
            json.dumps({"num_predictions": len(predictions), "num_input": len(records)}, ensure_ascii=False),
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
