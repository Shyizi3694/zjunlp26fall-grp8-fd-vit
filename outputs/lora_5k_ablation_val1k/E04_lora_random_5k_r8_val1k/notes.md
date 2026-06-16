# E04_lora_random_5k_r8_val1k Notes

- Date: 2026-06-16
- Eval set: `data/processed/okvqa/val_1k.jsonl`
- Seed: `42`
- LoRA: yes
- Sampling: random
- Train size: 5000
- LoRA rank: 8
- Checkpoint: `checkpoints/lora_random_5k`
- Train command: `bash scripts/train_lora.sh configs/lora_random_5k_r8.yaml`
- Inference config: `configs/infer_lora_random_5k_r8.yaml`
- Metrics: `outputs/lora_5k_ablation_val1k/E04_lora_random_5k_r8_val1k/metrics.json`
- Result: `acc_any=0.6690`, `acc_soft=0.6267`, `format_error_rate=0.0000`

This experiment is part of the true 5k LoRA ablation and does not overwrite the main E00-E03 outputs.

