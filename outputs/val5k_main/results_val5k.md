| Exp | Setting | Train n | Sampling | LoRA r | acc_any | acc_soft | format_error_rate | Δacc_soft vs E00 | Δacc_soft vs E02 |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| E00_zero_shot_basic_val5k | Zero-shot | 0 | - | - | 0.5524 | 0.5127 | 0.0000 | 0.0000 | -0.1078 |
| E01_prompt_strict_val5k | Prompt-only | 0 | - | - | 0.5004 | 0.4647 | 0.0002 | -0.0479 | -0.1557 |
| E02_lora_random_2k_r8_val5k | LoRA-random | 2000 | random | 8 | 0.6670 | 0.6205 | 0.0002 | 0.1078 | 0.0000 |
| E03_lora_failure_2k_r8_val5k | LoRA-failure | 2000 | failure | 8 | 0.6696 | 0.6201 | 0.0002 | 0.1075 | -0.0003 |
