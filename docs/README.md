# FD-VIT 项目 docs 目录说明

> Version: 2026-06-06-regenerated  
> Purpose: 这个目录同时服务于课程要求溯源、项目范围控制、coding agent 执行与最终报告准备。

本目录用于指导 coding agent 与团队成员完成 NLP 课程大作业：**FD-VIT: Failure-Driven Visual Instruction Tuning for Multimodal Visual Reasoning**。

项目主线已经收敛为：

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

Coding agent 不应只根据课程原始要求自行扩展实验范围。实际编码、实验和报告应以本目录中的执行文档为准。

## 1. 文档分层

本目录分为三类文档。

### 1.1 课程要求溯源文档

这些文档回答：**课程原始 Word 文档要求了什么？我们是否覆盖了这些要求？**

- [`project_requirements.md`](./project_requirements.md)：原始 Word 要求的 Markdown 转写。保留课程给出的模型、任务、数据集、微调方式、指令模板和 bonus 方向。图片只做文字说明。
- [`REQUIREMENTS_TRACEABILITY.md`](./REQUIREMENTS_TRACEABILITY.md)：课程要求到 FD-VIT 实施方案的覆盖表。说明哪些要求被主线覆盖，哪些被降级为 optional，哪些被明确排除。

### 1.2 项目执行文档

这些文档回答：**coding agent 具体应该写什么代码、跑什么实验、保存什么结果？**

- [`FD_VIT_CODING_AGENT_GUIDE.md`](./FD_VIT_CODING_AGENT_GUIDE.md)：主控文档。定义阶段划分、代码任务、实验任务、指标、验收标准和风险边界。
- [`DATA_AND_FORMAT_CONTRACT.md`](./DATA_AND_FORMAT_CONTRACT.md)：数据格式契约。规定 raw / processed / Qwen conversation / prediction / metrics / failure files 的字段与格式。
- [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md)：实验协议。规定 E00–E03 主线实验、可选扩展、指标、命名、随机种子和防泄漏规则。
- [`ERROR_TAXONOMY.md`](./ERROR_TAXONOMY.md)：错误分类标准。用于 failure-driven sampling、人工/半自动错误标注和 qualitative analysis。
- [`CODING_AGENT_TASK_CARDS.md`](./CODING_AGENT_TASK_CARDS.md)：可直接派发给 coding agent 的任务卡。每张卡包含目标、输入、输出、脚本、验收标准和自测命令。
- [`REPORT_CHECKLIST.md`](./REPORT_CHECKLIST.md)：最终报告、展示和答辩 checklist。

### 1.3 合并阅读文档

- [`FD_VIT_DOCS_ALL_IN_ONE.md`](./FD_VIT_DOCS_ALL_IN_ONE.md)：把主要文档合并成一个文件，方便一次性喂给 coding agent。编辑时仍应修改独立文件，合并文件只作为阅读副本。

## 2. 建议阅读顺序

### A. 先确认课程要求与项目边界

1. 阅读 [`project_requirements.md`](./project_requirements.md)。  
   目的：了解课程原始要求，包括 QwenVL / Qwen3-VL、Janus-Pro、Image Caption、VQA、Image Generation、Visual Agent、COCO、Flickr30K、VQA、RICO、SeeClick、LoRA、projector-only 等范围。

2. 阅读 [`REQUIREMENTS_TRACEABILITY.md`](./REQUIREMENTS_TRACEABILITY.md)。  
   目的：理解为什么本项目最终采用 FD-VIT 主线，以及为什么 Janus-Pro、image generation、完整 GUI Agent 不作为必做主线。

### B. 再进入 coding agent 执行文档

3. 阅读 [`FD_VIT_CODING_AGENT_GUIDE.md`](./FD_VIT_CODING_AGENT_GUIDE.md)。  
   目的：掌握分阶段工作流，从环境检查、数据转换、推理评测、failure mining、LoRA 训练到报告产出。

4. 阅读 [`DATA_AND_FORMAT_CONTRACT.md`](./DATA_AND_FORMAT_CONTRACT.md)。  
   目的：确保所有代码遵守统一数据 schema，避免团队协作时格式不兼容。

