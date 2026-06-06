# FD-VIT 数据与格式契约

本文档定义项目中所有数据文件、预测文件、评测文件和 failure mining 文件的格式。coding agent 写任何脚本前必须遵守此契约；若确需变更，必须同步更新本文档和相关 validator。

---

## 1. 数据目录约定

```text
data/
├── raw/             # 原始数据，不手动修改，不纳入 git
├── interim/         # 临时中间结果，可重建
├── processed/       # 模型训练/评测直接读取的数据
├── samples/         # 小样本 smoke test 数据
└── README.md
```

规则：

- `data/raw/` 中只放原始下载数据；
- `data/processed/` 中只放脚本生成的规范数据；
- `data/samples/` 必须有 10 条以内小样本，供 CI / smoke test 使用；
- 禁止脚本依赖本机绝对路径；
- 所有路径建议使用相对 repo root 的路径。

---

## 2. 统一 VQA 样本格式

项目内部使用 JSONL。每一行是一个样本。

### 2.1 必需字段

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
  "answer": "tennis"
}
```

### 2.2 字段说明

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| `sample_id` | string | 是 | 全项目唯一 ID，建议 `{dataset}_{split}_{index}` |
| `dataset` | string | 是 | `okvqa` / `vqa` / `gui` 等 |
| `split` | string | 是 | `train` / `val` / `test` / `dev` |
| `question_id` | int/string | 是 | 数据集原始 question id |
| `image_id` | int/string | 是 | 数据集原始 image id |
| `image_path` | string | 是 | 相对 repo root 的图片路径 |
| `question` | string | 是 | 原始问题文本 |
| `answers` | list[string] | 是 | 多个 ground-truth answers |
| `answer` | string | 是 | 训练时默认使用的 canonical answer |
| `metadata` | object | 否 | 额外信息，如原文件、题型、来源等 |

### 2.3 数据质量要求

- `question` 不为空；
- `answers` 至少有 1 个非空字符串；
- `answer` 必须是短答案，优先取多数答案或第一个有效答案；
- 图片路径存在率在抽样检查中 ≥ 99%；
- `sample_id` 不重复；
- train/val/test 的 `question_id` 不重叠；如数据集设计允许 image 重叠，需要在报告中说明。

---

## 3. Qwen3-VL instruction tuning 格式

用于训练的 Qwen 格式建议为 JSON list 或 JSONL，具体取决于训练框架要求。项目统一生成 `.json`，内容为 list。

### 3.1 单图 VQA 样本

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

### 3.2 训练格式硬性要求

- 每个样本必须包含 `image`；
- human prompt 必须包含 `<image>`；
- human prompt 必须包含 short-answer 约束；
- gpt answer 必须尽量短，不要写完整句子；
- 同一训练文件中不混入 val/test 样本；
- prompt 模板选择必须可复现，保存 `template_id` 或 seed。

### 3.3 可选 metadata

可以保留额外字段，便于追踪：

```json
{
  "id": "okvqa_train_000000001",
  "image": "...",
  "conversations": [...],
  "metadata": {
    "dataset": "okvqa",
    "split": "train",
    "question_id": 123,
    "template_id": "okvqa_short_003",
    "sampling_strategy": "failure_driven",
    "error_type_auto": "counting"
  }
}
```

---

## 4. Prompt 模板格式

模板文件位于 `prompts/*.json`。

```json
[
  {
    "template_id": "okvqa_short_001",
    "task": "vqa",
    "text": "<image>\nQuestion: {question}\nAnswer with a short phrase only. Do not explain."
  }
]
```

字段：

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| `template_id` | string | 是 | 模板唯一 ID |
| `task` | string | 是 | `vqa` / `caption` / `gui_grounding` |
| `text` | string | 是 | 包含 `{question}` 或 `{instruction}` |
| `note` | string | 否 | 说明模板设计目的 |

校验规则：

- VQA 模板必须包含 `{question}`；
- VQA 模板必须包含 `<image>`；
- VQA 模板必须包含短答案约束。

---

## 5. 推理预测文件格式

所有 inference 输出统一为 JSONL。

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
  "prompt": "<image>\nQuestion: What sport is this person playing?\nAnswer with a short phrase only. Do not explain.",
  "template_id": "okvqa_short_001",
  "prediction_raw": "The answer is tennis.",
  "prediction": "tennis",
  "normalized_prediction": "tennis",
  "normalized_answers": ["tennis", "tennis", "tennis", "badminton", "tennis"],
  "model_id": "Qwen3-VL-4B-Instruct",
  "checkpoint": null,
  "generation_config": {
    "max_new_tokens": 16,
    "temperature": 0.0,
    "top_p": 1.0
  },
  "runtime": {
    "latency_sec": 0.84,
    "device": "cuda:0"
  },
  "error": null
}
```

要求：

- 即使推理失败，也要写一行，并在 `error` 中记录异常；
- 不要丢样本；
- `prediction_raw` 保留模型原始输出；
- `prediction` 是清洗后的短答案；
- `normalized_prediction` 由统一 normalization 生成；
- 不同实验的 predictions 字段必须兼容。

---

## 6. 评测 metrics 格式

`metrics.json` 示例：

```json
{
  "experiment_id": "E03_lora_failure_2k_r8",
  "model_id": "Qwen3-VL-4B-Instruct",
  "checkpoint": "checkpoints/lora_failure_2k",
  "dataset": "okvqa",
  "split": "val_1k",
  "num_samples": 1000,
  "num_valid_predictions": 998,
  "acc_any": 0.341,
  "acc_soft": 0.302,
  "format_error_rate": 0.031,
  "empty_prediction_rate": 0.002,
  "avg_prediction_length_tokens": 1.8,
  "seed": 42,
  "created_at": "YYYY-MM-DD HH:MM:SS"
}
```

要求：

- 所有数值为数字类型，不要存百分号字符串；
- 保留实验 ID、模型、checkpoint、数据 split；
- 后续 `summarize_results.py` 直接读取此文件生成表格。

---

## 7. 错误样本格式

`errors.jsonl` 或 `failures_mined.jsonl`：

```json
{
  "sample_id": "okvqa_val_000000001",
  "question_id": 123,
  "image_path": "...",
  "question": "How many dogs are there?",
  "answers": ["2", "two", "2", "2", "two"],
  "prediction_raw": "There are three dogs.",
  "prediction": "3",
  "normalized_prediction": "3",
  "normalized_answers": ["2", "2", "2", "2", "2"],
  "is_correct": false,
  "error_type_auto": "counting",
  "error_type_manual": null,
  "format_flags": {
    "too_long": false,
    "has_explanation": true,
    "empty": false
  },
  "source_experiment": "E01_prompt_strict"
}
```

要求：

- 自动错误类型字段为 `error_type_auto`；
- 人工复核字段为 `error_type_manual`；
- 如果人工复核存在，分析时优先使用 `error_type_manual`；
- 保留 source experiment，便于比较。

---

## 8. 训练子集 metadata 格式

构造 random / failure-driven 子集时，建议保留 metadata：

```json
{
  "sample_id": "okvqa_train_000000001",
  "dataset": "okvqa",
  "split": "train",
  "question_id": 123,
  "image_path": "...",
  "question": "...",
  "answers": ["..."],
  "answer": "...",
  "metadata": {
    "sampling_strategy": "failure_driven",
    "sampling_seed": 42,
    "source_error_type": "counting",
    "source_probe_experiment": "train_probe_zero_shot"
  }
}
```

---

## 9. GUI grounding 可选格式

如果做 bonus，统一格式如下：

```json
{
  "sample_id": "gui_val_000001",
  "dataset": "screenspot",
  "split": "val",
  "image_path": "data/raw/gui/000001.png",
  "instruction": "Click the submit button.",
  "bbox": [100, 200, 180, 240],
  "point": [140, 220],
  "image_size": [1280, 720],
  "control_type": "button"
}
```

坐标规则：

- bbox 为 `[x1, y1, x2, y2]`；
- 坐标基于原图像素；
- 如果做归一化，必须另存 `bbox_norm`，不能覆盖原 bbox。

预测格式：

```json
{
  "sample_id": "gui_val_000001",
  "prediction_raw": "(142, 219)",
  "prediction_point": [142, 219],
  "parse_success": true,
  "point_in_bbox": true,
  "center_distance_norm": 0.012
}
```

---

## 10. Validator 必须检查的内容

`validate_data.py` 至少检查：

- JSON/JSONL 可解析；
- 必需字段存在；
- `sample_id` 唯一；
- 图片路径存在；
- question 非空；
- answers 非空；
- answer 非空；
- split 合法；
- Qwen 格式中 `<image>` 存在；
- train/val/test question_id 是否重叠；
- 训练样本中是否混入非 train split。

推荐命令：

```bash
python scripts/validate_data.py \
  --input data/processed/okvqa/train.jsonl \
  --check_images \
  --output logs/validate_train.json
```

---

## 11. 数据泄漏检查

必须实现或手工完成：

```bash
python scripts/validate_data.py \
  --train data/processed/okvqa/train_random_2k.jsonl \
  --eval data/processed/okvqa/val_1k.jsonl \
  --check_overlap question_id image_id
```

报告中至少说明：

- failure-driven 采样来源；
- 最终评测集未参与训练；
- 若 train 与 val 存在同图不同问，需要说明数据集原始划分特性。

---

## 12. 兼容性原则

- 所有脚本应读取本契约定义的字段；
- 新增字段可以，但不得删除必需字段；
- 不要在不同实验中使用不同 prediction schema；
- 任何 schema 变化都必须同步更新 validator 和本文档。
