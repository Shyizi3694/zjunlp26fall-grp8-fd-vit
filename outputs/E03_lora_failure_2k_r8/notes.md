# E03_lora_failure_2k_r8 Notes

- Experiment: E03_lora_failure_2k_r8
- Setting: LoRA-failure with 2k failure-driven OK-VQA training samples
- Eval set: data/processed/okvqa/val_1k.jsonl
- Seed: 42
- LoRA: yes, rank 8
- Checkpoint: checkpoints/lora_failure_2k
- Metrics: outputs/E03_lora_failure_2k_r8/metrics.json
- Repair date: 2026-06-16
- Repair note: inference and evaluation were rerun against the current checkpoint. The LoRA checkpoint was not retrained.