5. 阅读 [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md)。  
   目的：确认必须完成的 E00–E03 实验、指标和结果保存方式。

6. 阅读 [`ERROR_TAXONOMY.md`](./ERROR_TAXONOMY.md)。  
   目的：统一 failure-driven sampling 与错误案例分析中的错误类型。

7. 按需阅读 [`CODING_AGENT_TASK_CARDS.md`](./CODING_AGENT_TASK_CARDS.md)。  
   目的：把任务拆成可派发给 coding agent 的工作单元。

8. 最后阅读 [`REPORT_CHECKLIST.md`](./REPORT_CHECKLIST.md)。  
   目的：确认实验产物能够转化为课程报告和展示材料。

## 3. 课程要求与执行方案的关系

`project_requirements.md` 是**需求来源**，不是**执行方案**。它保留了课程允许探索的完整范围，包括多种模型、多种数据集、多种任务和 bonus 方向。

`REQUIREMENTS_TRACEABILITY.md` 是**范围收敛说明**。它解释 FD-VIT 如何覆盖课程要求，并明确以下取舍：

- Qwen3-VL-4B-Instruct 是主模型。
- OK-VQA / VQA 是主任务。
- LoRA / QLoRA / projector-only 是主要微调方式。
- zero-shot、prompt-only、LoRA-random、LoRA-failure-driven 是必做对照。
- Janus-Pro、image generation、完整 GUI Agent 不进入主线。
- GUI grounding 只作为可选 bonus。

`FD_VIT_CODING_AGENT_GUIDE.md` 是**coding agent 的执行入口**。除非团队明确更新实验协议，否则 coding agent 不应根据 `project_requirements.md` 擅自增加新模型、新任务或新实验矩阵。

## 4. 对 coding agent 的硬约束

- 不要擅自扩大实验矩阵。
- 不要把 Janus-Pro、图像生成、完整 GUI Agent 当作主线。
- 不要污染最终测试集；failure-driven 采样只能使用训练集或明确允许的开发集。
- 不要用简单字符串匹配替代规范化后的 VQA / OK-VQA 评测。
- 不要只保存 aggregate metrics；必须保存逐样本 prediction。
- 不要在没有 zero-shot baseline 和 prompt-only baseline 的情况下开始写结论。
- 所有脚本必须提供 CLI、日志、输入路径、输出路径和随机种子参数。
- 新增实验必须先更新 `EXPERIMENT_PROTOCOL.md`。
- 新增数据格式必须先更新 `DATA_AND_FORMAT_CONTRACT.md`。
- 新增课程覆盖解释必须先更新 `REQUIREMENTS_TRACEABILITY.md`。

## 5. 推荐项目目录结构

```text
FD-VIT/
├── docs/
│   ├── README.md
│   ├── project_requirements.md
│   ├── REQUIREMENTS_TRACEABILITY.md
│   ├── FD_VIT_CODING_AGENT_GUIDE.md
│   ├── DATA_AND_FORMAT_CONTRACT.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── ERROR_TAXONOMY.md
│   ├── CODING_AGENT_TASK_CARDS.md
│   ├── REPORT_CHECKLIST.md
│   └── FD_VIT_DOCS_ALL_IN_ONE.md
├── configs/
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── prompts/
├── scripts/
├── outputs/
├── runs/
└── reports/
```

## 6. 最小必做实验

| ID | Setting | 目的 |
|---|---|---|
| E00 | Qwen3-VL zero-shot | 原模型能力基线 |
| E01 | Qwen3-VL prompt-only | 排除仅靠提示词改进的影响 |
| E02 | LoRA-random | 普通指令微调 baseline |
| E03 | LoRA-failure-driven | FD-VIT 核心方法 |

主结果表至少需要包含：accuracy、相对 zero-shot 提升、输出格式错误率、样本数、prompt/template 设置、LoRA 配置。

## 7. 文档维护规则

