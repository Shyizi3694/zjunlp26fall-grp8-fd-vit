# FD-VIT Coding Agent 任务卡

本文档把主控计划拆成可直接派发给 coding agent 的任务卡。每张任务卡包含目标、输入、输出、实现要求、自测命令和完成标准。

---

## 使用方式

每次只派发一张任务卡。coding agent 完成后必须返回：

- 修改了哪些文件；
- 新增了哪些文件；
- 运行了哪些命令；
- 自测是否通过；
- 生成了哪些产物；
- 还存在哪些风险。

---

# Task 0：创建项目骨架与环境检查

## 目标

创建标准 repo 结构，写环境检查脚本。

## 输入

无。

## 输出

```text
requirements.txt
.gitignore
scripts/check_env.py
configs/base.yaml
logs/env_check.json
```

## 实现要求

`check_env.py` 必须输出：

- Python version；
- OS；
- CUDA availability；
- GPU name；
- GPU memory；
- PyTorch version；
- Transformers version；
- PEFT version；
- bitsandbytes availability；
- working directory。

## 自测命令

```bash
python scripts/check_env.py --output logs/env_check.json
```

## 完成标准

- 命令成功；
- `logs/env_check.json` 存在；
- 不依赖绝对路径；
- `.gitignore` 排除大文件目录。

---

# Task 1：实现 OK-VQA 数据准备脚本

## 目标

将原始 OK-VQA annotation 和 COCO image path 转成项目统一 JSONL。

## 输入

```text
data/raw/okvqa/
data/raw/coco/
```

## 输出

```text
data/processed/okvqa/train.jsonl
data/processed/okvqa/val.jsonl
data/processed/okvqa/stats.json
data/samples/okvqa_10.jsonl
```

## 实现要求

脚本：`scripts/prepare_okvqa.py`

支持参数：

```bash
--raw_dir
--image_root
--output_dir
--limit
--seed
--overwrite
```

每条样本必须包含：

- `sample_id`
- `dataset`
- `split`
- `question_id`
- `image_id`
- `image_path`
- `question`
- `answers`
- `answer`

## 自测命令

```bash
python scripts/prepare_okvqa.py \
  --raw_dir data/raw/okvqa \
  --image_root data/raw/coco \
  --output_dir data/processed/okvqa \
  --limit 20 \
  --seed 42 \
  --overwrite
```

## 完成标准

- JSONL 可解析；
- 每行字段完整；
- `stats.json` 包含样本数、空答案比例、图片路径检查结果；
- 生成 `data/samples/okvqa_10.jsonl`。

---

# Task 2：实现数据校验器

## 目标

检查 processed 数据和 Qwen 训练数据是否符合格式契约。

## 输入

```text
data/processed/okvqa/train.jsonl
```

## 输出

```text
logs/validate_train.json
```

## 实现要求

脚本：`scripts/validate_data.py`

支持检查：

- JSON/JSONL 可解析；
- required fields；
- sample_id 唯一；
- question 非空；
- answers 非空；
- image_path 存在；
- train/eval overlap；
- Qwen 格式 `<image>` 检查。

## 自测命令

```bash
python scripts/validate_data.py \
  --input data/samples/okvqa_10.jsonl \
  --check_images \
  --output logs/validate_sample.json
```

## 完成标准

- 对 10 条样本通过校验；
- 缺字段时能给出清晰错误；
- 输出 JSON summary。

---

# Task 3：实现 prompt 模板库与预览脚本

## 目标

创建 OK-VQA prompt 模板并生成预览。

## 输入

```text
data/samples/okvqa_10.jsonl
```

## 输出

```text
prompts/okvqa_templates.json
logs/prompt_preview.md
```

## 实现要求

- 至少 6 个 VQA 模板；
- 每个模板包含 `<image>`；
- 每个模板包含 `{question}`；
- 每个模板要求 short answer；
- 脚本 `scripts/preview_prompts.py` 能输出填充后的 prompt。

## 自测命令

```bash
python scripts/preview_prompts.py \
  --input data/samples/okvqa_10.jsonl \
  --template_file prompts/okvqa_templates.json \
  --output logs/prompt_preview.md
```

## 完成标准

- 预览文件可读；
- 模板 ID 唯一；
- 无模板缺少短答案约束。

---

# Task 4：实现 Qwen 训练格式转换

## 目标

将统一 JSONL 转成 Qwen3-VL instruction tuning 格式。

## 输入

```text
data/processed/okvqa/train.jsonl
prompts/okvqa_templates.json
```

## 输出

```text
data/processed/okvqa/train_qwen.json
```

## 实现要求

脚本：`scripts/convert_to_qwen_format.py`

支持参数：

```bash
--input
--output
--template_file
--template_id
--template_mode single|multi
--seed
--limit
--overwrite
```

