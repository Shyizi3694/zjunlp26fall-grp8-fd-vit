# FD-VIT Coding Agent 全程执行指南

版本：v0.1  
适用项目：NLP 课程大作业，MLLM / 视觉推理方向  
项目简称：FD-VIT  
推荐题目：**基于失败驱动指令微调的多模态视觉推理增强**

---

## 0. 文档目的

本文档是给 coding agent 与团队成员使用的主控说明。它不只是项目计划，而是一个可执行的工程协议：

- 每个阶段要准备什么；
- 每个阶段要写哪些代码；
- 每个阶段要跑哪些实验；
- 每个阶段要产出哪些文件；
- 每个阶段用什么指标验收；
- 什么事情不能做，避免项目膨胀或结果不可信。

coding agent 每次开始任务前，应先阅读本文档与相关附录，并遵守其中的文件格式、命名、实验和评测约束。

---

## 1. 项目主线与范围边界

### 1.1 固定主线

本项目只保留一条主线：

```text
Qwen3-VL-4B-Instruct
→ OK-VQA / VQA 子集
→ zero-shot baseline
→ prompt-only baseline
→ LoRA-random instruction tuning
→ LoRA-failure-driven instruction tuning
→ 错误类型分析
→ 可选 GUI grounding bonus
```

核心研究问题：

> 在相同模型、相同训练规模、相同 LoRA 配置下，failure-driven instruction tuning 是否优于 random instruction tuning？

### 1.2 默认标准版配置

| 项目 | 默认配置 |
|---|---|
| 主模型 | Qwen3-VL-4B-Instruct |
| 低显存备选 | Qwen3-VL-2B-Instruct 或 4B + QLoRA |
| 主数据集 | OK-VQA，必要时使用 VQA v2 子集 |
| 主任务 | open-ended visual question answering |
| 训练方法 | LoRA；显存不足时 QLoRA 或 projector-only |
| 默认 LoRA rank | r=8 |
| 训练规模 | 先 2k，跑通后再 5k |
| 评测规模 | 先 1k val subset，最终 5k 或完整 val |
| 模板策略 | 多模板 instruction + short answer 约束 |
| 主创新变量 | random sampling vs failure-driven sampling |
| 主指标 | VQA/OK-VQA accuracy、分类错误率、输出格式错误率 |

### 1.3 不作为主线的内容

以下内容除非主线已经完整跑通，否则不得加入主实验矩阵：

- Janus-Pro 对比；
- text-to-image / 图像生成；
- 完整 GUI Agent；
- 多模型大规模对比；
- LoRA rank 8 / 16 / 32 全量消融；
- 1k / 5k / 10k / full 全数据规模消融；
- 自动化复杂错误分类器训练。

允许的 bonus：

- 小规模 GUI grounding demo；
- LoRA rank 8 vs 16 小消融；
- 1k vs 5k 数据规模小消融；
- 单模板 vs 多模板小消融。

### 1.4 结果可信度底线

最终报告必须至少包含：

1. zero-shot baseline；
2. prompt-only baseline；
3. LoRA-random；
4. LoRA-failure-driven；
5. 统一评测脚本；
6. 逐样本 prediction 文件；
7. 错误类型分析；
8. 6–10 个 qualitative cases；
9. 明确说明失败驱动采样没有污染最终测试集。

---

## 2. 推荐 repo 结构

coding agent 应以如下结构为目标，不要随意创建散乱目录：

```text
FD-VIT/
├── README.md
├── requirements.txt
├── pyproject.toml                         # 可选
├── configs/
│   ├── infer_zero_shot.yaml
│   ├── infer_prompt_only.yaml
│   ├── lora_random_2k.yaml
│   ├── lora_failure_2k.yaml
│   ├── lora_random_5k.yaml                # 可选
│   └── lora_failure_5k.yaml               # 可选
├── data/
│   ├── raw/                               # 原始数据，禁止手改
│   ├── interim/                           # 中间转换结果
│   ├── processed/                         # 训练/评测直接读取
│   ├── samples/                           # 小样本调试数据
│   └── README.md
├── prompts/
│   ├── okvqa_templates.json
│   ├── vqa_templates.json
│   └── README.md
├── scripts/
│   ├── prepare_okvqa.py
│   ├── prepare_vqa.py                     # 可选
│   ├── convert_to_qwen_format.py
│   ├── validate_data.py
│   ├── run_inference.py
│   ├── evaluate_vqa.py
│   ├── normalize_answer.py
│   ├── mine_failures.py
│   ├── build_training_subset.py
│   ├── train_lora.sh
│   ├── merge_lora.py                      # 可选
│   ├── summarize_results.py
│   └── make_case_study_table.py
├── src/
│   └── fdvit/
│       ├── __init__.py
│       ├── data.py
│       ├── prompts.py
│       ├── model_qwen.py
│       ├── inference.py
│       ├── evaluation.py
│       ├── failure_mining.py
│       └── utils.py
├── outputs/
│   ├── zero_shot/
│   ├── prompt_only/
│   ├── lora_random/
│   ├── lora_failure/
│   └── bonus_gui/
├── checkpoints/
│   ├── lora_random_2k/
│   └── lora_failure_2k/
├── logs/
├── docs/
│   ├── README.md
│   ├── FD_VIT_CODING_AGENT_GUIDE.md
│   ├── DATA_AND_FORMAT_CONTRACT.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── ERROR_TAXONOMY.md
│   ├── CODING_AGENT_TASK_CARDS.md
│   └── REPORT_CHECKLIST.md
└── notebooks/
    └── error_analysis.ipynb                # 可选
```