- 修改课程要求理解：更新 `project_requirements.md` 或在其中注明差异来源。
- 修改范围取舍：更新 `REQUIREMENTS_TRACEABILITY.md`。
- 修改数据 schema：更新 `DATA_AND_FORMAT_CONTRACT.md`。
- 修改实验编号、指标或对照组：更新 `EXPERIMENT_PROTOCOL.md`。
- 修改 coding agent 工作流：更新 `FD_VIT_CODING_AGENT_GUIDE.md` 和 `CODING_AGENT_TASK_CARDS.md`。
- 修改报告结构：更新 `REPORT_CHECKLIST.md`。
- 修改任何独立文档后，如需要一次性给 agent 阅读，再重新生成 `FD_VIT_DOCS_ALL_IN_ONE.md`。

## 8. GUI Grounding Bonus 从 0 流程

GUI grounding 只作为 `B01_gui_grounding_demo` bonus，不进入 E00-E03 主结果表，也不能替代 OK-VQA/VQA 主线。

### 8.1 前置条件

先完成基础环境和模型准备：

```bash
python scripts/check_env.py --output logs/env_check.json --overwrite

python scripts/prepare_model.py \
  --download \
  --output logs/model_prepare.json \
  --overwrite
```

CUDA/Linux 环境中应确认：

- `logs/env_check.json` 中 CUDA 可用；
- `transformers >= 4.57.0`；
- `qwen-vl-utils`、`peft`、`Pillow` 可用；
- `logs/model_prepare.json` 中 `ready_for_baseline: true`。

### 8.2 下载和转换 ScreenSpot-Pro 小样本

默认数据源为 Hugging Face dataset `likaixin/ScreenSpot-Pro`。为控制 bonus 规模，默认只取 `vscode_macos` 的小样本：

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

生成文件：

- `data/raw/gui/screenspot_pro/annotations/vscode_macos.json`
- `data/raw/gui/screenspot_pro/images/...`
- `data/processed/gui/val_small.jsonl`
- `data/processed/gui/val_small.summary.json`
- `data/samples/gui_grounding_5.jsonl`

如果服务器已经缓存数据，可加 `--local_files_only`，但必须保证 annotation 和图片已在 `data/raw/gui/screenspot_pro/` 下。

### 8.3 校验 GUI 数据

```bash
python scripts/validate_data.py \
  --input data/processed/gui/val_small.jsonl \
  --check_images \
  --expect_split val \
  --output logs/validate_gui_val_small.json \
  --overwrite
```

通过条件：

- JSONL 可解析；
- 每条样本有 `sample_id`、`instruction`、`bbox`、`point`、`image_size`、`control_type`；
- `bbox`、`point`、`image_size` 数值合法；
- 图片路径存在。

### 8.4 运行 GUI Grounding 推理

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --overwrite
```

可先做 2 条 dry run，不加载模型：

```bash
python scripts/run_gui_grounding.py \
  --config configs/gui_grounding.yaml \
  --input data/processed/gui/val_small.jsonl \
  --output outputs/B01_gui_grounding_demo/predictions.jsonl \
  --limit 2 \
  --dry_run
```

推理输出必须保留逐样本 `predictions.jsonl`。即使某条推理失败，也应写入该样本并记录 `error`。

### 8.5 评测 B01

```bash
python scripts/evaluate_gui_grounding.py \
  --predictions outputs/B01_gui_grounding_demo/predictions.jsonl \
  --output outputs/B01_gui_grounding_demo/metrics.json \
  --error_output outputs/B01_gui_grounding_demo/errors.jsonl \
  --overwrite
```

主要指标：

- `point_in_bbox_acc`：预测点是否落入 GT bbox；
- `parse_success_rate`：模型输出是否能解析为坐标；
- `center_distance_norm`：预测点到 bbox 中心的归一化距离；
- `control_type_metrics`：按控件类型分组的附加分析。

### 8.6 报告使用方式

报告中只把 B01 放在 bonus/appendix：

- 不放入 E00-E03 主结果表；
- 不声称模型具备完整 GUI Agent 能力；
- 不做多步环境交互结论；
- 只说明这是静态截图上的 click-point grounding 小样本评测。