输出样本格式：

```json
{
  "id": "...",
  "image": "...",
  "conversations": [
    {"from": "human", "value": "<image>\nQuestion: ..."},
    {"from": "gpt", "value": "..."}
  ],
  "metadata": {"template_id": "..."}
}
```

## 自测命令

```bash
python scripts/convert_to_qwen_format.py \
  --input data/samples/okvqa_10.jsonl \
  --output data/samples/okvqa_10_qwen.json \
  --template_file prompts/okvqa_templates.json \
  --template_mode multi \
  --seed 42 \
  --overwrite
```

## 完成标准

- 输出 JSON 可解析；
- 每条有 `<image>`；
- 每条有 human/gpt 两轮对话；
- gpt answer 是短答案。

---

# Task 5：实现答案 normalization 与 VQA 评测

## 目标

实现统一评测脚本，输出 acc_any、acc_soft、format_error_rate。

## 输入

```text
outputs/*/predictions.jsonl
```

## 输出

```text
outputs/*/metrics.json
outputs/*/errors.jsonl
```

## 实现要求

脚本：

- `scripts/normalize_answer.py`
- `scripts/evaluate_vqa.py`
- `src/fdvit/evaluation.py`

normalization 至少支持：

- lowercase；
- 去标点；
- 数字词转数字；
- 去冠词；
- 压缩空格；
- 保守去除 `the answer is` 等前缀。

## 自测命令

先创建一个 5 行 toy prediction 文件，再运行：

```bash
python scripts/evaluate_vqa.py \
  --predictions data/samples/toy_predictions.jsonl \
  --output outputs/debug_eval/metrics.json \
  --error_output outputs/debug_eval/errors.jsonl \
  --overwrite
```

## 完成标准

- toy examples 结果符合人工预期；
- metrics.json 字段完整；
- errors.jsonl 只含错误样本；
- prediction schema 与 DATA_AND_FORMAT_CONTRACT.md 一致。

---

# Task 6：实现 Qwen3-VL 批量推理脚本

## 目标

用统一脚本跑 zero-shot、prompt-only 和 LoRA checkpoint 推理。

## 输入

```text
data/processed/okvqa/val_1k.jsonl
configs/infer_zero_shot.yaml
```

## 输出

```text
outputs/E00_zero_shot_basic/predictions.jsonl
```

## 实现要求

脚本：`scripts/run_inference.py`

支持：

- base model 加载；
- 可选 LoRA checkpoint；
- 图片 + prompt 输入；
- batch 或逐条推理；
- max_new_tokens；
- temperature；
- resume；
- limit；
- seed；
- 失败样本记录。

## 自测命令

```bash
python scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/samples/okvqa_10.jsonl \
  --output outputs/debug_zero_shot/predictions.jsonl \
  --limit 10 \
  --seed 42 \
  --overwrite
```

## 完成标准

- 10 条样本可完成推理；
- 输出字段完整；
- 推理失败不导致整个程序崩溃；
- 支持断点续跑。

---

# Task 7：跑 E00 / E01 baseline

## 目标

生成 zero-shot 与 prompt-only baseline。

## 输入

```text
data/processed/okvqa/val_1k.jsonl
configs/infer_zero_shot.yaml
configs/infer_prompt_only.yaml
```

## 输出

```text
outputs/E00_zero_shot_basic/
outputs/E01_prompt_strict/
```

## 命令

```bash
python scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --output outputs/E00_zero_shot_basic/predictions.jsonl \
  --seed 42

python scripts/evaluate_vqa.py \
  --predictions outputs/E00_zero_shot_basic/predictions.jsonl \
  --output outputs/E00_zero_shot_basic/metrics.json \
  --error_output outputs/E00_zero_shot_basic/errors.jsonl

python scripts/run_inference.py \
  --config configs/infer_prompt_only.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --output outputs/E01_prompt_strict/predictions.jsonl \
  --seed 42

python scripts/evaluate_vqa.py \
  --predictions outputs/E01_prompt_strict/predictions.jsonl \
  --output outputs/E01_prompt_strict/metrics.json \
  --error_output outputs/E01_prompt_strict/errors.jsonl
```

## 完成标准

- E00/E01 都有 predictions、metrics、errors；
- 行数一致；
- metrics 可被 summarize 脚本读取；
- 记录 prompt 模板 ID。

---

# Task 8：实现 failure mining

## 目标

从 baseline 错误样本中生成带错误类型的 failure 文件。

## 输入

```text
outputs/E01_prompt_strict/predictions.jsonl
outputs/E01_prompt_strict/errors.jsonl
```

## 输出

```text
outputs/E01_prompt_strict/failures_mined.jsonl
outputs/E01_prompt_strict/error_summary.csv
```

## 实现要求

