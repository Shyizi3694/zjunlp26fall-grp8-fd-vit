# Invalid Optional 5k Configs

These configs are quarantined and should not be used for official experiments.

They were originally named as optional 5k configs, but their contents still referenced 2k experiment ids, 2k training files, and 2k checkpoint directories. They are preserved only for traceability.

Use the clean E00-E03 mainline configs instead:

- `configs/infer_zero_shot.yaml`
- `configs/infer_prompt_only.yaml`
- `configs/lora_random_2k.yaml`
- `configs/lora_failure_2k.yaml`
- `configs/infer_lora_random_2k.yaml`
- `configs/infer_lora_failure_2k.yaml`

Repair date: 2026-06-16.
