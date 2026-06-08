#!/usr/bin/env python3
"""Train a Qwen3-VL LoRA/QLoRA adapter from a YAML config."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdvit_prep_common import append_log, display_path, emit, repo_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Resolved training YAML config path")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
    return parser.parse_args()


def load_yaml_or_json(path: str | Path) -> dict[str, Any]:
    target = repo_path(path)
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


def set_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def resolve_torch_dtype(value: str | None) -> Any:
    try:
        import torch
    except Exception:
        return None
    if value is None:
        return None
    mapping = {
        "auto": None,
        "float16": torch.float16,
        "half": torch.float16,
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float32": torch.float32,
    }
    return mapping.get(str(value).lower())


def to_file_uri(path: str | Path) -> str:
    return Path(repo_path(path)).resolve().as_uri()


def sanitize_user_text(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("<image>"):
        stripped = stripped[len("<image>") :].lstrip()
    return stripped


@dataclass
class TrainSample:
    sample_id: str
    image_path: str
    user_text: str
    assistant_text: str


def load_train_samples(path: str | Path) -> list[TrainSample]:
    target = repo_path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("train file must be a JSON list")
    samples: list[TrainSample] = []
    for idx, row in enumerate(payload, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {idx}: expected object")
        sample_id = str(row.get("id", "") or "").strip()
        image_path = str(row.get("image", "") or "").strip()
        conversations = row.get("conversations")
        if not sample_id or not image_path or not isinstance(conversations, list) or len(conversations) < 2:
            raise ValueError(f"row {idx}: missing id/image/conversations")
        user_turn = conversations[0]
        assistant_turn = conversations[1]
        if not isinstance(user_turn, dict) or not isinstance(assistant_turn, dict):
            raise ValueError(f"row {idx}: invalid conversation turn")
        user_text = sanitize_user_text(str(user_turn.get("value", "") or ""))
        assistant_text = " ".join(str(assistant_turn.get("value", "") or "").split())
        samples.append(
            TrainSample(
                sample_id=sample_id,
                image_path=image_path,
                user_text=user_text,
                assistant_text=assistant_text,
            )
        )
    return samples


class QwenVLTrainDataset:
    def __init__(self, rows: list[TrainSample]) -> None:
        self.rows = rows

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> dict[str, str]:
        row = self.rows[idx]
        return {
            "sample_id": row.sample_id,
            "image_path": row.image_path,
            "user_text": row.user_text,
            "assistant_text": row.assistant_text,
        }


class QwenVLDataCollator:
    def __init__(self, processor: Any, *, max_pixels: int | None = None) -> None:
        self.processor = processor
        self.image_patch_size = getattr(processor.image_processor, "patch_size", 16)
        self.max_pixels = max_pixels
        from qwen_vl_utils import process_vision_info

        self.process_vision_info = process_vision_info

    def _message_pair(self, feature: dict[str, str], *, include_assistant: bool) -> list[dict[str, Any]]:
        image_item: dict[str, Any] = {
            "type": "image",
            "image": to_file_uri(feature["image_path"]),
        }
        if self.max_pixels is not None:
            image_item["max_pixels"] = self.max_pixels

        messages = [
            {
                "role": "user",
                "content": [
                    image_item,
                    {"type": "text", "text": feature["user_text"]},
                ],
            }
        ]
        if include_assistant:
            messages.append(
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": feature["assistant_text"]}],
                }
            )
        return messages

    def __call__(self, features: list[dict[str, str]]) -> dict[str, Any]:
        full_texts: list[str] = []
        prompt_texts: list[str] = []
        images_batch: list[Any] = []
        for feature in features:
            full_messages = self._message_pair(feature, include_assistant=True)
            prompt_messages = self._message_pair(feature, include_assistant=False)

            full_texts.append(self.processor.apply_chat_template(full_messages, tokenize=False, add_generation_prompt=False))
            prompt_texts.append(self.processor.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True))

            images, videos = self.process_vision_info(full_messages, image_patch_size=self.image_patch_size)
            if videos not in (None, []):
                raise ValueError("video inputs are not supported in this training script")
            if images is None or len(images) != 1:
                raise ValueError("expected exactly one image per training sample")
            images_batch.append(images[0])

        batch = self.processor(
            text=full_texts,
            images=images_batch,
            do_resize=False,
            padding=True,
            return_tensors="pt",
        )
        prompt_batch = self.processor(
            text=prompt_texts,
            images=images_batch,
            do_resize=False,
            padding=True,
            return_tensors="pt",
        )

        labels = batch["input_ids"].clone()
        labels[labels == self.processor.tokenizer.pad_token_id] = -100
        for idx in range(labels.shape[0]):
            prompt_len = int(prompt_batch["attention_mask"][idx].sum().item())
            labels[idx, :prompt_len] = -100
        batch["labels"] = labels
        return batch


def count_trainable_parameters(model: Any) -> tuple[int, int]:
    total = 0
    trainable = 0
    for param in model.parameters():
        n = param.numel()
        total += n
        if param.requires_grad:
            trainable += n
    return trainable, total


def build_model_and_processor(cfg: dict[str, Any], *, log_file: str | None) -> tuple[Any, Any]:
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor

    model_cfg = cfg["model"]
    qlora_cfg = cfg["qlora"]
    lora_cfg = cfg["lora"]

    quantization_config = None
    model_kwargs: dict[str, Any] = {
        "trust_remote_code": bool(model_cfg.get("trust_remote_code", True)),
    }
    torch_dtype = resolve_torch_dtype(model_cfg.get("torch_dtype"))
    if torch_dtype is not None:
        model_kwargs["torch_dtype"] = torch_dtype

    if bool(qlora_cfg.get("enabled")):
        from transformers import BitsAndBytesConfig

        compute_dtype = resolve_torch_dtype(qlora_cfg.get("bnb_4bit_compute_dtype")) or torch.bfloat16
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=bool(qlora_cfg.get("load_in_4bit", True)),
            bnb_4bit_quant_type=str(qlora_cfg.get("bnb_4bit_quant_type", "nf4")),
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=bool(qlora_cfg.get("bnb_4bit_use_double_quant", True)),
        )
        model_kwargs["quantization_config"] = quantization_config
        model_kwargs["device_map"] = "auto"

    model_path = model_cfg.get("local_dir") or model_cfg.get("model_id")
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=model_kwargs["trust_remote_code"])
    model = AutoModelForImageTextToText.from_pretrained(model_path, **model_kwargs)

    if cfg["training"].get("gradient_checkpointing", False):
        model.gradient_checkpointing_enable()
        try:
            model.enable_input_require_grads()
        except Exception:
            pass

    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    if quantization_config is not None:
        model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=int(lora_cfg.get("rank", 8)),
        lora_alpha=int(lora_cfg.get("alpha", 16)),
        lora_dropout=float(lora_cfg.get("dropout", 0.05)),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(lora_cfg.get("target_modules", [])),
    )
    model = get_peft_model(model, peft_config)

    trainable, total = count_trainable_parameters(model)
    emit(
        f"prepared model with trainable params={trainable:,} / total params={total:,}",
        log_file=log_file,
    )
    return model, processor


def build_training_arguments(cfg: dict[str, Any]) -> Any:
    from transformers import TrainingArguments

    train_cfg = cfg["training"]
    report_to = train_cfg.get("report_to", "none")
    if isinstance(report_to, str) and report_to.lower() == "none":
        report_to = []

    bf16 = str(cfg["model"].get("torch_dtype", "")).lower() in {"bf16", "bfloat16"}
    fp16 = str(cfg["model"].get("torch_dtype", "")).lower() in {"fp16", "float16", "half"}

    return TrainingArguments(
        output_dir=str(repo_path(train_cfg["output_dir"])),
        overwrite_output_dir=False,
        num_train_epochs=float(train_cfg.get("num_train_epochs", 1)),
        per_device_train_batch_size=int(train_cfg.get("per_device_train_batch_size", 1)),
        gradient_accumulation_steps=int(train_cfg.get("gradient_accumulation_steps", 1)),
        learning_rate=float(train_cfg.get("learning_rate", 1e-4)),
        weight_decay=float(train_cfg.get("weight_decay", 0.0)),
        warmup_ratio=float(train_cfg.get("warmup_ratio", 0.03)),
        lr_scheduler_type=str(train_cfg.get("lr_scheduler_type", "cosine")),
        logging_steps=int(train_cfg.get("logging_steps", 10)),
        save_strategy=str(train_cfg.get("save_strategy", "epoch")),
        save_steps=int(train_cfg.get("save_steps", 0)),
        save_total_limit=int(train_cfg.get("save_total_limit", 2)),
        bf16=bf16,
        fp16=fp16 and not bf16,
        remove_unused_columns=False,
        report_to=report_to,
        dataloader_num_workers=0,
        gradient_checkpointing=bool(train_cfg.get("gradient_checkpointing", False)),
        max_grad_norm=1.0,
        seed=int(cfg.get("seed", 42)),
    )


def train(cfg: dict[str, Any], *, log_file: str | None) -> None:
    from transformers import Trainer

    set_seed(int(cfg.get("seed", 42)))
    model, processor = build_model_and_processor(cfg, log_file=log_file)
    samples = load_train_samples(cfg["data"]["train_file"])
    emit(f"loaded {len(samples)} training samples", log_file=log_file)

    dataset = QwenVLTrainDataset(samples)
    collator = QwenVLDataCollator(
        processor,
        max_pixels=int(cfg["training"].get("max_pixels")) if cfg["training"].get("max_pixels") is not None else None,
    )
    trainer = Trainer(
        model=model,
        args=build_training_arguments(cfg),
        train_dataset=dataset,
        data_collator=collator,
    )
    trainer.train()
    trainer.save_model(str(repo_path(cfg["training"]["output_dir"])))
    processor.save_pretrained(str(repo_path(cfg["training"]["output_dir"])))


def main() -> int:
    args = parse_args()
    try:
        cfg = load_yaml_or_json(args.config)
        train(cfg, log_file=args.log_file)
        emit("training completed", log_file=args.log_file)
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {type(exc).__name__}: {exc}")
        append_log(args.log_file, f"ERROR: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
