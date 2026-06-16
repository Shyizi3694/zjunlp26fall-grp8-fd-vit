# E05_lora_failure_5k_r8_val5k Notes

- Date: 2026-06-16
- Eval set: `data/processed/okvqa/val_5k.jsonl`
- Seed: `42`
- LoRA: yes
- Sampling: failure-driven
- Train size: 5000
- LoRA rank: 8
- Checkpoint: `checkpoints/lora_failure_5k`
- Inference config: `configs/infer_lora_failure_5k_r8_val5k.yaml`
- Metrics: `outputs/lora_5k_ablation_val5k/E05_lora_failure_5k_r8_val5k/metrics.json`
- Result: `acc_any=0.6818`, `acc_soft=0.6341`, `format_error_rate=0.0002`

