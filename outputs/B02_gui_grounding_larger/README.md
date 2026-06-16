# B02 GUI Grounding Larger Demo

Date: 2026-06-16

This is a larger optional GUI grounding bonus evaluation using Qwen3-VL on ScreenSpot-Pro `vscode_macos` samples.

## Data

- Source dataset: `likaixin/ScreenSpot-Pro`
- Task: `vscode_macos`
- Requested limit: 100
- Available processed examples: 55
- Processed file: `data/processed/gui/val_100.jsonl`
- Sample file: `data/samples/gui_grounding_10.jsonl`

## Setup

- Config: `configs/gui_grounding_larger.yaml`
- Model: `Qwen/Qwen3-VL-4B-Instruct`
- Checkpoint: none
- Coordinate mode: `qwen_1000`
- Seed: `42`

## Result

| Metric | Value |
|---|---:|
| num_samples | 55 |
| parse_success_rate | 1.0000 |
| point_in_bbox_acc | 0.4364 |
| center_distance_norm | 0.1239 |
| inference_error_rate | 0.0000 |

By control type:

| Control type | Samples | point_in_bbox_acc |
|---|---:|---:|
| text | 33 | 0.5758 |
| icon | 22 | 0.2273 |

This remains a bonus demo rather than a full GUI benchmark.