---

## 3. 全局工程规则

### 3.1 所有脚本必须具备的能力

每个 Python 脚本必须支持 CLI 参数，至少包括：

- `--input` 或 `--input_dir`；
- `--output` 或 `--output_dir`；
- `--config`，如果脚本依赖配置；
- `--seed`，如果涉及采样；
- `--limit`，用于小样本 debug；
- `--overwrite`，避免误删已有结果；
- `--log_file`，用于记录运行信息。

示例：

```bash
python scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/processed/okvqa_val_1k.jsonl \
  --output outputs/zero_shot/predictions.jsonl \
  --limit 100 \
  --seed 42
```

### 3.2 每个脚本必须可小样本自测

每个脚本都应能在 `data/samples/` 上运行。coding agent 不允许直接写一个只能在全量数据上跑的脚本。

最小自测命令示例：

```bash
python scripts/validate_data.py \
  --input data/samples/okvqa_10.jsonl
```

### 3.3 结果文件不可覆盖

默认不得覆盖已有结果。需要覆盖时必须显式传入 `--overwrite`。

### 3.4 所有实验必须记录 metadata

每个实验目录必须包含：

```text
outputs/<exp_name>/
├── predictions.jsonl
├── metrics.json
├── run_config.yaml
├── command.txt
├── environment.txt
└── error_summary.csv
```

其中：

- `command.txt` 记录完整命令；
- `environment.txt` 记录 Python、CUDA、PyTorch、Transformers、PEFT 等版本；
- `metrics.json` 记录 aggregate metrics；
- `predictions.jsonl` 记录逐样本预测；
- `error_summary.csv` 记录错误类型统计。

### 3.5 任何指标必须可复现

不得只手工记录表格数字。所有报告中的表格数字必须能由 `scripts/summarize_results.py` 从 `outputs/` 自动汇总得到。

---

## 4. 分阶段执行计划

下面每个阶段都包含：目标、准备、需要写的代码、需要跑的实验、指标、产物、验收标准。

---

# Phase 0：项目冻结与环境基线

## 0.1 目标

建立项目骨架，冻结主线，跑通最小环境检查，确保后续 coding agent 不会在错误目录和错误依赖上开发。

## 0.2 准备工作

- 确定当前机器 GPU 显存；
- 确定模型使用 Qwen3-VL-4B-Instruct 或低显存备选；
- 创建 repo 结构；
- 创建 docs、configs、scripts、src、data、outputs、logs；
- 写入 `.gitignore`，避免提交大模型权重、原始图片、checkpoint。

## 0.3 需要写的代码/文件

- `requirements.txt`
- `.gitignore`
- `scripts/check_env.py`
- `configs/base.yaml`
- `docs/README.md`

`check_env.py` 至少输出：

- Python version；
- OS；
- CUDA 是否可用；
- GPU 名称与显存；
- PyTorch version；
- Transformers version；
- PEFT version；
- bitsandbytes 是否可用；
- 当前 working directory。

## 0.4 推荐命令

```bash
python scripts/check_env.py --output logs/env_check.json
```

## 0.5 验收标准

- `python scripts/check_env.py` 能成功运行；
- `logs/env_check.json` 存在；
- `README.md` 中写清楚项目主线；
- `docs/` 中至少有本指南与实验协议；
- `.gitignore` 正确排除 `data/raw/`、`checkpoints/`、`outputs/*/predictions.jsonl` 等大文件。

---

# Phase 1：数据准备与格式契约

## 1.1 目标

将 OK-VQA / VQA 数据转换成项目统一 JSONL，并进一步转换成 Qwen3-VL instruction tuning 格式。

## 1.2 输入

- OK-VQA train/val annotations；
- 对应 COCO images；
- 可选 VQA v2 子集。

## 1.3 需要写的代码

- `scripts/prepare_okvqa.py`
- `scripts/prepare_vqa.py`，可选；
- `scripts/convert_to_qwen_format.py`
- `scripts/validate_data.py`
- `src/fdvit/data.py`

## 1.4 统一中间格式

项目内部统一样本格式为 JSONL，每行一个样本：

```json
{
  "sample_id": "okvqa_train_000000001",
  "dataset": "okvqa",
  "split": "train",
  "question_id": 123,
  "image_id": 456,
  "image_path": "data/raw/coco/train2014/COCO_train2014_000000000456.jpg",
  "question": "What sport is this person playing?",
  "answers": ["tennis", "tennis", "tennis", "badminton", "tennis"],
  "answer": "tennis",
  "metadata": {
    "source_file": "...",
    "license_note": "follow dataset license"
  }
}
```

字段要求详见 `DATA_AND_FORMAT_CONTRACT.md`。

## 1.5 Qwen3-VL 训练格式

训练格式示例：

```json
{
  "id": "okvqa_train_000000001",
  "image": "data/raw/coco/train2014/COCO_train2014_000000000456.jpg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nQuestion: What sport is this person playing?\nAnswer with a short phrase only. Do not explain."
    },
    {
      "from": "gpt",
      "value": "tennis"
    }
  ]
}
```

