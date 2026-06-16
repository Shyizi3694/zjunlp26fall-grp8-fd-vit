# Val5k Main Evaluation

Repair/evaluation date: 2026-06-16

This directory contains the non-overlapping `val_5k` evaluation for the clean E00-E03 mainline. It intentionally does not overwrite the `val_1k` outputs under `outputs/E00_*` through `outputs/E03_*`.

## Experiments

| Exp | Setting | Eval set | Checkpoint |
|---|---|---|---|
| E00_zero_shot_basic_val5k | zero-shot basic prompt | `data/processed/okvqa/val_5k.jsonl` | none |
| E01_prompt_strict_val5k | prompt-only strict short answer | `data/processed/okvqa/val_5k.jsonl` | none |
| E02_lora_random_2k_r8_val5k | LoRA-random-2k | `data/processed/okvqa/val_5k.jsonl` | `checkpoints/lora_random_2k` |
| E03_lora_failure_2k_r8_val5k | LoRA-failure-2k | `data/processed/okvqa/val_5k.jsonl` | `checkpoints/lora_failure_2k` |

## Main Result

| Exp | acc_any | acc_soft | format_error_rate | num_samples |
|---|---:|---:|---:|---:|
| E00_zero_shot_basic_val5k | 0.5524 | 0.5127 | 0.0000 | 5000 |
| E01_prompt_strict_val5k | 0.5004 | 0.4647 | 0.0002 | 5000 |
| E02_lora_random_2k_r8_val5k | 0.6670 | 0.6205 | 0.0002 | 5000 |
| E03_lora_failure_2k_r8_val5k | 0.6696 | 0.6201 | 0.0002 | 5000 |

Compared with random LoRA, failure-driven LoRA is slightly higher on `acc_any` (+0.0026) but slightly lower on `acc_soft` (-0.0003). This should be reported as a near-tie rather than a strong overall accuracy win.

## Report-ready Artifacts

- `results_val5k.csv` / `results_val5k.md`: main `val_5k` result table.
- `error_comparison_val5k.csv` / `error_comparison_val5k.md`: error type comparison.
- `case_studies_val5k.md`: automatically selected qualitative cases.
- `dashboard_val5k/`: dashboard artifacts generated only from the four `val_5k` experiments.

## Notes

- The E03 run was executed outside the restricted sandbox because CUDA was not visible inside the sandbox. The approved environment path was `/home/hhhjyz/miniconda3/envs/fd-vit`.
- These results are separate from the quarantined optional 5k artifacts under `outputs/invalid_optional_5k/`.
