| Exp | Setting | Train n | Sampling | LoRA r | acc_any | acc_soft | format_error_rate | Δacc_soft vs E00 | Δacc_soft vs E02 |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| E02_lora_random_2k_r8 | LoRA-random | 2000 | random | 8 | 0.6620 | 0.6167 | 0.0000 | 0.6167 | 0.0000 |
| E03_lora_failure_2k_r8 | LoRA-failure | 2000 | failure | 8 | 0.6620 | 0.6177 | 0.0000 | 0.6177 | 0.0010 |
| E04_lora_random_5k_r8_val1k | LoRA-random | 5000 | random | 8 | 0.6690 | 0.6267 | 0.0000 | 0.6267 | 0.0100 |
| E05_lora_failure_5k_r8_val1k | LoRA-failure | 5000 | failure | 8 | 0.6790 | 0.6313 | 0.0000 | 0.6313 | 0.0147 |