## 1.6 需要跑的实验/检查

此阶段不跑模型，只做数据检查：

```bash
python scripts/prepare_okvqa.py \
  --raw_dir data/raw/okvqa \
  --image_root data/raw/coco \
  --output_dir data/processed/okvqa

python scripts/validate_data.py \
  --input data/processed/okvqa/train.jsonl \
  --check_images \
  --limit 100

python scripts/convert_to_qwen_format.py \
  --input data/processed/okvqa/train.jsonl \
  --output data/processed/okvqa/train_qwen.json \
  --template_file prompts/okvqa_templates.json \
  --template_mode multi \
  --seed 42
```

## 1.7 指标与统计

必须输出：

- train/val 样本数；
- 图片存在率；
- 空问题比例；
- 空答案比例；
- 平均问题长度；
- 平均答案长度；
- top-20 answer frequency；
- 随机样本预览。

## 1.8 产物

```text
data/processed/okvqa/train.jsonl
data/processed/okvqa/val.jsonl
data/processed/okvqa/train_qwen.json
data/processed/okvqa/val_qwen.json
data/processed/okvqa/stats.json
data/samples/okvqa_10.jsonl
```

## 1.9 验收标准

- `validate_data.py` 对 100 个样本图片路径检查通过率 ≥ 99%；
- 每个样本有 `sample_id`、`question_id`、`image_path`、`question`、`answers`；
- Qwen 格式中每个样本有 `<image>`；
- 所有训练输出答案是短答案，不包含长解释。

---

# Phase 2：Prompt 模板库与 short-answer 约束

## 2.1 目标

建立统一 prompt 模板库，为 zero-shot、prompt-only、instruction tuning 提供可复用模板。

## 2.2 需要写的代码/文件

- `prompts/okvqa_templates.json`
- `prompts/vqa_templates.json`
- `src/fdvit/prompts.py`
- `scripts/preview_prompts.py`

## 2.3 模板要求

所有 VQA prompt 必须包含：

```text
Answer with a short phrase only. Do not explain.
```

或者等价短答案约束。

推荐模板示例：

```json
[
  {
    "template_id": "okvqa_short_001",
    "text": "<image>\nQuestion: {question}\nAnswer with a short phrase only. Do not explain."
  },
  {
    "template_id": "okvqa_short_002",
    "text": "<image>\nLook at the image and answer the question.\nQuestion: {question}\nGive only the answer, not a full sentence."
  },
  {
    "template_id": "okvqa_short_003",
    "text": "<image>\nBased on the image, answer this question: {question}\nShort answer:"
  }
]
```

## 2.4 prompt-only baseline 设计

至少比较两个 prompt：

| Prompt | 目的 |
|---|---|
| basic | 原始短答案 prompt |
| strict_short | 更严格控制输出格式 |

不要把 prompt-only 做成十几个模板大搜索；最多 2–4 个模板即可。

## 2.5 需要跑的检查

```bash
python scripts/preview_prompts.py \
  --input data/samples/okvqa_10.jsonl \
  --template_file prompts/okvqa_templates.json \
  --output logs/prompt_preview.md
```

## 2.6 验收标准

- 模板能正确填充 `{question}`；
- 每条 prompt 中有 `<image>`；
- short-answer 约束存在；
- 输出 preview 易读，可直接给团队审核。

---

# Phase 3：推理脚本与 zero-shot baseline

## 3.1 目标

跑通 Qwen3-VL 的批量推理，生成 zero-shot 结果，形成后续 failure mining 的输入。

## 3.2 需要写的代码

- `src/fdvit/model_qwen.py`
- `src/fdvit/inference.py`
- `scripts/run_inference.py`

## 3.3 推理脚本要求

`run_inference.py` 必须支持：

- 从 JSONL 读取样本；
- 根据模板生成 prompt；
- 读取图片路径；
- 批量或逐条推理；
- 断点续跑；
- 限制最大生成 token；
- 输出逐样本 JSONL；
- 记录失败样本和异常；
- 可指定 LoRA checkpoint，后续复用同一脚本评测微调模型。

## 3.4 预测输出格式

```json
{
  "sample_id": "okvqa_val_000000001",
  "dataset": "okvqa",
  "split": "val",
  "question_id": 123,
  "image_id": 456,
  "image_path": "data/raw/coco/val2014/COCO_val2014_000000000456.jpg",
  "question": "What sport is this person playing?",
  "answers": ["tennis", "tennis", "tennis", "badminton", "tennis"],
  "prompt": "<image>\nQuestion: ...",
  "template_id": "okvqa_short_001",
  "prediction_raw": "The answer is tennis.",
  "prediction": "tennis",
  "model_id": "Qwen3-VL-4B-Instruct",
  "checkpoint": null,
  "generation_config": {
    "max_new_tokens": 16,
    "temperature": 0.0
  },
  "runtime": {
    "latency_sec": 0.84
  }
}
```

## 3.5 推荐命令

小样本 smoke test：

```bash
python scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/samples/okvqa_10.jsonl \
  --output outputs/debug_zero_shot/predictions.jsonl \
  --limit 10 \
  --seed 42
```

正式 1k baseline：

```bash
python scripts/run_inference.py \
  --config configs/infer_zero_shot.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --output outputs/zero_shot_val_1k/predictions.jsonl \
  --seed 42
```

## 3.6 指标

