# zjunlp26fall-grp8-fd-vit

FD-VIT 是浙江大学 2026 秋季 NLP 课程大作业项目，主题是面向多模态视觉推理的失败驱动视觉指令微调。

本仓库主线固定为：

```text
Qwen3-VL-4B-Instruct
-> OK-VQA / VQA 子集
-> zero-shot 基线
-> prompt-only 基线
-> LoRA-random 指令微调
-> LoRA-failure-driven 指令微调
-> 错误分析
```

不要在未更新 `docs/EXPERIMENT_PROTOCOL.md` 和 `docs/REQUIREMENTS_TRACEABILITY.md` 的情况下扩展主实验矩阵。Janus-Pro、图像生成、完整 GUI Agent 都不是当前主线。

## 项目文档

开始编码或跑实验前先读：

- `docs/README.md`: 文档总入口和阅读顺序。
- `docs/FD_VIT_CODING_AGENT_GUIDE.md`: 项目阶段、范围边界、全局工程规则。
- `docs/CODING_AGENT_TASK_CARDS.md`: 每个编码任务的输入、输出、自测命令和完成标准。
- `docs/DATA_AND_FORMAT_CONTRACT.md`: 原始数据、处理后数据、预测、指标等格式契约。
- `docs/EXPERIMENT_PROTOCOL.md`: E00-E03 实验矩阵、指标、随机种子和防泄漏规则。
- `docs/REQUIREMENTS_TRACEABILITY.md`: 课程要求到 FD-VIT 范围的映射。

如果使用 coding agent，优先使用 `.agents/skills/fd-vit-task-runner/SKILL.md`；如果 agent 不支持 skill，就按 `AGENTS.md` 中的 Required Reading Flow 手动执行。

## 目录结构

```text
configs/       共享配置
data/raw/      OK-VQA 原始标注与 COCO 图片，不纳入 git
data/processed 转换后的 JSONL / Qwen 格式数据
data/samples   小样本冒烟测试数据
models/        本地基础模型快照，不纳入 git
outputs/       实验输出
logs/          准备与校验摘要，不纳入 git
scripts/       准备、校验、推理、评测脚本
src/fdvit/     可复用项目代码
docs/          项目契约与执行文档
```

## 环境准备

Python 依赖写在 `requirements.txt` 中。准备脚本会创建项目目录，按需创建 `venv` 或 conda 环境，安装依赖，并可运行 CUDA/PyTorch 环境检查。

默认环境后端是 `venv`：

```bash
python3 scripts/prepare_environment.py \
  --create_env \
  --install \
  --run_check_env \
  --output logs/environment_prepare.json \
  --overwrite

source .venv/bin/activate
```

如果本机已经安装 conda 或 miniconda，也可以使用 conda 后端：

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

如果只想检查当前环境：

```bash
python scripts/check_env.py --output logs/env_check.json --overwrite
```

环境检查会把 Python、OS、CUDA 可用性、GPU 名称/显存、PyTorch、Transformers、PEFT、bitsandbytes 状态写入 `logs/env_check.json`。

## 原始数据准备

基线运行需要 OK-VQA 标注和 COCO train2014/val2014 图片：

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

只下载 OK-VQA 标注：

```bash
python scripts/prepare_raw_data.py \
  --download_annotations \
  --output logs/raw_data_prepare.json \
  --overwrite
```

同时下载 OK-VQA 标注和 COCO train2014/val2014 图片压缩包：

```bash
python scripts/prepare_raw_data.py \
  --download_annotations \
  --download_coco \
  --output logs/raw_data_prepare.json \
  --overwrite
```

COCO 图片压缩包较大。如果手动下载，解压后把目录放到 `data/raw/coco/train2014` 和 `data/raw/coco/val2014`，然后不带下载参数运行校验：

```bash
python scripts/prepare_raw_data.py \
  --output logs/raw_data_prepare.json \
  --overwrite
```

`logs/raw_data_prepare.json` 会记录 OK-VQA 样本数、COCO 图片数量、缺失文件和 `ready_for_prepare_okvqa`。在运行处理后数据转换前，`ready_for_prepare_okvqa` 必须为 `true`。

## 模型准备

默认模型：

```text
Qwen/Qwen3-VL-4B-Instruct -> models/Qwen3-VL-4B-Instruct
```

下载或校验默认 4B 模型：

