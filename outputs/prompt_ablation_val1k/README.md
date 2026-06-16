# Prompt Template Ablation on val_1k

Evaluation date: 2026-06-16

This directory contains a lightweight inference-only prompt/template ablation. It uses the base Qwen3-VL model without LoRA and evaluates all six OK-VQA short-answer templates on `data/processed/okvqa/val_1k.jsonl`.

## Main Finding

| Template | acc_any | acc_soft | format_error_rate |
|---|---:|---:|---:|
| okvqa_short_001 | 0.5350 | 0.4973 | 0.0000 |
| okvqa_short_002 | 0.4980 | 0.4620 | 0.0000 |
| okvqa_short_003 | 0.4740 | 0.4420 | 0.0000 |
| okvqa_short_004 | 0.5210 | 0.4840 | 0.0000 |
| okvqa_short_005 | 0.4140 | 0.3857 | 0.0000 |
| okvqa_short_006 | 0.4980 | 0.4650 | 0.0000 |

Template `okvqa_short_001` is the best prompt among the tested templates. The stricter or more verbose prompts reduce accuracy in this setup, even though all keep the format error rate at zero.

## Report-ready Files

- `prompt_ablation_table.csv`
- `prompt_ablation_table.md`
- `prompt_ablation_results.csv`
- `prompt_ablation_results.md`

Use `prompt_ablation_table.*` for report writing because it contains prompt-specific deltas. `prompt_ablation_results.*` is the generic summarizer output and is kept for traceability.