此阶段先不要求最终 accuracy，但至少统计：

- 推理成功率；
- 平均生成长度；
- 空输出比例；
- 异常样本数；
- 平均 latency；
- 预测文件行数是否等于输入样本数。

## 3.7 验收标准

- 小样本 10 条推理成功；
- 1k 推理成功率 ≥ 98%；
- 每条 prediction 中包含 `prediction_raw` 和清洗后的 `prediction`；
- 输出没有被重复写入或丢样本；
- 能断点续跑。

---

# Phase 4：VQA/OK-VQA 评测脚本

## 4.1 目标

实现统一的答案 normalization 和评测脚本，用于所有 baseline 与微调结果。

## 4.2 需要写的代码

- `scripts/normalize_answer.py`
- `scripts/evaluate_vqa.py`
- `src/fdvit/evaluation.py`

## 4.3 normalization 规则

至少实现：

- lowercase；
- 去除首尾空白；
- 去除多数标点；
- 常见数字词转数字，例如 `two` → `2`；
- 去除冠词 `a/an/the`；
- 压缩多空格；
- 可选：从完整句子中抽取短答案，例如 `the answer is tennis` → `tennis`。

注意：抽取短答案必须保守，不能把明显多词答案错误截断。

## 4.4 指标定义

默认同时报告三种指标：

| 指标 | 含义 | 用途 |
|---|---|---|
| `acc_any` | 预测答案匹配任一 ground-truth answer | 直观主指标之一 |
| `acc_soft` | 类 VQA soft accuracy，按匹配次数折算 | 与 VQA 风格更接近 |
| `format_error_rate` | 输出过长、带解释、空输出等格式问题比例 | 分析 prompt / 微调效果 |

推荐公式：

```python
acc_any = int(normalized_prediction in normalized_answers)
acc_soft = min(match_count / 3.0, 1.0)
```

对于 OK-VQA 如果每题只有 5 个答案，仍可报告 `acc_soft`，但必须在报告中说明实现方式。

## 4.5 推荐命令

```bash
python scripts/evaluate_vqa.py \
  --predictions outputs/zero_shot_val_1k/predictions.jsonl \
  --output outputs/zero_shot_val_1k/metrics.json \
  --error_output outputs/zero_shot_val_1k/errors.jsonl
```

## 4.6 输出文件

`metrics.json`：

```json
{
  "num_samples": 1000,
  "num_valid_predictions": 998,
  "acc_any": 0.321,
  "acc_soft": 0.287,
  "format_error_rate": 0.094,
  "empty_prediction_rate": 0.002,
  "avg_prediction_length_tokens": 2.4,
  "template_id": "okvqa_short_001",
  "model_id": "Qwen3-VL-4B-Instruct"
}
```

`errors.jsonl`：只保存错误样本，用于后续 failure mining。

## 4.7 验收标准

- 输入 predictions 行数与 metrics 中 `num_samples` 一致；
- 对手写 20 条测试样例，normalization 结果符合预期；
- `acc_any`、`acc_soft`、`format_error_rate` 都能输出；
- 错误样本文件可被 `mine_failures.py` 读取。

---

# Phase 5：prompt-only baseline

## 5.1 目标

证明后续提升不是单纯来自 prompt 改写，同时找到较稳的推理模板。

## 5.2 需要跑的实验

至少两组：

| Exp ID | 配置 | 数据 | 输出目录 |
|---|---|---|---|
| E00 | zero-shot basic prompt | val_1k | `outputs/E00_zero_shot_basic/` |
| E01 | prompt-only strict short answer | val_1k | `outputs/E01_prompt_strict/` |

## 5.3 推荐命令

```bash
python scripts/run_inference.py \
  --config configs/infer_prompt_only.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --output outputs/E01_prompt_strict/predictions.jsonl \
  --template_id okvqa_short_002 \
  --seed 42

python scripts/evaluate_vqa.py \
  --predictions outputs/E01_prompt_strict/predictions.jsonl \
  --output outputs/E01_prompt_strict/metrics.json \
  --error_output outputs/E01_prompt_strict/errors.jsonl
```

## 5.4 指标

- `acc_any`；
- `acc_soft`；
- `format_error_rate`；
- 平均输出长度；
- 与 E00 的差值。

## 5.5 验收标准

- E00 和 E01 使用同一模型、同一数据、同一评测；
- 只改变 prompt，不改变模型；
- 结果进入 `results_main.csv`；
- 选出一个后续统一使用的推理模板。

---

# Phase 6：Failure mining 与错误类型分析

## 6.1 目标

从 baseline 错误中挖掘失败样本，按错误类型统计，为 failure-driven 训练集构造提供依据。

## 6.2 需要写的代码

- `scripts/mine_failures.py`
- `scripts/build_error_annotation_sheet.py`，可选；
- `src/fdvit/failure_mining.py`
- `scripts/summarize_error_types.py`

## 6.3 错误类型

默认类型：

| error_type | 含义 |
|---|---|
| answer_format | 输出太长、带解释、空输出、格式不适合 VQA |
| counting | 数量判断错误 |
| ocr_text | 图中文字、数字、招牌、菜单、屏幕文本相关错误 |
| spatial | 左右、前后、遮挡、相对位置错误 |
| attribute | 颜色、材质、类别、状态等属性错误 |
| commonsense | 需要常识或外部知识的问题答错 |
| hallucination | 编造图中不存在的物体/关系 |
| ambiguous | 问题或标注本身有歧义 |
| other | 无法归类 |

