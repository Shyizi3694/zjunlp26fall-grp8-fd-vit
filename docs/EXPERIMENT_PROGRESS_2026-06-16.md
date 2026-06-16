# Experiment Progress 2026-06-16

This file records additional experiments and analysis added after the clean E00-E03 `val_1k` mainline repair. It is intended as report-writing evidence and should not replace the protocol documents.

## Step 1: val_5k Evaluation for E00-E03

Status: completed.

Output root:

```text
outputs/val5k_main/
```

Summary:

| Exp | acc_any | acc_soft | format_error_rate | num_samples |
|---|---:|---:|---:|---:|
| E00_zero_shot_basic_val5k | 0.5524 | 0.5127 | 0.0000 | 5000 |
| E01_prompt_strict_val5k | 0.5004 | 0.4647 | 0.0002 | 5000 |
| E02_lora_random_2k_r8_val5k | 0.6670 | 0.6205 | 0.0002 | 5000 |
| E03_lora_failure_2k_r8_val5k | 0.6696 | 0.6201 | 0.0002 | 5000 |

Interpretation for report:

- E02 and E03 are essentially tied on `acc_soft` at the larger validation scale.
- E03 is slightly higher on `acc_any`, but slightly lower on `acc_soft`; do not describe this as a strong overall win.
- Error type comparison shows E03 improves `spatial`, `attribute`, and `commonsense` counts compared with E02, while `other` and `ambiguous` increase slightly.
- The result supports a nuanced claim: failure-driven sampling changes the error distribution and may help targeted categories, but broad accuracy improvement is not decisive on `val_5k`.

Report-ready files:

- `outputs/val5k_main/results_val5k.csv`
- `outputs/val5k_main/results_val5k.md`
- `outputs/val5k_main/error_comparison_val5k.csv`
- `outputs/val5k_main/error_comparison_val5k.md`
- `outputs/val5k_main/case_studies_val5k.md`
- `outputs/val5k_main/dashboard_val5k/dashboard.html`

Implementation note:

- E03 `val_5k` inference required running outside the restricted sandbox because CUDA was not visible inside the sandbox.

## Remaining Steps

## Step 2: Manual Error Review and Balanced Case Study Reselection

Status: completed.

Output root:

```text
outputs/manual_review/
```

Files:

- `outputs/manual_review/manual_error_review_val5k.csv`
- `outputs/manual_review/balanced_case_studies_val5k.md`
- `outputs/manual_review/README.md`

Review summary:

| Category | Count | Purpose |
|---|---:|---|
| fd_fixes_random | 6 | positive examples for failure-driven sampling |
| random_beats_fd | 4 | counterexamples where random LoRA is better |
| both_lora_wrong | 4 | limitation examples |
| both_lora_fix_zero | 4 | examples where LoRA helps regardless of sampling |
| regression_from_zero | 2 | examples where fine-tuning hurts a zero-shot answer |

Interpretation for report:

- Use the balanced case study table for qualitative analysis instead of only showing failure-driven wins.
- The manual review supports a cautious story: failure-driven sampling can fix targeted commonsense/attribute/counting cases, but it also introduces regressions and is not uniformly better than random sampling.
- The review is based on question text, accepted answers, predictions, and automatic correctness; it is not a full dataset relabeling pass.

## Remaining Steps

## Step 3: Lightweight Prompt/Template Inference Ablation

Status: completed.

Output root:

```text
outputs/prompt_ablation_val1k/
```

Setup:

- Base model only, no LoRA.
- Eval set: `data/processed/okvqa/val_1k.jsonl`.
- Templates: `okvqa_short_001` through `okvqa_short_006`.
- Outputs use experiment IDs `E06_prompt_template_XXX_val1k` to avoid overwriting E00/E01.

Summary:

| Template | acc_any | acc_soft | format_error_rate |
|---|---:|---:|---:|
| okvqa_short_001 | 0.5350 | 0.4973 | 0.0000 |
| okvqa_short_002 | 0.4980 | 0.4620 | 0.0000 |
| okvqa_short_003 | 0.4740 | 0.4420 | 0.0000 |
| okvqa_short_004 | 0.5210 | 0.4840 | 0.0000 |
| okvqa_short_005 | 0.4140 | 0.3857 | 0.0000 |
| okvqa_short_006 | 0.4980 | 0.4650 | 0.0000 |

Interpretation for report:

- Template `okvqa_short_001` is strongest on this validation subset.
- Stronger wording about compact answers does not automatically improve VQA accuracy.
- Prompt-only strict mode (`okvqa_short_002`) controls format but reduces accuracy relative to the simpler template.

Report-ready files:

- `outputs/prompt_ablation_val1k/prompt_ablation_table.csv`
- `outputs/prompt_ablation_val1k/prompt_ablation_table.md`
- `outputs/prompt_ablation_val1k/README.md`

## Remaining Steps

1. True 5k LoRA training ablation if compute budget allows.
2. GUI grounding bonus only after the main analysis is stable.

## Step 4: True 5k LoRA Training Ablation

Status: completed.

Output root:

```text
outputs/lora_5k_ablation_val1k/
```

Checkpoints:

- `checkpoints/lora_random_5k`
- `checkpoints/lora_failure_5k`

Evaluation setup:

- Eval set: `data/processed/okvqa/val_1k.jsonl`
- Seed: `42`
- Prompt template: `okvqa_short_002`
- LoRA rank: `8`
- Output directories:
  - `outputs/lora_5k_ablation_val1k/E04_lora_random_5k_r8_val1k/`
  - `outputs/lora_5k_ablation_val1k/E05_lora_failure_5k_r8_val1k/`

