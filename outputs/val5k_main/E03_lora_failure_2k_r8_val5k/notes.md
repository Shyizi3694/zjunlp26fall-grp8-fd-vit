# E03_lora_failure_2k_r8_val5k Notes

- Experiment: E03_lora_failure_2k_r8_val5k
- Setting: LoRA-failure with 2k failure-driven OK-VQA training samples
- Eval set: data/processed/okvqa/val_5k.jsonl
- Seed: 42
- LoRA: yes, rank 8
- Checkpoint: checkpoints/lora_failure_2k
- Metrics: outputs/val5k_main/E03_lora_failure_2k_r8_val5k/metrics.json
- Repair/evaluation date: 2026-06-16
- Report note: Compared with E02 on val_5k, this run improves acc_any but is effectively tied/slightly lower on acc_soft.