详细定义见 `ERROR_TAXONOMY.md`。

## 6.4 自动标注与人工复核

coding agent 可以先做启发式弱标注：

- 问题以 `how many` 开头 → counting；
- 问题含 `read`, `sign`, `text`, `number`, `word` → ocr_text；
- 问题含 `left`, `right`, `behind`, `front`, `next to` → spatial；
- 输出长度超过阈值或含 `because`, `I think`, `the answer is` → answer_format；
- 其余由人工复核。

最终错误分析表应明确说明哪些是自动弱标注，哪些经过人工复核。

## 6.5 推荐命令

```bash
python scripts/mine_failures.py \
  --predictions outputs/E01_prompt_strict/predictions.jsonl \
  --metrics outputs/E01_prompt_strict/metrics.json \
  --output outputs/E01_prompt_strict/failures_mined.jsonl \
  --summary outputs/E01_prompt_strict/error_summary.csv
```

## 6.6 指标

- 错误样本总数；
- 每类错误数量；
- 每类错误占全部错误比例；
- format error rate；
- top-k 高频问题模式；
- 可用于训练的 hard samples 数量。

## 6.7 验收标准

- `failures_mined.jsonl` 每行包含 `error_type_auto`；
- 至少 100 条错误样本被抽样预览；
- 形成 `error_summary.csv`；
- 明确 failure-driven subset 只从 train 或允许使用的开发集构造，不使用最终测试集。

---

# Phase 7：构造 random 与 failure-driven 训练集

## 7.1 目标

构造同规模、同格式的 LoRA 训练数据：random subset 和 failure-driven subset。

## 7.2 需要写的代码

- `scripts/build_training_subset.py`
- `scripts/convert_to_qwen_format.py` 补充 sampling 支持；
- `scripts/validate_train_subset.py`

## 7.3 训练集设计

默认训练集：

| 文件 | 样本数 | 来源 | 用途 |
|---|---:|---|---|
| `train_random_2k.jsonl` | 2,000 | train 随机采样 | LoRA-random |
| `train_failure_2k.jsonl` | 2,000 | train 中 baseline 错误/高风险样本优先 | LoRA-failure |
| `train_random_5k.jsonl` | 5,000 | 可选 | 扩展实验 |
| `train_failure_5k.jsonl` | 5,000 | 可选 | 扩展实验 |

如果无法在 train split 上跑 baseline，可采用 train 子集作为 probing set。不能从最终 test split 采样。

## 7.4 failure-driven 采样策略

推荐策略：

1. 从 baseline train-probing 错误样本中选 hard set；
2. 按错误类型设置采样权重；
3. 优先覆盖高频错误类型，但避免全是同一类；
4. 对 answer_format 错误不要采太多，避免训练集过窄；
5. 若 hard set 不足，用 random train 样本补齐；
6. 保持 random 和 failure-driven 样本数完全一致；
7. 使用相同 prompt 模板策略转换成 Qwen 格式。

默认权重建议：

| error_type | weight |
|---|---:|
| commonsense | 1.4 |
| counting | 1.2 |
| spatial | 1.2 |
| ocr_text | 1.1 |
| attribute | 1.0 |
| answer_format | 0.7 |
| hallucination | 1.0 |
| other | 0.8 |

## 7.5 推荐命令

```bash
python scripts/build_training_subset.py \
  --train data/processed/okvqa/train.jsonl \
  --failures outputs/train_probe/failures_mined.jsonl \
  --strategy random \
  --n 2000 \
  --seed 42 \
  --output data/processed/okvqa/train_random_2k.jsonl

python scripts/build_training_subset.py \
  --train data/processed/okvqa/train.jsonl \
  --failures outputs/train_probe/failures_mined.jsonl \
  --strategy failure_driven \
  --n 2000 \
  --seed 42 \
  --output data/processed/okvqa/train_failure_2k.jsonl

python scripts/convert_to_qwen_format.py \
  --input data/processed/okvqa/train_failure_2k.jsonl \
  --output data/processed/okvqa/train_failure_2k_qwen.json \
  --template_file prompts/okvqa_templates.json \
  --template_mode multi \
  --seed 42
```

## 7.6 指标

- 两个训练集样本数完全一致；
- 两个训练集 answer 分布；
- failure-driven 中各 error type 分布；
- 图片路径有效率；
- 重复样本比例；
- 与 val/test 的 question_id 重叠数。

## 7.7 验收标准

- random 与 failure-driven 训练集规模一致；
- 不含最终测试集样本；
- Qwen 格式通过 `validate_data.py`；
- 训练样本 prompt 包含 short-answer 约束；
- 输出 `subset_stats.json`。

---

# Phase 8：LoRA / QLoRA 训练

## 8.1 目标

在相同模型、相同训练规模、相同训练超参数下分别训练 LoRA-random 和 LoRA-failure-driven。

## 8.2 需要写的代码/文件

- `configs/lora_random_2k.yaml`
- `configs/lora_failure_2k.yaml`
- `scripts/train_lora.sh`
- `scripts/collect_train_log.py`
- 可选：`scripts/merge_lora.py`

## 8.3 训练配置默认值

