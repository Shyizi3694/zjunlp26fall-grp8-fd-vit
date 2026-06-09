# FD-VIT 实验执行清单

本文档用于记录本项目接下来需要完成的实验内容、执行顺序、输入输出路径和验收标准。

适用范围：

- 主线实验 `E00`–`E03`
- 主结果表、错误分析表、case study 产出
- 可选扩展实验的边界说明

相关文档：

- [EXPERIMENT_PROTOCOL.md](./EXPERIMENT_PROTOCOL.md)
- [REQUIREMENTS_TRACEABILITY.md](./REQUIREMENTS_TRACEABILITY.md)
- [REPORT_CHECKLIST.md](./REPORT_CHECKLIST.md)
- [FD_VIT_CODING_AGENT_GUIDE.md](./FD_VIT_CODING_AGENT_GUIDE.md)

---

## 1. 实验目标

本项目的核心问题是：

> 在相同 base model、相同训练规模、相同 LoRA 配置、相同评测集下，failure-driven instruction tuning 是否优于 random instruction tuning？

因此主线实验只比较一个核心变量：

- `random sampling`
- `failure-driven sampling`

---

## 2. 当前已完成前提

截至当前仓库状态，以下准备工作已经完成：

- OK-VQA 原始数据与 COCO 图像已准备
- `train.jsonl` / `val.jsonl` 已生成
- `train_random_2k_qwen.json` 已生成
- `train_failure_2k_qwen.json` 已重新生成为真实 failure-driven 版本
- Qwen3-VL 推理链路已修复，支持正确的多模态 chat template
- LoRA 训练、评测、汇总、错误分析脚本已具备

当前最重要的缺口已经不是“补代码”，而是“跑完 E00–E03 并产出报告材料”。

---

## 3. 必做实验矩阵

| Exp ID | Setting | Train Data | Eval Set | 必做 |
|---|---|---|---|---|
| E00 | Zero-shot basic | - | `val_1k` | 是 |
| E01 | Prompt-only strict | - | `val_1k` | 是 |
| E02 | LoRA-random-2k | `train_random_2k_qwen.json` | `val_1k` | 是 |
| E03 | LoRA-failure-2k | `train_failure_2k_qwen.json` | `val_1k` | 是 |

说明：

- `E00`–`E03` 是最低可交付版本
- 其他实验都不能替代 `E00`–`E03`
- `E02` 与 `E03` 必须使用同一个评测集

---

## 4. 固定设置

主线实验必须保持以下设置一致：

| 项目 | 固定值 |
|---|---|
| Base model | `Qwen3-VL-4B-Instruct` |
| Train size | `2k` |
| Eval set | `val_1k` |
| LoRA rank | `8` |
| Seed | `42` |
| Prompt mode | strict short-answer |
| Evaluation script | `scripts/evaluate_vqa.py` |
| Generation | `temperature=0.0`, `max_new_tokens=16` |

如果因为显存问题切换到 `2B` 或 `QLoRA`，必须在结果说明里明确记录。

---

## 5. 执行顺序

严格按下面顺序执行：

1. 生成并固定 `val_1k`
2. 跑 `E00 zero-shot`
3. 跑 `E01 prompt-only`
4. 训练 `E02 LoRA-random-2k`
5. 训练 `E03 LoRA-failure-2k`
6. 评测 `E02`
7. 评测 `E03`
8. 汇总主结果表
9. 生成错误类型对比表
10. 生成 case study 表
11. 写报告和展示材料

---

## 6. 实验任务明细

### 6.1 准备统一评测集

目的：

- 固定 `val_1k`，保证 `E00`–`E03` 使用完全相同的评测集

输入：

- `data/processed/okvqa/val.jsonl`

输出：

- `data/processed/okvqa/val_1k.jsonl`

验收标准：

- `val_1k` 条数正确
- 后续所有实验统一使用这一个文件

### 6.2 E00: Zero-shot baseline

目的：

- 建立原始模型能力基线

输入：

- 模型：`Qwen3-VL-4B-Instruct`
- 评测集：`val_1k.jsonl`

输出目录：

- `outputs/E00_zero_shot_basic/`

必须产物：

- `predictions.jsonl`
- `metrics.json`
- `errors.jsonl`
- `run_config.yaml`
- `command.txt`
- `environment.txt`

验收标准：

- 成功完成全部样本推理
- `metrics.json` 可被后续汇总脚本读取

### 6.3 E01: Prompt-only baseline

目的：

- 验证 prompt 约束本身能带来多少提升

输入：

- 模型：`Qwen3-VL-4B-Instruct`
- 评测集：`val_1k.jsonl`
- strict short-answer prompt

输出目录：

- `outputs/E01_prompt_strict/`

必须产物：

- `predictions.jsonl`
- `metrics.json`
- `errors.jsonl`
- `failures_mined.jsonl`
- `error_summary.csv`

验收标准：

- 与 `E00` 使用相同评测集
- 可以直接用于后续错误类型对比

### 6.4 E02: LoRA-random-2k 训练

目的：

- 作为普通指令微调 baseline

输入：

- 训练数据：`data/processed/okvqa/train_random_2k_qwen.json`
- 配置：`configs/lora_random_2k.yaml`

