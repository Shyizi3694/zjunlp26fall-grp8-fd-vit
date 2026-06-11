#!/usr/bin/env python3
"""Run Qwen3-VL GUI grounding inference for the optional B01 demo."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit.gui_grounding import evaluate_gui_record
from fdvit.model_qwen import load_qwen
from fdvit_prep_common import append_log, display_path, emit, repo_path, utc_now


DEFAULT_TEMPLATE_FILE = "prompts/gui_grounding_templates.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/gui_grounding.yaml", help="YAML/JSON config path")
    parser.add_argument("--input", required=True, help="Processed GUI JSONL/JSON")
    parser.add_argument("--output", required=True, help="Output predictions JSONL")
    parser.add_argument("--model_id", default=None, help="Override model id")
    parser.add_argument("--local_dir", default=None, help="Override local model directory")
    parser.add_argument("--lora_checkpoint", default=None, help="Optional LoRA checkpoint")
    parser.add_argument("--template_file", default=None, help="Override GUI template JSON")
    parser.add_argument("--template_id", default=None, help="Override template id")
    parser.add_argument("--coordinate_mode", choices=["auto", "pixel", "normalized", "qwen_1000"], default=None)
    parser.add_argument("--seed", type=int, default=42, help="Recorded seed")
    parser.add_argument("--limit", type=int, default=0, help="Maximum samples (0 means all)")
    parser.add_argument("--resume", action="store_true", help="Skip sample_ids already in output")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists")
    parser.add_argument("--dry_run", action="store_true", help="Validate inputs/prompts without loading model")
    parser.add_argument("--log_file", default=None, help="Optional text log")
    return parser.parse_args()


def load_yaml_or_json(path: str | Path) -> dict[str, Any]:
    target = repo_path(path)
    if not target.exists():
        return {}
    content = target.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    if target.suffix in {".yaml", ".yml"}:
        import yaml

        payload = yaml.safe_load(content)
    else:
        payload = json.loads(content)
    if not isinstance(payload, dict):
        raise ValueError("config must be a mapping")
    return payload


def read_json_like(path: str | Path) -> list[dict[str, Any]]:
    target = repo_path(path)
    raw = target.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw[0] == "[":
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("input JSON must be a list")
        return [row for row in payload if isinstance(row, dict)]
    rows = []
    for line_no, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"line {line_no}: parse error: {exc}") from exc
        if isinstance(row, dict):
            rows.append(row)
    return rows


def read_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        sample_id = row.get("sample_id")
        if isinstance(sample_id, str):
            ids.add(sample_id)
    return ids


def load_templates(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(repo_path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("template file must contain a list")
    templates = []
    seen = set()
    for item in payload:
        if not isinstance(item, dict):
            continue
        template_id = item.get("template_id")
        text = item.get("text")
        if not isinstance(template_id, str) or not template_id.strip():
            raise ValueError("template_id must be a non-empty string")
        if template_id in seen:
            raise ValueError(f"duplicate template_id: {template_id}")
        if item.get("task") != "gui_grounding":
            raise ValueError(f"{template_id}: task must be gui_grounding")
        if not isinstance(text, str) or "<image>" not in text or "{instruction}" not in text:
            raise ValueError(f"{template_id}: text must contain <image> and {{instruction}}")
        seen.add(template_id)
        templates.append(item)
    if not templates:
        raise ValueError("no GUI grounding templates found")
    return templates


def pick_template(templates: list[dict[str, Any]], template_id: str | None) -> dict[str, Any]:
    if template_id is None:
        return templates[0]
    for template in templates:
        if template["template_id"] == template_id:
            return template
    raise ValueError(f"template_id not found: {template_id}")


def render_prompt(template: dict[str, Any], record: dict[str, Any]) -> str:
    return str(template["text"]).format(
        instruction=record.get("instruction", ""),
        image_width=record.get("image_size", ["", ""])[0],
        image_height=record.get("image_size", ["", ""])[1],
    )


def user_text(prompt: str) -> str:
    return prompt.replace("<image>", "").strip()


def build_inputs(processor: Any, prompt: str, image_path: str) -> tuple[dict[str, Any], int]:
    from PIL import Image

    image = Image.open(repo_path(image_path)).convert("RGB")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": user_text(prompt)},
            ],
        }
    ]
    chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    encoded = processor(text=[chat_text], images=[image], return_tensors="pt")
    return encoded, int(encoded["input_ids"].shape[1])


def decode_new_tokens(processor: Any, generated: Any, prompt_length: int) -> str:
    new_tokens = generated[:, prompt_length:] if prompt_length > 0 else generated
    decoded = processor.batch_decode(new_tokens, skip_special_tokens=True)
    return decoded[0].strip() if decoded else ""


def infer_one(model_bundle: Any, prompt: str, image_path: str, generation: dict[str, Any]) -> tuple[str, float]:
    start = time.perf_counter()
    inputs, prompt_length = build_inputs(model_bundle.processor, prompt, image_path)
    if hasattr(model_bundle.model, "device"):
        for key, value in inputs.items():
            if hasattr(value, "to"):
                inputs[key] = value.to(model_bundle.model.device)

    generation_kwargs = {
        "max_new_tokens": int(generation.get("max_new_tokens", 32)),
        "temperature": float(generation.get("temperature", 0.0)),
        "top_p": float(generation.get("top_p", 1.0)),
        "do_sample": float(generation.get("temperature", 0.0)) > 0,
    }
    tokenizer = getattr(model_bundle.processor, "tokenizer", None)
    if tokenizer is not None:
        if getattr(tokenizer, "pad_token_id", None) is not None:
            generation_kwargs["pad_token_id"] = tokenizer.pad_token_id
        if getattr(tokenizer, "eos_token_id", None) is not None:
            generation_kwargs["eos_token_id"] = tokenizer.eos_token_id

    import torch

    with torch.no_grad():
        generated = model_bundle.model.generate(**inputs, **generation_kwargs)
    return decode_new_tokens(model_bundle.processor, generated, prompt_length), time.perf_counter() - start


def module_version(name: str) -> str | None:
    try:
        module = importlib.import_module(name)
    except Exception:
        return None
    return getattr(module, "__version__", None)


def write_run_artifacts(output_path: Path, args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import yaml

        config_text = yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True)
    except Exception:
        config_text = json.dumps(cfg, indent=2, ensure_ascii=False)
    (output_path.parent / "run_config.yaml").write_text(config_text, encoding="utf-8")
    (output_path.parent / "command.txt").write_text(
        "python " + " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:]) + "\n",
        encoding="utf-8",
    )
    env = {
        "created_at": utc_now(),
        "python": sys.version,
        "cwd": os.getcwd(),
        "versions": {
            "torch": module_version("torch"),
            "transformers": module_version("transformers"),
            "peft": module_version("peft"),
            "qwen_vl_utils": module_version("qwen_vl_utils"),
            "PIL": module_version("PIL"),
        },
    }
    (output_path.parent / "environment.txt").write_text(json.dumps(env, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        cfg = load_yaml_or_json(args.config)
        model_cfg = cfg.get("model", {}) or {}
        infer_cfg = cfg.get("inference", {}) or {}
        experiment_id = str(cfg.get("experiment_id", "B01_gui_grounding_demo"))
        model_id = args.model_id or model_cfg.get("model_id") or "Qwen/Qwen3-VL-4B-Instruct"
        local_dir = args.local_dir if args.local_dir is not None else model_cfg.get("local_dir")
        checkpoint = args.lora_checkpoint if args.lora_checkpoint is not None else infer_cfg.get("checkpoint")
        template_file = args.template_file or infer_cfg.get("template_file") or DEFAULT_TEMPLATE_FILE
        template_id = args.template_id or infer_cfg.get("template_id")
        coordinate_mode = args.coordinate_mode or infer_cfg.get("coordinate_mode") or "auto"
        generation = model_cfg.get("generation", {}) or {}

        templates = load_templates(template_file)
        template = pick_template(templates, template_id)
        rows = read_json_like(args.input)
        if args.limit > 0:
            rows = rows[: args.limit]

        output_path = repo_path(args.output)
        if output_path.exists() and not (args.overwrite or args.resume):
            raise FileExistsError(f"output exists: {display_path(output_path)}")
        done_ids = read_existing_ids(output_path) if args.resume else set()
        todo = [row for row in rows if str(row.get("sample_id")) not in done_ids]

        prompts = [render_prompt(template, row) for row in todo]
        if args.dry_run:
            emit(f"[dry_run] would run {len(todo)} GUI grounding samples with template {template['template_id']}")
            return 0

        bundle = load_qwen(
            model_id=str(model_id),
            local_dir=local_dir,
            revision=model_cfg.get("revision"),
            device=model_cfg.get("device", "auto"),
            torch_dtype=str(model_cfg.get("torch_dtype")) if model_cfg.get("torch_dtype") else None,
            lora_checkpoint=checkpoint,
            trust_remote_code=bool(model_cfg.get("trust_remote_code", True)),
            device_map=infer_cfg.get("device_map"),
            log_file=args.log_file,
        )

        mode = "w" if args.overwrite or not args.resume else "a"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open(mode, encoding="utf-8") as handle:
            for idx, (row, prompt) in enumerate(zip(todo, prompts, strict=True), start=1):
                result = {
                    **row,
                    "prompt": prompt,
                    "template_id": template["template_id"],
                    "prediction_raw": "",
                    "prediction_point": None,
                    "parse_success": False,
                    "point_in_bbox": False,
                    "center_distance_norm": None,
                    "model_id": model_id,
                    "checkpoint": checkpoint,
                    "experiment_id": experiment_id,
                    "generation_config": generation,
                    "runtime": {"latency_sec": 0.0},
                    "error": None,
                }
                try:
                    raw, latency = infer_one(bundle, prompt, str(row["image_path"]), generation)
                    result["prediction_raw"] = raw
                    result["runtime"]["latency_sec"] = latency
                    result.update(evaluate_gui_record(result, coordinate_mode=coordinate_mode))
                except Exception as exc:  # noqa: BLE001
                    result["error"] = f"{type(exc).__name__}: {exc}"
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
                if idx % 10 == 0 or idx == len(todo):
                    append_log(args.log_file, f"progress: {idx}/{len(todo)}")

        write_run_artifacts(output_path, args, cfg)
        emit(f"wrote {len(todo)} GUI predictions -> {display_path(output_path)}", log_file=args.log_file)
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {type(exc).__name__}: {exc}")
        append_log(args.log_file, f"ERROR: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
