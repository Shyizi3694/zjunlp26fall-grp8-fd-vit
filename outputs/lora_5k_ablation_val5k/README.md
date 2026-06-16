# True 5k LoRA Ablation on OK-VQA val_5k

Date: 2026-06-16

This directory extends the true 5k LoRA ablation to the larger fixed validation split `data/processed/okvqa/val_5k.jsonl`.

## Experiments

| Exp ID | Setting | Train data | Checkpoint | Eval set |
|---|---|---|---|---|
| E04_lora_random_5k_r8_val5k | LoRA random 5k | `train_random_5k_qwen.json` | `checkpoints/lora_random_5k` | `val_5k` |
| E05_lora_failure_5k_r8_val5k | LoRA failure-driven 5k | `train_failure_5k_qwen.json` | `checkpoints/lora_failure_5k` | `val_5k` |

The summary table also includes E00-E03 val_5k results for context.

## Main Result

| Exp ID | Train size | Sampling | acc_any | acc_soft | format_error_rate |
|---|---:|---|---:|---:|---:|
| E00_zero_shot_basic_val5k | 0 | none | 0.5524 | 0.5127 | 0.0000 |
| E01_prompt_strict_val5k | 0 | none | 0.5004 | 0.4647 | 0.0002 |
| E02_lora_random_2k_r8_val5k | 2k | random | 0.6670 | 0.6205 | 0.0002 |
| E03_lora_failure_2k_r8_val5k | 2k | failure-driven | 0.6696 | 0.6201 | 0.0002 |
| E04_lora_random_5k_r8_val5k | 5k | random | 0.6818 | 0.6359 | 0.0002 |
| E05_lora_failure_5k_r8_val5k | 5k | failure-driven | 0.6818 | 0.6341 | 0.0002 |

## Interpretation

- The true 5k LoRA checkpoints improve over the 2k LoRA checkpoints on `val_5k`.
- On `val_5k`, random-5k and failure-driven-5k tie on `acc_any`; random-5k is slightly higher on `acc_soft`.
- This larger evaluation weakens any strong claim that failure-driven sampling consistently beats random sampling. The safer conclusion is that both sampling strategies benefit from scaling to 5k, with small, non-robust differences between them.

## Files

- `results_lora_2k5k_val5k.csv`
- `results_lora_2k5k_val5k.md`
- `error_comparison_lora_2k5k_val5k.csv`
- `error_comparison_lora_2k5k_val5k.md`
- `E04_lora_random_5k_r8_val5k/`
- `E05_lora_failure_5k_r8_val5k/`