输出目录：

- `checkpoints/lora_random_2k/`

必须产物：

- LoRA adapter checkpoint
- `train_config.yaml`
- `command.txt`
- `environment.txt`

验收标准：

- checkpoint 能被推理脚本加载
- 训练配置和 `E03` 仅在训练数据上不同

### 6.5 E03: LoRA-failure-2k 训练

目的：

- 验证 failure-driven 训练数据是否优于 random baseline

输入：

- 训练数据：`data/processed/okvqa/train_failure_2k_qwen.json`
- 配置：`configs/lora_failure_2k.yaml`

输出目录：

- `checkpoints/lora_failure_2k/`

必须产物：

- LoRA adapter checkpoint
- `train_config.yaml`
- `command.txt`
- `environment.txt`

验收标准：

- checkpoint 能被推理脚本加载
- 与 `E02` 在模型、训练规模、LoRA rank、seed 上保持一致

### 6.6 E02 评测

目的：

- 得到 random LoRA 的标准结果

输入：

- checkpoint：`checkpoints/lora_random_2k/`
- 配置：`configs/infer_lora_random_2k.yaml`
- 评测集：`val_1k.jsonl`

输出目录：

- `outputs/E02_lora_random_2k_r8/`

必须产物：

- `predictions.jsonl`
- `metrics.json`
- `errors.jsonl`

验收标准：

- `metrics.json` 可以进入主结果汇总

### 6.7 E03 评测

目的：

- 得到 failure-driven LoRA 的标准结果

输入：

- checkpoint：`checkpoints/lora_failure_2k/`
- 配置：`configs/infer_lora_failure_2k.yaml`
- 评测集：`val_1k.jsonl`

输出目录：

- `outputs/E03_lora_failure_2k_r8/`

必须产物：

- `predictions.jsonl`
- `metrics.json`
- `errors.jsonl`

验收标准：

- `metrics.json` 可以进入主结果汇总
- 能与 `E02` 直接公平对比

---

## 7. 结果分析任务

### 7.1 主结果表

脚本：

- `scripts/summarize_results.py`

输入：

- `outputs/E00_*/metrics.json`
- `outputs/E01_*/metrics.json`
- `outputs/E02_*/metrics.json`
- `outputs/E03_*/metrics.json`

输出：

- `outputs/results_main.csv`
- `outputs/results_main.md`

目标：

- 汇总 `acc_any`
- 汇总 `acc_soft`
- 汇总 `format_error_rate`
- 计算 `Δ vs E00`
- 计算 `Δ vs E02`

### 7.2 错误类型对比

脚本：

- `scripts/compare_errors.py`

输入：

- `outputs/E00_*/predictions.jsonl`
- `outputs/E01_*/predictions.jsonl`
- `outputs/E02_*/predictions.jsonl`
- `outputs/E03_*/predictions.jsonl`

输出：

- `outputs/error_comparison.csv`
- `outputs/error_comparison.md`

目标：

- 比较 `answer_format`
- 比较 `counting`
- 比较 `ocr_text`
- 比较 `spatial`
- 比较 `attribute`
- 比较 `commonsense`
- 比较 `hallucination`
- 比较 `ambiguous`
- 比较 `other`

### 7.3 Case study

脚本：

- `scripts/make_case_study_table.py`

输出：

- `outputs/case_study.csv`
- `outputs/case_study.md`

至少应包含：

- zero-shot 错，failure-driven 对
- random LoRA 错，failure-driven 对
- failure-driven 仍错
- format error 修复
- counting / spatial / commonsense 代表样例

---

## 8. 报告所需最小材料

最终至少要有：

1. `E00`–`E03` 四组标准结果
2. 主结果表
3. 错误类型对比表
4. 6 到 10 个 qualitative cases
5. 方法流程图
6. 训练配置说明
7. 模型、数据、硬件、seed、prompt 记录

---

## 9. 当前建议优先级

当前最推荐的执行优先级如下：

### P0

- 生成 `val_1k`
- 跑 `E00`
- 跑 `E01`
- 跑 `E02`
- 跑 `E03`
- 评测 `E02/E03`

### P1

- 跑 `summarize_results.py`
- 跑 `compare_errors.py`
- 跑 `make_case_study_table.py`

### P2

- 写报告
- 做 PPT
- 补 `notes.md`

### P3

- `5k` 数据规模扩展
- `single vs multi template`
- `LoRA r=8 vs r=16`
- GUI grounding bonus

---

## 10. 不建议现在做的事情

在 `E00`–`E03` 完成前，不建议投入：

- Janus-Pro 对比
- image generation 方向
- 完整 GUI agent
- 大规模 rank sweep
- 多模型横评
- 10k 或全量训练

原因：

- 会显著扩张实验矩阵
- 与课程最低可交付目标不一致
- 容易拖慢主线完成时间

---

## 11. 一句话版本

接下来最重要的不是继续补功能，而是把 `E00 zero-shot`、`E01 prompt-only`、`E02 LoRA-random-2k`、`E03 LoRA-failure-2k` 这四组实验完整跑完，并自动生成结果表、错误分析和 case study，为最终报告提供可追溯证据。