```bash
python scripts/prepare_model.py \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

如果 Hugging Face Xet 下载很慢或不稳定，可以在命令前禁用 Xet：

```bash
HF_HUB_DISABLE_XET=1 python scripts/prepare_model.py \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

如果机器显存较小，可以下载文档约定的备选模型：

```bash
python scripts/prepare_model.py \
  --use_fallback \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

如果模型已经下载好，只想离线校验：

```bash
python scripts/prepare_model.py \
  --local_files_only \
  --output logs/model_prepare.json \
  --overwrite
```

`logs/model_prepare.json` 应显示 `status: passed` 和 `ready_for_baseline: true`。

## 基线前置检查

运行 E00/E01 基线前，先确认：

- `logs/env_check.json` 已生成，并且已经确认目标机器上的 CUDA/PyTorch 状态。
- `logs/raw_data_prepare.json` 中 `ready_for_prepare_okvqa: true`。
- `logs/model_prepare.json` 中 `ready_for_baseline: true`。
- raw 数据和模型权重不进入 git；只提交脚本、配置、文档、指标和小型摘要。

这些检查通过后，下一步是 `docs/CODING_AGENT_TASK_CARDS.md` 中的 Task 1：用 `scripts/prepare_okvqa.py` 把原始 OK-VQA 和 COCO 图片路径转换为项目统一 JSONL 格式。

## 数据准备（Task 1）

OK-VQA 数据处理脚本将 raw 标注与图片信息统一成 `data/processed/okvqa/` 下的标准格式（`train.jsonl`、`val.jsonl`），并生成校验统计与 10 条冒烟样本：

```bash
python3 scripts/prepare_okvqa.py \
  --raw_dir data/raw/okvqa \
  --image_root data/raw/coco \
  --output_dir data/processed/okvqa \
  --limit 20 \
  --seed 42 \
  --overwrite
```

生成文件：

- `data/processed/okvqa/train.jsonl`
- `data/processed/okvqa/val.jsonl`
- `data/processed/okvqa/stats.json`
- `data/samples/okvqa_10.jsonl`

单条样本字段（数据契约）：

- `sample_id`, `dataset`, `split`, `question_id`, `image_id`, `image_path`, `question`, `answers`, `answer`

`data/processed/okvqa/stats.json` 中会记录：

- 样本总数/按 split 样本数
- 空答案比例、空问题比例
- 图片路径抽查结果（检查数量、存在数、缺失数）
- 平均问题长度、平均答案长度、Top-20 高频答案

## 数据校验（Task 2）

在准备好 JSONL 后，先做快速数据一致性检查。`scripts/validate_data.py` 支持解析 JSON/JSONL、字段完整性、`sample_id` 唯一性、问题/答案非空、图片存在性、Qwen 格式 `<image>` 检查、train-eval 重叠检查。

最小自测（推荐）：

```bash
python3 scripts/validate_data.py \
  --input data/samples/okvqa_10.jsonl \
  --check_images \
  --output logs/validate_sample.json
```

如果当前图片未完整下载，可先用：

```bash
python3 scripts/validate_data.py \
  --input data/samples/okvqa_10.jsonl \
  --output logs/validate_sample.json
```

验证 train/val 泄漏（如有 `train` 和 `val` 文件）：

```bash
python3 scripts/validate_data.py \
  --input data/processed/okvqa/train.jsonl \
  --check_overlap \
  --train data/processed/okvqa/train.jsonl \
  --eval data/processed/okvqa/val.jsonl \
  --output logs/validate_train.json
```

通过标准：

- 脚本返回码为 0；
- `logs/validate_*.json` 为可解析 JSON；
- `sample_id` 不重复；
- `required_fields` 为 true；
- `checks.images_exist` 在完整环境下达到预期（若未下载图片，这一项会是 false）。

建议把 `data/processed/okvqa/` 和 `logs/` 的输出摘要提交到 `logs`，避免大文件被误提交。

## Phase 2：Prompt 模板库与短答案约束（Task 3）

本项目新增了可复用的 VQA prompt 模板与预览脚本，用于 E00/E01 基线一致性比较。

### 文件

- `prompts/okvqa_templates.json`：OK-VQA 任务的 6 个 short-answer 模板（含 `Answer with a short phrase only` 等约束）
- `prompts/vqa_templates.json`：通用 VQA 模板（可选）
- `scripts/preview_prompts.py`：从 `data/samples/okvqa_10.jsonl` 生成 prompt 渲染预览

### 快速预览命令

```bash
python3 scripts/preview_prompts.py \
  --input data/samples/okvqa_10.jsonl \
  --template_file prompts/okvqa_templates.json \
  --output logs/prompt_preview.md \
  --overwrite
