# Manual Error Review and Balanced Case Studies

Review date: 2026-06-16

This directory contains a small manually reviewed validation set for report writing. It is based on `outputs/val5k_main/` and does not overwrite the automatically generated case studies.

## Files

- `manual_error_review_val5k.csv`: 20 reviewed examples across five comparison categories.
- `balanced_case_studies_val5k.md`: 10 report-ready qualitative cases selected from the reviewed examples.

## Review Categories

| Category | Count | Meaning |
|---|---:|---|
| fd_fixes_random | 6 | failure-driven LoRA correct, random LoRA wrong |
| random_beats_fd | 4 | random LoRA correct, failure-driven LoRA wrong |
| both_lora_wrong | 4 | both LoRA systems wrong |
| both_lora_fix_zero | 4 | both LoRA systems correct while zero-shot is wrong |
| regression_from_zero | 2 | zero-shot correct, both LoRA systems wrong |

## Report Guidance

- Use `balanced_case_studies_val5k.md` instead of the automatically selected cases when presenting qualitative analysis.
- The reviewed cases intentionally include negative and regression examples, so they are better for a balanced report.
- The review is text-based: it checks question, accepted answers, model predictions, and automatic correctness. It does not claim exhaustive visual relabeling of the dataset.
