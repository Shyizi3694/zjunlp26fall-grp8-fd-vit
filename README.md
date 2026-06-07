# zjunlp26fall-grp8-fd-vit

FD-VIT: Failure-Driven Visual Instruction Tuning for multimodal visual reasoning in the ZJU NLP 2026 fall course project.

本仓库主线固定为：

```text
Qwen3-VL-4B-Instruct
-> OK-VQA / VQA subset
-> zero-shot baseline
-> prompt-only baseline
-> LoRA-random instruction tuning
-> LoRA-failure-driven instruction tuning
-> error analysis
```

不要在未更新 `docs/EXPERIMENT_PROTOCOL.md` 和 `docs/REQUIREMENTS_TRACEABILITY.md` 的情况下扩展主实验矩阵。Janus-Pro、image generation、完整 GUI Agent 都不是当前主线。

## Docs

开始编码或跑实验前先读：

- `docs/README.md`: 文档总入口和阅读顺序。
- `docs/FD_VIT_CODING_AGENT_GUIDE.md`: 项目阶段、范围边界、全局工程规则。
- `docs/CODING_AGENT_TASK_CARDS.md`: 每个 coding task 的输入、输出、自测命令和完成标准。
- `docs/DATA_AND_FORMAT_CONTRACT.md`: raw / processed / prediction / metrics 等格式契约。
- `docs/EXPERIMENT_PROTOCOL.md`: E00-E03 实验矩阵、指标、随机种子和防泄漏规则。
- `docs/REQUIREMENTS_TRACEABILITY.md`: 课程要求到 FD-VIT 范围的映射。

如果使用 coding agent，优先使用 `.agents/skills/fd-vit-task-runner/SKILL.md`；如果 agent 不支持 skill，就按 `AGENTS.md` 中的 Required Reading Flow 手动执行。

## Repository Layout

```text
configs/       shared configs
data/raw/      raw OK-VQA annotations and COCO images, ignored by git
data/processed processed JSONL / Qwen-format data
data/samples   tiny smoke-test samples
models/        local base model snapshots, ignored by git
outputs/       experiment outputs
logs/          preparation and validation summaries, ignored by git
scripts/       preparation, validation, inference, evaluation scripts
src/fdvit/     reusable project package code
docs/          project contracts and execution docs
```

## Environment Preparation

Python dependencies are pinned in `requirements.txt`. The helper script creates project directories, creates either a `venv` or conda environment, installs dependencies, and can run the CUDA/PyTorch environment check.

Default backend is `venv`:

```bash
python3 scripts/prepare_environment.py \
  --create_env \
  --install \
  --run_check_env \
  --output logs/environment_prepare.json \
  --overwrite

source .venv/bin/activate
```

Conda backend is available when local conda or miniconda is installed:

```bash
python3 scripts/prepare_environment.py \
  --env_backend conda \
  --conda_executable "$HOME/miniconda3/bin/conda" \
  --conda_env fd-vit \
  --python_version 3.12 \
  --create_env \
  --install \
  --run_check_env \
  --output logs/environment_prepare.json \
  --overwrite

conda activate fd-vit
```

To only inspect the current environment:

```bash
python scripts/check_env.py --output logs/env_check.json --overwrite
```

The environment check writes Python, OS, CUDA availability, GPU name/memory, PyTorch, Transformers, PEFT and bitsandbytes status to `logs/env_check.json`.

## Raw Data Preparation

The baseline requires both OK-VQA annotations and COCO train2014/val2014 images:

```text
data/raw/okvqa/
  OpenEnded_mscoco_train2014_questions.json
  mscoco_train2014_annotations.json
  OpenEnded_mscoco_val2014_questions.json
  mscoco_val2014_annotations.json

data/raw/coco/
  train2014/*.jpg
  val2014/*.jpg
```

Download OK-VQA annotations only:

```bash
python scripts/prepare_raw_data.py \
  --download_annotations \
  --output logs/raw_data_prepare.json \
  --overwrite
```

Download annotations plus COCO train2014/val2014 image archives:

```bash
python scripts/prepare_raw_data.py \
  --download_annotations \
  --download_coco \
  --output logs/raw_data_prepare.json \
  --overwrite
```

COCO image archives are large. If downloading them manually, place extracted directories under `data/raw/coco/train2014` and `data/raw/coco/val2014`, then validate without download flags:

```bash
python scripts/prepare_raw_data.py \
  --output logs/raw_data_prepare.json \
  --overwrite
```

`logs/raw_data_prepare.json` reports OK-VQA record counts, COCO image counts, missing files, and `ready_for_prepare_okvqa`. It must be `true` before running processed-data conversion.

## Model Preparation

Default model:

```text
Qwen/Qwen3-VL-4B-Instruct -> models/Qwen3-VL-4B-Instruct
```

Download or validate the default 4B model:

```bash
python scripts/prepare_model.py \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

If Hugging Face Xet is slow or unstable, disable Xet for the command:

```bash
HF_HUB_DISABLE_XET=1 python scripts/prepare_model.py \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

For low-VRAM machines, resolve the documented fallback model instead:

```bash
python scripts/prepare_model.py \
  --use_fallback \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

To validate an already downloaded model without network access:

```bash
python scripts/prepare_model.py \
  --local_files_only \
  --output logs/model_prepare.json \
  --overwrite
```

`logs/model_prepare.json` should show `status: passed` and `ready_for_baseline: true`.

## Baseline Readiness

Before running E00/E01 baseline work, check:

- `logs/env_check.json` exists and CUDA/PyTorch status is understood for the target machine.
- `logs/raw_data_prepare.json` has `ready_for_prepare_okvqa: true`.
- `logs/model_prepare.json` has `ready_for_baseline: true`.
- Raw data and model weights stay out of git; only scripts, configs, docs, metrics and small summaries should be committed.

Next implementation step after these checks is Task 1 in `docs/CODING_AGENT_TASK_CARDS.md`: convert raw OK-VQA + COCO paths into the project JSONL format with `scripts/prepare_okvqa.py`.