脚本：`scripts/mine_failures.py`

支持：

- 读取 predictions 或 errors；
- 自动弱标注 error type；
- 输出 error_summary；
- 支持人工复核字段；
- 支持导出 CSV。

## 自测命令

```bash
python scripts/mine_failures.py \
  --predictions outputs/E01_prompt_strict/predictions.jsonl \
  --output outputs/E01_prompt_strict/failures_mined.jsonl \
  --summary outputs/E01_prompt_strict/error_summary.csv \
  --overwrite
```

## 完成标准

- 每条错误样本有 `error_type_auto`；
- summary 中有各类错误数量；
- answer_format、counting、ocr_text、spatial 至少能被启发式识别。

---

# Task 9：构造 random / failure-driven 训练子集

## 目标

生成同规模 random 和 failure-driven 训练集。

## 输入

```text
data/processed/okvqa/train.jsonl
outputs/train_probe/failures_mined.jsonl
```

## 输出

```text
data/processed/okvqa/train_random_2k.jsonl
data/processed/okvqa/train_failure_2k.jsonl
data/processed/okvqa/train_random_2k_qwen.json
data/processed/okvqa/train_failure_2k_qwen.json
```

## 实现要求

脚本：`scripts/build_training_subset.py`

支持：

- `--strategy random|failure_driven`；
- `--n`；
- `--seed`；
- error type 权重；
- 不足样本自动补齐；
- 输出 subset stats。

## 自测命令

```bash
python scripts/build_training_subset.py \
  --train data/processed/okvqa/train.jsonl \
  --strategy random \
  --n 100 \
  --seed 42 \
  --output data/samples/train_random_100.jsonl \
  --overwrite
```

## 完成标准

- 两个 subset 样本数一致；
- sample_id 不重复；
- 不含 val/test 样本；
- 输出 stats；
- Qwen 格式转换通过。

---

# Task 10：编写 LoRA 训练配置与脚本

## 目标

准备 LoRA-random 和 LoRA-failure 训练。

## 输入

```text
data/processed/okvqa/train_random_2k_qwen.json
data/processed/okvqa/train_failure_2k_qwen.json
```

## 输出

```text
configs/lora_random_2k.yaml
configs/lora_failure_2k.yaml
scripts/train_lora.sh
```

## 实现要求

- 两个 config 除 train data 和 output_dir 外保持一致；
- 支持 LoRA r=8；
- 支持 QLoRA fallback；
- 保存 command 和 environment；
- 训练失败时清楚报错。

## 自测命令

```bash
bash scripts/train_lora.sh configs/lora_random_2k.yaml --dry_run
```

## 完成标准

- dry run 展示训练命令；
- config 字段完整；
- 不包含绝对路径；
- 随机种子固定。

---

# Task 11：评测 LoRA checkpoint

## 目标

对 LoRA-random 和 LoRA-failure 使用同一 val set 评测。

## 输入

```text
checkpoints/lora_random_2k/
checkpoints/lora_failure_2k/
data/processed/okvqa/val_1k.jsonl
```

## 输出

```text
outputs/E02_lora_random_2k_r8/
outputs/E03_lora_failure_2k_r8/
```

## 命令

```bash
python scripts/run_inference.py \
  --config configs/infer_lora_random_2k.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --lora_checkpoint checkpoints/lora_random_2k \
  --output outputs/E02_lora_random_2k_r8/predictions.jsonl \
  --seed 42

python scripts/evaluate_vqa.py \
  --predictions outputs/E02_lora_random_2k_r8/predictions.jsonl \
  --output outputs/E02_lora_random_2k_r8/metrics.json \
  --error_output outputs/E02_lora_random_2k_r8/errors.jsonl
```

对 failure checkpoint 重复同样流程。

## 完成标准

- E02/E03 metrics 存在；
- 使用相同 eval set；
- 预测行数一致；
- 可复现完整命令。

---

# Task 12：汇总主结果表

## 目标

从各实验 metrics 自动生成主结果表。

## 输入

```text
outputs/E00_*/metrics.json
outputs/E01_*/metrics.json
outputs/E02_*/metrics.json
outputs/E03_*/metrics.json
```

## 输出

```text
outputs/results_main.csv
outputs/results_main.md
```

## 实现要求

脚本：`scripts/summarize_results.py`

支持：

- 扫描 outputs；
- 读取 metrics；
- 按 Exp ID 排序；
- 计算 delta；
- 输出 CSV 和 Markdown。

## 自测命令

```bash
python scripts/summarize_results.py \
  --outputs outputs \
  --output_csv outputs/results_main.csv \
  --output_md outputs/results_main.md
```

## 完成标准

- 表格包含 E00–E03；
- delta 计算正确；
- 数值保留 3 或 4 位小数；
- 报告可直接引用。

