# FD-VIT Critical Invariants

## Scope

- Mainline: Qwen3-VL + OK-VQA/VQA + zero-shot baseline + prompt-only baseline + LoRA-random + LoRA-failure-driven + error analysis.
- Course requirements are broad; FD-VIT execution scope is the narrowed mainline documented in `docs/REQUIREMENTS_TRACEABILITY.md`.
- Do not make Janus-Pro, image generation, full GUI Agent, multi-model comparisons, or large rank sweeps the mainline.
- Keep optional work clearly marked as optional and after E00-E03.
- Any new model, task, experiment, metric, or bonus direction must update `docs/EXPERIMENT_PROTOCOL.md`; if it changes course-coverage claims, also update `docs/REQUIREMENTS_TRACEABILITY.md`.

## Data

- Raw data belongs in `data/raw/`; processed model-ready data belongs in `data/processed/`; smoke samples belong in `data/samples/`.
- No script may depend on a local absolute path.
- Required VQA fields: `sample_id`, `dataset`, `split`, `question_id`, `image_id`, `image_path`, `question`, `answers`, `answer`.
- Qwen training samples must include `image`, `<image>` in the human prompt, short-answer instruction, and short `gpt` answer.
- Do not mix val/test samples into training data.

## Experiments

- Required matrix: E00 zero-shot, E01 prompt-only, E02 LoRA-random, E03 LoRA-failure.
- Default seed is 42.
- Main eval set must be shared across comparable experiments.
- Default generation config: `temperature=0.0`, `max_new_tokens=16`, unless recorded.
- Reports must cite files, not chat estimates.

## Evaluation

- Do not use raw string matching as the only VQA metric.
- Implement normalization: lowercase, trim, punctuation cleanup, article removal, common number-word conversion, whitespace compression.
- Required metrics: `acc_any`, `acc_soft`, `format_error_rate`.
- Always save per-sample `predictions.jsonl`, not only aggregate metrics.

## Safety and Reproducibility

- Never invent experiment results.
- Never overwrite existing outputs silently.
- Never hardcode tokens, account names, private paths, or cache directories.
- If generated outputs are too large for git, keep summaries and metrics in git and ignore raw large artifacts.