| 参数 | 默认值 |
|---|---|
| base_model | Qwen3-VL-4B-Instruct |
| train_method | LoRA |
| lora_rank | 8 |
| lora_alpha | 16 |
| lora_dropout | 0.05 |
| learning_rate | 1e-4 或 2e-4，按稳定性调整 |
| epochs | 1–3 |
| batch_size | 根据显存决定 |
| grad_accum | 根据显存决定 |
| max_seq_len | 视框架默认和显存控制 |
| max_pixels | 低显存时降低 |
| seed | 42 |

## 8.4 训练公平性规则

LoRA-random 与 LoRA-failure-driven 必须保持：

- 相同 base model；
- 相同训练样本数；
- 相同 LoRA rank；
- 相同 learning rate；
- 相同 epochs；
- 相同 batch size / grad accumulation；
- 相同 prompt 模板策略；
- 相同评测数据与评测脚本。

只有采样策略不同。

## 8.5 推荐命令

```bash
bash scripts/train_lora.sh configs/lora_random_2k.yaml
bash scripts/train_lora.sh configs/lora_failure_2k.yaml
```

如果显存不足：

```bash
bash scripts/train_lora.sh configs/lora_failure_2k_qlora.yaml
```

## 8.6 训练日志要求

每个 checkpoint 目录必须包含：

```text
checkpoints/lora_failure_2k/
├── adapter_config.json
├── adapter_model.safetensors
├── trainer_state.json
├── train.log
├── train_config.yaml
├── command.txt
└── environment.txt
```

## 8.7 指标

训练阶段不以 loss 作为最终结论，但必须记录：

- train loss 曲线；
- 是否出现 NaN；
- peak GPU memory；
- 训练时长；
- checkpoint 大小；
- 实际训练样本数。

## 8.8 验收标准

- random 与 failure 两个 LoRA checkpoint 均能加载；
- 训练日志无 NaN；
- checkpoint 文件完整；
- 训练配置已保存；
- 不因 failure-driven 数据导致训练脚本特殊分支。

---

# Phase 9：微调后评测与主结果表

## 9.1 目标

使用同一推理与评测脚本，对 LoRA-random 和 LoRA-failure-driven 进行评测，形成主结果表。

## 9.2 需要跑的实验

| Exp ID | Setting | 必须 | 输出目录 |
|---|---|---:|---|
| E00 | Zero-shot basic | 是 | `outputs/E00_zero_shot_basic/` |
| E01 | Prompt-only strict | 是 | `outputs/E01_prompt_strict/` |
| E02 | LoRA-random-2k | 是 | `outputs/E02_lora_random_2k/` |
| E03 | LoRA-failure-2k | 是 | `outputs/E03_lora_failure_2k/` |
| E04 | LoRA-random-5k | 可选 | `outputs/E04_lora_random_5k/` |
| E05 | LoRA-failure-5k | 可选 | `outputs/E05_lora_failure_5k/` |

## 9.3 推荐命令

```bash
python scripts/run_inference.py \
  --config configs/infer_lora_random_2k.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --lora_checkpoint checkpoints/lora_random_2k \
  --output outputs/E02_lora_random_2k/predictions.jsonl \
  --seed 42

python scripts/evaluate_vqa.py \
  --predictions outputs/E02_lora_random_2k/predictions.jsonl \
  --output outputs/E02_lora_random_2k/metrics.json \
  --error_output outputs/E02_lora_random_2k/errors.jsonl

python scripts/run_inference.py \
  --config configs/infer_lora_failure_2k.yaml \
  --input data/processed/okvqa/val_1k.jsonl \
  --lora_checkpoint checkpoints/lora_failure_2k \
  --output outputs/E03_lora_failure_2k/predictions.jsonl \
  --seed 42

python scripts/evaluate_vqa.py \
  --predictions outputs/E03_lora_failure_2k/predictions.jsonl \
  --output outputs/E03_lora_failure_2k/metrics.json \
  --error_output outputs/E03_lora_failure_2k/errors.jsonl
```

汇总：

```bash
python scripts/summarize_results.py \
  --outputs outputs \
  --output_csv outputs/results_main.csv \
  --output_md outputs/results_main.md
```

## 9.4 主结果表模板

| Setting | Train n | Sampling | LoRA r | Prompt | acc_any | acc_soft | format_error_rate | Δ vs zero-shot | Δ vs random |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|
| Zero-shot | 0 | - | - | basic | - | - | - | - | - |
| Prompt-only | 0 | - | - | strict | - | - | - | - | - |
| LoRA-random | 2k | random | 8 | strict | - | - | - | - | - |
| LoRA-failure | 2k | failure | 8 | strict | - | - | - | - | - |

## 9.5 验收标准

- 所有 setting 使用同一 val set；
- 所有 setting 使用同一 evaluation 脚本；
- `results_main.csv` 可由脚本自动生成；
- 每个 setting 保留逐样本 predictions；
- 失败样本可追溯到原图、问题、ground truth 和模型输出。

---

# Phase 10：消融实验

## 10.1 目标

在主线完成后，做少量高价值消融，验证方法而不是堆实验。

## 10.2 推荐优先级

