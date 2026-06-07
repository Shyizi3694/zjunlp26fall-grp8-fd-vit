"""Qwen model loading helpers for FD-VIT inference."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fdvit_prep_common import append_log, repo_path


@dataclass
class QwenModel:
    model: Any
    processor: Any


def _torch_dtype_from_value(value: str | None) -> Any:
    try:
        import torch
    except Exception:  # pragma: no cover - env-level import guard
        return None

    if value is None:
        return None
    value = value.lower()
    mapping = {
        "auto": torch.float16,
        "float16": torch.float16,
        "half": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
    }
    return mapping.get(value, None)


def _load_model_and_processor(
    *,
    model_id: str,
    local_dir: str | None,
    revision: str | None,
    torch_dtype: str | None,
    device_map: str | None,
    trust_remote_code: bool,
    log_file: str | None,
) -> QwenModel:
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"transformers import failed: {exc}")

    dtype = _torch_dtype_from_value(torch_dtype)
    local_path = str(repo_path(local_dir)) if local_dir else None
    candidates = [local_path, model_id] if local_path and local_path != model_id else [model_id]

    load_base_kwargs = {
        "torch_dtype": dtype if dtype is not None else "auto",
        "trust_remote_code": trust_remote_code,
    }
    if device_map:
        load_base_kwargs["device_map"] = device_map

    last_err: Exception | None = None
    for idx, model_path in enumerate(candidates):
        use_remote_revision = idx > 0 and revision is not None
        model_kwargs = dict(load_base_kwargs)
        processor_kwargs = {}
        if use_remote_revision:
            model_kwargs["revision"] = revision
            processor_kwargs["revision"] = revision
        processor_kwargs["trust_remote_code"] = trust_remote_code

        try:
            model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)
            processor = AutoProcessor.from_pretrained(model_path, **processor_kwargs)
            append_log(
                log_file,
                f"loaded model: source={model_path}, model_id={model_id}, local_dir={local_dir}, revision={revision}",
            )
            return QwenModel(model=model, processor=processor)
        except ValueError as exc:
            last_err = exc
            if model_path == local_path:
                append_log(
                    log_file,
                    f"local candidate {model_path} failed ({exc}), trying remote {model_id}",
                )
                continue
            raise
        except Exception as exc:  # pragma: no cover
            last_err = exc
            if model_path == local_path:
                append_log(
                    log_file,
                    f"local candidate {model_path} failed, trying remote {model_id}: {exc}",
                )
                continue
            raise

    if last_err is not None:
        raise last_err
    raise RuntimeError("no model candidates configured")


def _attach_lora_if_needed(model: Any, *, checkpoint: str | None, log_file: str | None) -> Any:
    if not checkpoint:
        return model
    checkpoint_path = Path(checkpoint)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"LoRA checkpoint not found: {checkpoint}")
    try:
        from peft import PeftModel
    except Exception as exc:  # pragma: no cover - optional path
        raise RuntimeError(f"peft import failed: {exc}")

    tuned = PeftModel.from_pretrained(model, str(checkpoint_path), is_trainable=False)
    append_log(log_file, f"attached LoRA adapter: {checkpoint_path}")
    return tuned


def load_qwen(
    *,
    model_id: str,
    local_dir: str | None = None,
    revision: str | None = None,
    device: str = "auto",
    torch_dtype: str | None = None,
    lora_checkpoint: str | None = None,
    trust_remote_code: bool = True,
    device_map: str | None = None,
    log_file: str | None = None,
) -> QwenModel:
    q = _load_model_and_processor(
        model_id=model_id,
        local_dir=local_dir,
        revision=revision,
        torch_dtype=torch_dtype,
        device_map=device_map,
        trust_remote_code=trust_remote_code,
        log_file=log_file,
    )

    if device != "auto" and hasattr(q.model, "to"):
        try:
            import torch
            if torch.cuda.is_available() or device == "cpu":
                q.model.to(device)
        except Exception:  # pragma: no cover
            pass

    q.model.eval()
    if lora_checkpoint:
        q.model = _attach_lora_if_needed(q.model, checkpoint=lora_checkpoint, log_file=log_file)
    return q