Summary:

| Exp ID | Train size | Sampling | acc_any | acc_soft | format_error_rate |
|---|---:|---|---:|---:|---:|
| E02_lora_random_2k_r8 | 2k | random | 0.6620 | 0.6167 | 0.0000 |
| E03_lora_failure_2k_r8 | 2k | failure-driven | 0.6620 | 0.6177 | 0.0000 |
| E04_lora_random_5k_r8_val1k | 5k | random | 0.6690 | 0.6267 | 0.0000 |
| E05_lora_failure_5k_r8_val1k | 5k | failure-driven | 0.6790 | 0.6313 | 0.0000 |

Interpretation for report:

- Moving from 2k to 5k improves both LoRA variants on `val_1k`.
- Failure-driven sampling is only marginally ahead of random at 2k, but the gap becomes larger at 5k.
- The strongest result in this ablation is `E05_lora_failure_5k_r8_val1k`.
- The margin remains modest, so the report should describe this as supportive evidence rather than an overwhelming win.

Report-ready files:

- `outputs/lora_5k_ablation_val1k/results_lora_2k5k_val1k.csv`
- `outputs/lora_5k_ablation_val1k/results_lora_2k5k_val1k.md`
- `outputs/lora_5k_ablation_val1k/error_comparison_lora_2k5k_val1k.csv`
- `outputs/lora_5k_ablation_val1k/error_comparison_lora_2k5k_val1k.md`
- `outputs/lora_5k_ablation_val1k/case_studies_lora_2k5k_val1k.md`
- `outputs/lora_5k_ablation_val1k/dashboard_lora_2k5k_val1k/`

## Remaining Steps

1. GUI grounding bonus only after confirming local GUI data availability.

## Step 5: GUI Grounding Bonus

Status: completed as a small optional demo.

Output root:

```text
outputs/B01_gui_grounding_demo/
```

Data:

- Source dataset: `likaixin/ScreenSpot-Pro`
- Task: `vscode_macos`
- Processed file: `data/processed/gui/val_small.jsonl`
- Number of examples: 20
- Sample file: `data/samples/gui_grounding_5.jsonl`

Setup:

- Config: `configs/gui_grounding.yaml`
- Model: `Qwen/Qwen3-VL-4B-Instruct`
- Checkpoint: none
- Coordinate mode: `qwen_1000`
- Seed: `42`

Result:

| Metric | Value |
|---|---:|
| num_samples | 20 |
| parse_success_rate | 1.0000 |
| point_in_bbox_acc | 0.4500 |
| center_distance_norm | 0.0991 |
| inference_error_rate | 0.0000 |

Control-type breakdown:

| Control type | Samples | point_in_bbox_acc |
|---|---:|---:|
| text | 15 | 0.6000 |
| icon | 5 | 0.0000 |

Interpretation for report:

- The GUI code path is runnable end to end: data preparation, inference, parsing, and evaluation all complete.
- This is only a 20-sample bonus demo, not a robust GUI benchmark.
- The result suggests Qwen3-VL can sometimes localize text controls, while icon localization is weak in this small sample.
- The model outputs are best interpreted as Qwen-style 0-1000 coordinates rather than original pixel coordinates.

Report-ready files:

- `outputs/B01_gui_grounding_demo/predictions.jsonl`
- `outputs/B01_gui_grounding_demo/metrics.json`
- `outputs/B01_gui_grounding_demo/errors.jsonl`
- `outputs/B01_gui_grounding_demo/README.md`

## Step 6: Additional Robustness Experiments and Final Visualization

Status: completed.

Added experiments:

1. E04/E05 true 5k LoRA evaluation on `val_5k`
2. Paired bootstrap and paired randomization significance analysis
3. Larger GUI grounding bonus evaluation
4. Unified final visualization dashboard

### E04/E05 on val_5k

Output root:

```text
outputs/lora_5k_ablation_val5k/
```

| Exp ID | Train size | Sampling | acc_any | acc_soft | format_error_rate |
|---|---:|---|---:|---:|---:|
| E04_lora_random_5k_r8_val5k | 5k | random | 0.6818 | 0.6359 | 0.0002 |
| E05_lora_failure_5k_r8_val5k | 5k | failure-driven | 0.6818 | 0.6341 | 0.0002 |

Interpretation:

- Both true 5k LoRA variants improve over the 2k LoRA variants on the larger validation split.
- On `val_5k`, random-5k and failure-driven-5k tie on `acc_any`; random-5k is slightly higher on `acc_soft`.

### Paired Significance

Output root:

```text
outputs/significance/
```

Summary:

- E02 vs E03 on `val_1k`: no significant difference.
- E04 vs E05 on `val_1k`: no significant difference.
- E02 vs E03 on `val_5k`: no significant difference.
- E04 vs E05 on `val_5k`: no significant difference.

All bootstrap confidence intervals cross zero, so the report should describe random-vs-failure differences as small and not statistically robust.

### Larger GUI Bonus

Output root:

```text
outputs/B02_gui_grounding_larger/
```

Data:

- Requested limit: 100
- Available processed examples: 55
- Source task: ScreenSpot-Pro `vscode_macos`

Result:

| Metric | Value |
|---|---:|
| num_samples | 55 |
| parse_success_rate | 1.0000 |
| point_in_bbox_acc | 0.4364 |
| center_distance_norm | 0.1239 |

### Final Visualization

Output root:

```text
outputs/final_visualization/
```

Files:

- `outputs/final_visualization/dashboard.html`
- `outputs/final_visualization/all_vqa_results.csv`
- `outputs/final_visualization/gui_results.csv`