| 优先级 | 消融 | 是否推荐 | 目的 |
|---:|---|---|---|
| 1 | random vs failure-driven | 必须 | 核心创新变量 |
| 2 | zero-shot vs prompt-only | 必须 | 排除 prompt 影响 |
| 3 | 单模板 vs 多模板 | 推荐 | 证明模板鲁棒性 |
| 4 | 2k vs 5k | 可选 | 数据规模影响 |
| 5 | LoRA r=8 vs r=16 | 可选 | PEFT 超参影响 |
| 6 | GUI grounding | bonus | 呼应 visual agent |
| 7 | Janus-Pro | 不推荐 | 工程成本高，主线不需要 |

## 10.3 消融表模板

### 模板消融

| Setting | Template mode | acc_any | acc_soft | format_error_rate |
|---|---|---:|---:|---:|
| LoRA-random-2k | single | - | - | - |
| LoRA-random-2k | multi | - | - | - |
| LoRA-failure-2k | single | - | - | - |
| LoRA-failure-2k | multi | - | - | - |

### 数据规模消融

| Setting | Train n | acc_any | acc_soft | Δ vs 2k |
|---|---:|---:|---:|---:|
| LoRA-random | 2k | - | - | - |
| LoRA-random | 5k | - | - | - |
| LoRA-failure | 2k | - | - | - |
| LoRA-failure | 5k | - | - | - |

## 10.4 验收标准

- 消融只在主线跑通后进行；
- 每个消融一次只改变一个变量；
- 不允许把不同 val set 上的结果放进同一表直接比较；
- 如果时间不足，只保留 random vs failure-driven 主对比。

---

# Phase 11：错误类型对比与 qualitative analysis

## 11.1 目标

解释模型提升来自哪里，哪些错误改善，哪些没有改善。

## 11.2 需要写的代码

- `scripts/compare_errors.py`
- `scripts/make_case_study_table.py`
- `scripts/export_case_images.py`，可选；
- `notebooks/error_analysis.ipynb`，可选。

## 11.3 错误类型对比表

| error_type | Zero-shot errors | Prompt-only errors | LoRA-random errors | LoRA-failure errors | Improvement vs random |
|---|---:|---:|---:|---:|---:|
| answer_format | - | - | - | - | - |
| counting | - | - | - | - | - |
| ocr_text | - | - | - | - | - |
| spatial | - | - | - | - | - |
| attribute | - | - | - | - | - |
| commonsense | - | - | - | - | - |
| hallucination | - | - | - | - | - |
| ambiguous | - | - | - | - | - |

## 11.4 qualitative cases 要求

至少 6–10 个例子：

- 微调前错，failure-driven 后对；
- random LoRA 仍错，failure-driven 对；
- failure-driven 仍错，用于说明局限；
- format error 被 prompt / 微调修复的例子；
- counting / spatial / commonsense 各至少一个。

case 表格式：

| Case | Image | Question | GT | Zero-shot | Random LoRA | Failure LoRA | Error Type | Note |
|---|---|---|---|---|---|---|---|---|
| 1 | path | ... | ... | ... | ... | ... | commonsense | ... |

## 11.5 推荐命令

```bash
python scripts/compare_errors.py \
  --exp_dirs outputs/E00_zero_shot_basic outputs/E01_prompt_strict outputs/E02_lora_random_2k outputs/E03_lora_failure_2k \
  --output_csv outputs/error_comparison.csv \
  --output_md outputs/error_comparison.md

python scripts/make_case_study_table.py \
  --exp_dirs outputs/E00_zero_shot_basic outputs/E02_lora_random_2k outputs/E03_lora_failure_2k \
  --output outputs/case_studies.md \
  --num_cases 10 \
  --seed 42
```

## 11.6 验收标准

- 生成错误类型对比表；
- 生成至少 6 个可读 case；
- case 中包含原问题、GT、各模型预测；
- 不只展示成功案例，也展示失败案例；
- 报告中不夸大结论。

---

# Phase 12：可选 GUI grounding bonus

## 12.1 目标

在主线完成后，用小规模 GUI grounding 展示 visual agent 相关潜力。该部分只能作为 bonus，不得影响主线完成。

## 12.2 任务定义

输入：GUI 截图 + 自然语言指令。  
输出：目标控件坐标点或 bounding box。

示例：

```text
<image>
Instruction: Click the button to submit the form.
Answer with the target coordinate as (x, y).
```

## 12.3 需要写的代码

- `scripts/prepare_gui_grounding.py`
- `scripts/run_gui_grounding.py`
- `scripts/evaluate_gui_grounding.py`
- `configs/gui_grounding.yaml`
- `prompts/gui_grounding_templates.json`

## 12.3.1 从 0 运行流程

GUI grounding 默认使用 ScreenSpot-Pro 小样本，不下载全量数据。推荐从 `vscode_macos` 取 20 条作为 demo：

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

然后校验数据：

```bash
python scripts/validate_data.py \
  --input data/processed/gui/val_small.jsonl \
  --check_images \
  --expect_split val \
  --output logs/validate_gui_val_small.json \
  --overwrite
```

推理前先做 dry run，确认输入、配置和模板可解析：

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --limit 2 \
  --dry_run
```

在 CUDA/Linux 环境中运行真实推理：

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --overwrite
```

最后评测：

```bash
python scripts/evaluate_gui_grounding.py \
  --predictions outputs/B01_gui_grounding_demo/predictions.jsonl \
  --output outputs/B01_gui_grounding_demo/metrics.json \
  --error_output outputs/B01_gui_grounding_demo/errors.jsonl \
  --overwrite
```

