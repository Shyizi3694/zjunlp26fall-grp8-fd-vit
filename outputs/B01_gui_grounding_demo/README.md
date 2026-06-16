# B01 GUI Grounding Demo

Date: 2026-06-16

This is an optional bonus demo using Qwen3-VL on a small ScreenSpot-Pro GUI grounding subset.

## Data

- Source dataset: `likaixin/ScreenSpot-Pro`
- Task: `vscode_macos`
- Processed split: `data/processed/gui/val_small.jsonl`
- Number of examples: 20
- Sample file: `data/samples/gui_grounding_5.jsonl`

## Setup

- Config: `configs/gui_grounding.yaml`
- Model: `Qwen/Qwen3-VL-4B-Instruct`
- Checkpoint: none
- Coordinate mode: `qwen_1000`
- Seed: `42`

The first run with `coordinate_mode=auto` parsed outputs as raw pixels and gave zero hits. The model outputs are better interpreted as Qwen-style 0-1000 coordinates, so the final config and metrics use `qwen_1000`.

## Result

| Metric | Value |
|---|---:|
| num_samples | 20 |
| parse_success_rate | 1.0000 |
| point_in_bbox_acc | 0.4500 |
| center_distance_norm | 0.0991 |
| inference_error_rate | 0.0000 |

By control type:

| Control type | Samples | point_in_bbox_acc |
|---|---:|---:|
| text | 15 | 0.6000 |
| icon | 5 | 0.0000 |

This result should be reported only as a small optional demonstration, not as a central FD-VIT claim.

