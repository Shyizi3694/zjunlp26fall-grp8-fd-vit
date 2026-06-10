| Exp | Setting | Train n | Sampling | LoRA r | acc_any | acc_soft | format_error_rate | Δacc_soft vs E00 | Δacc_soft vs E02 |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| E00_zero_shot_basic | Zero-shot | 0 | - | - | 0.5350 | 0.4973 | 0.0000 | 0.0000 | -0.1177 |
| E01_prompt_strict | Prompt-only | 0 | - | - | 0.4980 | 0.4620 | 0.0000 | -0.0353 | -0.1530 |
| E02_lora_random_2k_r8 | LoRA-random | 2000 | random | 8 | 0.6600 | 0.6150 | 0.0000 | 0.1177 | 0.0000 |
| E03_lora_failure_2k_r8 | LoRA-failure | 2000 | failure | 8 | 0.6720 | 0.6233 | 0.0000 | 0.1260 | 0.0083 |