推荐输出目录：

```text
outputs/B01_gui_grounding_demo/
├── predictions.jsonl
├── metrics.json
├── errors.jsonl
├── run_config.yaml
├── command.txt
└── environment.txt
```

## 12.4 指标

| 指标 | 含义 |
|---|---|
| point_in_bbox_acc | 预测点是否落在 GT bbox 内 |
| center_distance_norm | 预测点到目标中心点的归一化距离 |
| parse_success_rate | 模型输出是否能解析出坐标 |
| control_type_metrics | 按按钮、菜单、输入框等类型统计准确率和距离 |

## 12.5 验收标准

- 只做小样本；
- 不训练完整 agent；
- 不引入复杂交互环境；
- 坐标归一化规则写清楚；
- 逐样本保存 `predictions.jsonl`；
- `metrics.json` 至少包含 `point_in_bbox_acc`、`parse_success_rate`、`center_distance_norm`；
- 作为附录展示，不放在主结果表核心位置。

---

## 5. 实验命名规范

推荐命名：

```text
E00_zero_shot_basic
E01_prompt_strict
E02_lora_random_2k_r8
E03_lora_failure_2k_r8
E04_lora_random_5k_r8_optional
E05_lora_failure_5k_r8_optional
E06_template_single_optional
E07_template_multi_optional
B01_gui_grounding_demo
```

每个 experiment 必须有：

- config；
- command；
- predictions；
- metrics；
- errors；
- summary。

---

## 6. coding agent 工作方式

### 6.1 每次任务开始前

coding agent 必须先确认：

1. 本任务属于哪个 Phase；
2. 本任务输入文件在哪里；
3. 本任务输出文件是什么；
4. 本任务是否会改变既有格式契约；
5. 本任务是否可能污染评测集；
6. 本任务完成后用什么命令自测。

### 6.2 每次任务完成后

coding agent 必须输出：

- 改动文件列表；
- 运行过的命令；
- 生成的文件；
- 自测结果；
- 仍未解决的问题；
- 下一步建议。

### 6.3 禁止行为

coding agent 不得：

- 捏造实验结果；
- 只写伪代码不落地；
- 更改数据格式但不更新 `DATA_AND_FORMAT_CONTRACT.md`；
- 更改实验矩阵但不更新 `EXPERIMENT_PROTOCOL.md`；
- 把最终 val/test 样本加入训练集；
- 用不同评测脚本比较不同实验；
- 覆盖已有结果而不备份；
- 让脚本依赖本机绝对路径；
- 把 token、私有路径、缓存目录硬编码进 repo。

---

## 7. 最小可交付版本 Definition of Done

如果时间或算力不够，项目至少完成以下内容即可交付：

- OK-VQA 子集数据转换；
- Qwen3-VL zero-shot baseline；
- prompt-only baseline；
- LoRA-random 1k/2k；
- LoRA-failure-driven 1k/2k；
- 统一评测脚本；
- 主结果表；
- 错误类型表；
- 6 个 case study；
- 报告中清楚说明方法、数据、指标、局限。

最小主结果表：

| Setting | Train n | Sampling | acc_any | acc_soft | format_error_rate |
|---|---:|---|---:|---:|---:|
| Zero-shot | 0 | - | - | - | - |
| Prompt-only | 0 | - | - | - | - |
| LoRA-random | 2k | random | - | - | - |
| LoRA-failure | 2k | failure-driven | - | - | - |

---

## 8. 标准版 Definition of Done

标准版应完成：

- val_1k 与 val_full 或 val_5k 两档评测；
- random vs failure-driven 2k 主对比；
- 5k 扩展对比，若算力允许；
- 单模板 vs 多模板，若时间允许；
- 错误类型对比；
- qualitative cases；
- 完整报告和展示材料。

标准版报告至少包含三张表：

1. 主结果表；
2. 消融表；
3. 错误类型表。

---

## 9. 风险与降级策略

| 风险 | 表现 | 降级策略 |
|---|---|---|
| 显存不足 | 4B 无法训练 | 换 2B、QLoRA、降低 batch、降低图片分辨率 |
| 推理太慢 | 1k 都很慢 | 先跑 200/500 样本，报告中说明 subset |
| LoRA 训练失败 | loss NaN 或 OOM | 降学习率、减 batch、检查数据格式、转 QLoRA |
| 指标提升不明显 | failure-driven 不如 random | 强化错误分析，说明哪些类型改善，检查采样是否过窄 |
| 输出格式差 | 很多完整句子 | 更严格 prompt，训练答案统一 short answer |
| 数据污染 | train 与 val/test 重叠 | 写 split 检查脚本，按 question_id/image_id 检查重叠 |
| 实验矩阵膨胀 | 做不完 | 只保留 E00–E03 |

---

## 10. 最终汇总命令

当所有主线实验完成后，运行：

```bash
python scripts/summarize_results.py \
  --outputs outputs \
  --output_csv outputs/results_main.csv \
  --output_md outputs/results_main.md

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

报告撰写时只引用这些自动生成文件中的数字。

---

## 11. 项目一句话总结

本项目不是泛泛地“微调一个多模态大模型”，而是验证一个清楚的问题：

> 对视觉问答/视觉推理任务，少量 failure-driven 视觉指令数据是否比同规模 random 数据更有效？

所有 coding、实验和报告都应围绕这个问题展开。
