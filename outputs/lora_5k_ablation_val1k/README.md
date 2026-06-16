# True 5k LoRA Ablation on OK-VQA val_1k

Date: 2026-06-16

This directory contains the non-overwriting 5k LoRA ablation for the FD-VIT project. It uses newly trained 5k checkpoints and evaluates them on the fixed `data/processed/okvqa/val_1k.jsonl` split.

## Experiments

| Exp ID | Setting | Train data | Checkpoint | Eval set |
|---|---|---|---|---|
| E04_lora_random_5k_r8_val1k | LoRA random 5k | `train_random_5k_qwen.json` | `checkpoints/lora_random_5k` | `val_1k` |
| E05_lora_failure_5k_r8_val1k | LoRA failure-driven 5k | `train_failure_5k_qwen.json` | `checkpoints/lora_failure_5k` | `val_1k` |

The original 2k LoRA results are included in the summary tables for comparison, but their files remain in the main output directories.

## Main Result

| Exp ID | Train size | Sampling | acc_any | acc_soft | format_error_rate |
|---|---:|---|---:|---:|---:|
| E02_lora_random_2k_r8 | 2k | random | 0.6620 | 0.6167 | 0.0000 |
| E03_lora_failure_2k_r8 | 2k | failure-driven | 0.6620 | 0.6177 | 0.0000 |
| E04_lora_random_5k_r8_val1k | 5k | random | 0.6690 | 0.6267 | 0.0000 |
| E05_lora_failure_5k_r8_val1k | 5k | failure-driven | 0.6790 | 0.6313 | 0.0000 |

## Interpretation

- Increasing the LoRA training set from 2k to 5k improves both random and failure-driven variants on `val_1k`.
- The failure-driven advantage is small at 2k (`+0.0010 acc_soft` over random) and larger at 5k (`+0.0047 acc_soft`, `+0.0100 acc_any` over random).
- The 5k result supports a cautious claim that failure-driven sampling becomes more useful when more mined examples are available, but the margin is still modest.

## Files

- `results_lora_2k5k_val1k.csv`
- `results_lora_2k5k_val1k.md`
- `error_comparison_lora_2k5k_val1k.csv`
- `error_comparison_lora_2k5k_val1k.md`
- `case_studies_lora_2k5k_val1k.md`
- `dashboard_lora_2k5k_val1k/`