```

预览文件会把 `{question}` 被替换后的最终 prompt 输出，便于人工审核是否包含 `<image>`、short-answer 约束与模板可读性。

## Phase 3：推理脚本与 zero-shot/prompt-only baseline（Task 6/7）

本阶段新增了统一推理链路和评测链路：

- `src/fdvit/model_qwen.py`：模型加载（支持本地模型优先，支持 LoRA checkpoint 挂载）
- `src/fdvit/inference.py`：逐条/批量推理核心逻辑
- `src/fdvit/prompts.py`：模板加载与渲染
- `scripts/run_inference.py`：零样本/Prompt-only 实验主脚本
- `scripts/evaluate_vqa.py`：统一评测脚本（`acc_any`、`acc_soft`、`format_error_rate`）
- `scripts/normalize_answer.py`：答案归一化入口
- `src/fdvit/evaluation.py`：规范化与指标计算函数
- 配置：`configs/infer_zero_shot.yaml`、`configs/infer_prompt_only.yaml`

### 小样本 smoke test

先在 `data/samples/okvqa_10.jsonl` 上跑 10 条，确认链路与输出格式：

```bash
python3 scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/samples/okvqa_10.jsonl \
  --output outputs/debug_zero_shot/predictions.jsonl \
  --limit 10 \
  --seed 42 \
  --overwrite

python3 scripts/evaluate_vqa.py \
  --predictions outputs/debug_zero_shot/predictions.jsonl \
  --output outputs/debug_zero_shot/metrics.json \
  --error_output outputs/debug_zero_shot/errors.jsonl \
  --overwrite
```

### 运行 E00 / E01 baseline

默认要求已完成模型与数据准备，并且在 `fd-vit` 环境中可运行（本地模型建议：
`models/Qwen3-VL-4B-Instruct`）。

```bash
# 1) zero-shot baseline（E00）
python3 scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --output outputs/E00_zero_shot_basic/predictions.jsonl \
  --seed 42 \
  --overwrite

python3 scripts/evaluate_vqa.py \
  --predictions outputs/E00_zero_shot_basic/predictions.jsonl \
  --output outputs/E00_zero_shot_basic/metrics.json \
  --error_output outputs/E00_zero_shot_basic/errors.jsonl \
  --overwrite

# 2) prompt-only baseline（E01）
python3 scripts/run_inference.py \
  --config configs/infer_prompt_only.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --output outputs/E01_prompt_strict/predictions.jsonl \
  --seed 42 \
  --overwrite

python3 scripts/evaluate_vqa.py \
  --predictions outputs/E01_prompt_strict/predictions.jsonl \
  --output outputs/E01_prompt_strict/metrics.json \
  --error_output outputs/E01_prompt_strict/errors.jsonl \
  --overwrite
```

### baseline 结果如何获取

每个实验目录会产生可复现的结果文件（推荐保留）：

- `outputs/<exp>/predictions.jsonl`：逐样本预测
- `outputs/<exp>/metrics.json`：聚合指标
- `outputs/<exp>/errors.jsonl`：错误样本（供后续 failure mining）
- `outputs/<exp>/run_config.yaml`：本次实验参数
- `outputs/<exp>/command.txt`：完整执行命令
- `outputs/<exp>/environment.txt`：运行环境版本信息

可用如下命令提取可写入报告的指标：

```bash
cat outputs/E00_zero_shot_basic/metrics.json
cat outputs/E01_prompt_strict/metrics.json
wc -l outputs/E00_zero_shot_basic/predictions.jsonl
wc -l outputs/E01_prompt_strict/predictions.jsonl
```

如需同时观察 E00/E01 对比：

```bash
python3 - <<'PY'
import json
for exp in ['E00_zero_shot_basic', 'E01_prompt_strict']:
    with open(f'outputs/{exp}/metrics.json', 'r', encoding='utf-8') as f:
        m = json.load(f)
    print(exp, 'acc_any=', m.get('acc_any'), 'acc_soft=', m.get('acc_soft'), 'format_error=', m.get('format_error_rate'))
PY
```

若训练/下载环境不稳定（无法访问 HF 或模型未完整下载），可先产出 `outputs/debug_zero_shot` 的流程验证，确认脚本可用后再在外部可联网环境补齐完整模型后重跑 baseline。