---

# Task 13：错误类型对比与 case study

## 目标

生成错误类型对比表和 qualitative case study。

## 输入

```text
outputs/E00_*/predictions.jsonl
outputs/E02_*/predictions.jsonl
outputs/E03_*/predictions.jsonl
```

## 输出

```text
outputs/error_comparison.csv
outputs/error_comparison.md
outputs/case_studies.md
```

## 实现要求

脚本：

- `scripts/compare_errors.py`
- `scripts/make_case_study_table.py`

case study 应包括：

- image path；
- question；
- GT answers；
- zero-shot prediction；
- random LoRA prediction；
- failure LoRA prediction；
- error type；
- note。

## 自测命令

```bash
python scripts/compare_errors.py \
  --exp_dirs outputs/E00_zero_shot_basic outputs/E01_prompt_strict outputs/E02_lora_random_2k_r8 outputs/E03_lora_failure_2k_r8 \
  --output_csv outputs/error_comparison.csv \
  --output_md outputs/error_comparison.md

python scripts/make_case_study_table.py \
  --exp_dirs outputs/E00_zero_shot_basic outputs/E02_lora_random_2k_r8 outputs/E03_lora_failure_2k_r8 \
  --output outputs/case_studies.md \
  --num_cases 10 \
  --seed 42
```

## 完成标准

- 至少 6 个 case；
- 包含成功和失败案例；
- 错误类型表可直接放报告。

---

# Task 14：可选 GUI grounding demo

## 目标

完成小规模 GUI grounding bonus，不影响主线。

## 输入

```text
data/raw/gui/screenspot_pro/
data/processed/gui/val_small.jsonl
```

## 输出

```text
data/raw/gui/screenspot_pro/annotations/*.json
data/raw/gui/screenspot_pro/images/
data/processed/gui/val_small.jsonl
data/processed/gui/val_small.summary.json
data/samples/gui_grounding_5.jsonl
outputs/B01_gui_grounding_demo/predictions.jsonl
outputs/B01_gui_grounding_demo/metrics.json
outputs/B01_gui_grounding_demo/errors.jsonl
```

## 实现要求

- 数据源默认使用 Hugging Face dataset `likaixin/ScreenSpot-Pro`；
- 默认只做小样本，如 `vscode_macos` + `--limit 20`；
- 脚本 `scripts/prepare_gui_grounding.py` 支持下载 annotation、下载选中图片、转换为统一 GUI JSONL；
- 脚本 `scripts/run_gui_grounding.py` 使用 Qwen3-VL 对 GUI 截图预测目标坐标；
- 脚本 `scripts/evaluate_gui_grounding.py` 读取 predictions 并输出 metrics；
- 预测坐标点；
- 解析 `(x, y)`；
- 计算 point-in-bbox；
- 计算 center distance；
- 记录 `parse_success_rate`、`control_type_metrics`；
- 只做 demo，不加入主结果表。

## 从 0 运行命令

### 1. 下载并转换小样本

```bash
python scripts/prepare_gui_grounding.py \
  --download \
  --download_images \
  --tasks vscode_macos \
  --limit 20 \
  --seed 42 \
  --output data/processed/gui/val_small.jsonl \
  --sample_output data/samples/gui_grounding_5.jsonl \
  --check_images \
  --overwrite
```

### 2. 校验数据

```bash
python scripts/validate_data.py \
  --input data/processed/gui/val_small.jsonl \
  --check_images \
  --expect_split val \
  --output logs/validate_gui_val_small.json \
  --overwrite
```

### 3. 推理前 dry run

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --limit 2 \
  --dry_run
```

### 4. CUDA 环境真实推理

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --overwrite
```

### 5. 评测

```bash
python scripts/evaluate_gui_grounding.py \
  --predictions outputs/B01_gui_grounding_demo/predictions.jsonl \
  --output outputs/B01_gui_grounding_demo/metrics.json \
  --error_output outputs/B01_gui_grounding_demo/errors.jsonl \
  --overwrite
```

## 自测命令

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --limit 2 \
  --dry_run

python scripts/evaluate_gui_grounding.py \
  --predictions outputs/B01_gui_grounding_demo/predictions.jsonl \
  --output outputs/B01_gui_grounding_demo/metrics.json \
  --error_output outputs/B01_gui_grounding_demo/errors.jsonl \
  --overwrite
```

## 完成标准

- 小样本可运行；
- `data/processed/gui/val_small.jsonl` 通过 `validate_data.py --check_images`；
- `outputs/B01_gui_grounding_demo/predictions.jsonl` 为逐样本 JSONL；
- `metrics.json` 包含 `point_in_bbox_acc`、`parse_success_rate`、`center_distance_norm`；
- 坐标解析成功率有记录；
- 结果作为附录，不干扰主线。
