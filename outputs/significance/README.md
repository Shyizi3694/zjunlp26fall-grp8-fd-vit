# Paired Significance Analysis

Date: 2026-06-16

This directory contains paired bootstrap confidence intervals and paired randomization p-values for the main random-vs-failure comparisons.

## Compared Pairs

- `E02_vs_E03_val1k`: random-2k vs failure-driven-2k on `val_1k`
- `E04_vs_E05_val1k`: random-5k vs failure-driven-5k on `val_1k`
- `E02_vs_E03_val5k`: random-2k vs failure-driven-2k on `val_5k`
- `E04_vs_E05_val5k`: random-5k vs failure-driven-5k on `val_5k`

## Interpretation

All 95% bootstrap confidence intervals for treatment-minus-baseline differences cross zero, and the paired randomization p-values are not significant. The report should avoid claiming a statistically significant failure-driven win. A cautious framing is that scaling LoRA data from 2k to 5k is consistently useful, while random vs failure-driven sampling differences are small and unstable across evaluation splits.

Files:

- `paired_significance.csv`
- `paired_significance.md`

