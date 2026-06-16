# FD-VIT Final Visualization

Date: 2026-06-16

This directory provides a unified view of the completed FD-VIT experiments.

## Included Results

- Main OK-VQA `val_1k` experiments: E00-E05
- Prompt/template ablation: E06 templates 001-006
- OK-VQA `val_5k` robustness experiments: E00-E05
- Paired bootstrap and paired randomization significance analysis
- GUI grounding bonus: B01 small demo and B02 larger demo

## Files

- `dashboard.html`: static HTML dashboard for quick inspection
- `all_vqa_results.csv`: quantitative VQA results across main, prompt ablation, and val_5k groups
- `gui_results.csv`: GUI grounding bonus metrics

The dashboard intentionally separates prompt ablation, `val_1k`, `val_5k`, significance, and GUI sections so report figures can be selected without mixing experimental roles.

