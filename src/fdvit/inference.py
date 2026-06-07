"""Core inference helpers for FD-VIT scripts."""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fdvit.model_qwen import QwenModel
from fdvit_prep_common import append_log


@dataclass(frozen=True)
class InferenceConfig:
    max_new_tokens: int
    temperature: float
    top_p: float = 1.0
    do_sample: bool = False


def build_inference_config(config: dict[str, Any]) -> InferenceConfig:
    max_new_tokens = int(config.get("max_new_tokens", 16))
    temperature = float(config.get("temperature", 0.0))
    top_p = float(config.get("top_p", 1.0))
    do_sample = bool(temperature > 0)
    return InferenceConfig(max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, do_sample=do_sample)


def load_records(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    content = target.read_text(encoding="utf-8").strip()
    if not content:
        return []
    if content[0] == "[":
        payload = json.loads(content)
        if not isinstance(payload, list):
            raise ValueError("input JSONL expected list when parsed as JSON payload")
        return [row for row in payload if isinstance(row, dict)]

    records = []
    for line_no, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"parse error line {line_no}: {exc}") from exc
        if isinstance(row, dict):
            records.append(row)
    return records


def _extract_device(model: Any) -> str:
    if hasattr(model, "device"):
        try:
            return str(model.device)
        except Exception:  # pragma: no cover
            pass
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception:  # pragma: no cover
        pass
    return "cpu"


def _build_inputs(processor: Any, prompt: str, image_path: str) -> dict[str, Any]:
    from PIL import Image

    image = Image.open(image_path).convert("RGB")
    return processor(text=prompt, images=image, return_tensors="pt")


def _safe_decode(processor: Any, prompt: str, generated_ids: Any) -> str:
    raw_output = processor.batch_decode(generated_ids, skip_special_tokens=True)
    if not raw_output:
        return ""
    raw = raw_output[0].strip()
    if prompt and raw.startswith(prompt):
        return raw[len(prompt) :].strip()
    return raw


def run_inference_for_one(
    *,
    model_bundle: QwenModel,
    prompt: str,
    image_path: str,
    config: InferenceConfig,
    log_file: str | None = None,
) -> tuple[str, float]:
    start = time.perf_counter()
    inputs = _build_inputs(model_bundle.processor, prompt, image_path)

    if hasattr(model_bundle.model, "device"):
        for key, value in inputs.items():
            if hasattr(value, "to"):
                inputs[key] = value.to(model_bundle.model.device)

    generation_kwargs = {
        "max_new_tokens": config.max_new_tokens,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "do_sample": config.do_sample,
    }
    pad_token_id = getattr(model_bundle.processor.tokenizer, "pad_token_id", None)
    eos_token_id = getattr(model_bundle.processor.tokenizer, "eos_token_id", None)
    if pad_token_id is not None:
        generation_kwargs["pad_token_id"] = pad_token_id
    if eos_token_id is not None:
        generation_kwargs["eos_token_id"] = eos_token_id

    try:
        import torch

        with torch.no_grad():
            generated = model_bundle.model.generate(**inputs, **generation_kwargs)
    except Exception as exc:  # noqa: BLE001
        if "no module named 'torch'" in str(type(exc)) or "torch" in str(exc).lower():
            raise
        raise

    raw = _safe_decode(model_bundle.processor, prompt, generated)
    latency = time.perf_counter() - start
    append_log(log_file, f"infer one: latency={latency:.4f}, prompt_len={len(prompt)}")
    return raw, latency


def run_inference(
    *,
    records: list[dict[str, Any]],
    prompts: list[str],
    model_bundle: QwenModel,
    infer_config: InferenceConfig,
    model_id: str,
    checkpoint: str | None,
    seed: int = 42,
    start: int = 0,
    batch_size: int = 1,
    experiment_id: str | None = None,
    log_file: str | None = None,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    _ = rng.random()
    completed: list[dict[str, Any]] = []
    total = min(len(records), len(prompts))
    device = _extract_device(model_bundle.model)

    for idx in range(start, total):
        record = records[idx]
        prompt = prompts[idx]
        result: dict[str, Any] = {
            "sample_id": record.get("sample_id"),
            "dataset": record.get("dataset"),
            "split": record.get("split"),
            "question_id": record.get("question_id"),
            "image_id": record.get("image_id"),
            "image_path": record.get("image_path"),
            "question": record.get("question"),
            "answers": record.get("answers", []),
            "prompt": prompt,
            "template_id": record.get("template_id"),
            "prediction_raw": "",
            "prediction": "",
            "normalized_prediction": "",
            "normalized_answers": [],
            "model_id": model_id,
            "checkpoint": checkpoint,
            "generation_config": {
                "max_new_tokens": infer_config.max_new_tokens,
                "temperature": infer_config.temperature,
                "top_p": infer_config.top_p,
                "batch_size": batch_size,
                "do_sample": infer_config.do_sample,
            },
            "experiment_id": experiment_id,
            "runtime": {
                "latency_sec": 0.0,
                "device": device,
            },
            "error": None,
        }
        try:
            image_path = record.get("image_path")
            if not isinstance(image_path, str):
                raise ValueError("missing image_path")
            pred_raw, latency = run_inference_for_one(
                model_bundle=model_bundle,
                prompt=prompt,
                image_path=image_path,
                config=infer_config,
                log_file=log_file,
            )
            result["prediction_raw"] = pred_raw
            result["prediction"] = pred_raw.strip().split("\n")[0].strip()
            result["runtime"]["latency_sec"] = latency
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"{type(exc).__name__}: {exc}"

        completed.append(result)
        if (idx - start) % batch_size == batch_size - 1 or idx == total - 1:
            append_log(log_file, f"progress: {idx - start + 1}/{total}")
    return completed
