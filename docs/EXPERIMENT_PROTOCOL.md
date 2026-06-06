# FD-VIT 实验协议

本文档定义项目实验矩阵、指标、随机种子、命名规则、结果汇总方式和防止数据污染的约束。coding agent 跑任何实验前必须确认本协议。

---

## 1. 核心实验假设

本项目验证：

> 在相同 base model、相同训练规模、相同 LoRA 配置、相同评测集下，failure-driven instruction tuning 是否优于 random instruction tuning？

因此，主实验只允许改变一个变量：**训练样本采样策略**。

---

## 2. 固定变量

主实验必须固定：

| 变量 | 固定值 |
|---|---|
| base model | Qwen3-VL-4B-Instruct，显存不足时统一换 2B 或 QLoRA |
| dataset | OK-VQA，必要时 VQA v2 子集 |
| train size | 2k，扩展实验可 5k |
| eval set | 同一个 val_1k / val_5k / val_full |
| LoRA rank | r=8 |
| prompt mode | strict short-answer，多模板训练 |
| evaluation script | `scripts/evaluate_vqa.py` |
| random seed | 42，扩展可 43/44 |
| generation config | temperature=0.0, max_new_tokens=16，除非另有记录 |

---

## 3. 必做实验矩阵

| Exp ID | Setting | Train data | Train n | Sampling | LoRA r | Eval | 目的 |
|---|---|---|---:|---|---:|---|---|
| E00 | Zero-shot basic | - | 0 | - | - | val_1k | 原始模型 baseline |
| E01 | Prompt-only strict | - | 0 | - | - | val_1k | 排除 prompt 改写影响 |
| E02 | LoRA-random-2k | `train_random_2k` | 2k | random | 8 | val_1k | 普通指令微调 baseline |
| E03 | LoRA-failure-2k | `train_failure_2k` | 2k | failure-driven | 8 | val_1k | 核心方法 |

这是最小可交付版本，任何其他实验都不能替代 E00–E03。

---

## 4. 推荐扩展实验

主线跑通后再做：

| Exp ID | Setting | Train n | 变量 | 优先级 |
|---|---|---:|---|---:|
| E04 | LoRA-random-5k | 5k | 数据规模 | 中 |
| E05 | LoRA-failure-5k | 5k | 数据规模 + 采样策略 | 中 |
| E06 | Single-template LoRA | 2k | 模板数量 | 中 |
| E07 | Multi-template LoRA | 2k | 模板数量 | 中 |
| E08 | LoRA-failure-r16 | 2k | LoRA rank | 低 |
| B01 | GUI grounding demo | 小样本 | bonus | 低 |

不推荐：

- Janus-Pro 全量对比；
- 图像生成评测；
- 完整 GUI Agent；
- 10k/全量训练作为必做项；
- 多个模型、多组 rank、多组 prompt 的笛卡尔积。

---

## 5. 数据划分协议

### 5.1 默认划分

| 数据 | 用途 | 是否可训练 |
|---|---|---:|
| train | LoRA 训练、failure-driven subset 构造 | 是 |
| train-probe subset | baseline probing，用于发现训练分布中的失败样本 | 是 |
| val_1k | 快速评测 | 否 |
| val_5k / val_full | 最终评测 | 否 |
| test | 如果有官方 test 且无 label，仅做最终提交或不使用 | 否 |

### 5.2 failure-driven 采样规则

允许：

- 在 train 或 train-probe subset 上跑 baseline；
- 从 train 中 baseline 错误样本构造 failure-driven 训练集；
- 用 val_1k 做开发评测。

禁止：

- 从最终评测 val_full / test 中选错题加入训练；
- 先看最终测试结果再回流训练；
- 使用不同 eval subset 对比 E02 和 E03。

---

## 6. 指标定义

### 6.1 主指标

| 指标 | 名称 | 说明 |
|---|---|---|
| `acc_any` | 任一答案匹配准确率 | normalized prediction 匹配任一 normalized GT answer |
| `acc_soft` | 类 VQA soft accuracy | `min(match_count / 3, 1)` |
| `format_error_rate` | 格式错误率 | 空输出、过长、带解释等比例 |

### 6.2 辅助指标

| 指标 | 说明 |
|---|---|
| `empty_prediction_rate` | 空预测比例 |
| `avg_prediction_length_tokens` | 平均输出 token 数 |
| `num_valid_predictions` | 成功推理样本数 |
| `latency_avg_sec` | 平均推理耗时 |
| `error_type_count` | 每类错误数量 |
| `error_type_rate` | 每类错误占比 |

### 6.3 GUI bonus 指标

| 指标 | 说明 |
|---|---|
| `point_in_bbox_acc` | 预测点落入 GT bbox 的比例 |
| `parse_success_rate` | 输出可解析成坐标的比例 |
| `center_distance_norm` | 归一化中心点距离 |

---

## 7. 结果表格式

### 7.1 主结果表

| Exp | Setting | Train n | Sampling | LoRA r | acc_any | acc_soft | format_error_rate | Δacc_soft vs E00 | Δacc_soft vs E02 |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| E00 | Zero-shot | 0 | - | - | - | - | - | - | - |
| E01 | Prompt-only | 0 | - | - | - | - | - | - | - |
| E02 | LoRA-random | 2k | random | 8 | - | - | - | - | - |
| E03 | LoRA-failure | 2k | failure | 8 | - | - | - | - | - |

### 7.2 错误类型表

| error_type | E00 errors | E01 errors | E02 errors | E03 errors | E03 vs E02 |
|---|---:|---:|---:|---:|---:|
| answer_format | - | - | - | - | - |
| counting | - | - | - | - | - |
| ocr_text | - | - | - | - | - |
| spatial | - | - | - | - | - |
| attribute | - | - | - | - | - |
| commonsense | - | - | - | - | - |
| hallucination | - | - | - | - | - |
| ambiguous | - | - | - | - | - |
| other | - | - | - | - | - |

### 7.3 消融表

| Exp | Variable | Setting | acc_any | acc_soft | format_error_rate |
|---|---|---|---:|---:|---:|
| E02 | sampling | random | - | - | - |
| E03 | sampling | failure | - | - | - |
| E06 | template | single | - | - | - |
| E07 | template | multi | - | - | - |

---

## 8. 随机种子协议

默认 seed：42。

涉及以下操作必须显式设置 seed：

- random subset 采样；
- failure-driven subset 中类别内采样；
- prompt template 多模板随机选择；
- train/val subset 抽样；
- case study 抽样。

如果做多 seed，使用：42、43、44。报告中说明均值和标准差。

---

## 9. 运行记录协议

每个实验目录必须包含：

```text
outputs/E03_lora_failure_2k_r8/
├── predictions.jsonl
├── metrics.json
├── errors.jsonl
├── error_summary.csv
├── run_config.yaml
├── command.txt
├── environment.txt
└── notes.md
```

### 9.1 command.txt

保存完整命令，例如：

```bash
python scripts/run_inference.py --config configs/infer_lora_failure_2k.yaml --input data/processed/okvqa/val_1k.jsonl --lora_checkpoint checkpoints/lora_failure_2k --output outputs/E03_lora_failure_2k_r8/predictions.jsonl --seed 42
```

### 9.2 notes.md

记录：

- 是否完整跑完；
- 是否有异常样本；
- 是否使用 subset；
- 是否与标准配置有偏差；
- 任何会影响结果解释的事项。

---

## 10. 实验执行顺序

严格按以下顺序执行：

1. 数据转换和 validate；
2. prompt preview；
3. E00 zero-shot 10 条 smoke test；
4. E00 zero-shot val_1k；
5. evaluate E00；
6. E01 prompt-only val_1k；
7. evaluate E01；
8. train-probe failure mining；
9. 构造 random/failure 2k；
10. 训练 E02 LoRA-random；
11. 训练 E03 LoRA-failure；
12. 评测 E02/E03；
13. 汇总主结果表；
14. 错误类型对比；
15. qualitative cases；
16. 可选扩展实验。

---

## 11. 结果解释协议

### 11.1 如果 E03 > E02

可以说：

- 在相同训练规模和 LoRA 配置下，failure-driven sampling 优于 random sampling；
- 进一步通过错误类型表说明提升主要来自哪些类别；
- 不要声称模型整体能力全面提升，除非多数据集验证。

### 11.2 如果 E03 ≈ E02

可以说：

- failure-driven sampling 没有显著提高总体准确率；
- 但可能降低 format error 或改善特定错误类型；
- 分析 failure subset 是否偏窄、标注是否噪声大、训练规模是否不足。

### 11.3 如果 E03 < E02

可以说：

- 当前 failure-driven 构造策略可能过拟合错误类型或引入分布偏差；
- random 数据覆盖更广；
- 仍可把项目写成负结果 + 错误分析，强调方法局限。

禁止：

- 只根据一两个 case 夸大方法；
- 不报告 random baseline；
- 不报告 format error；
- 不说明数据来源和采样策略。

---

## 12. 验收门槛

### 12.1 最小验收

- E00–E03 全部有 predictions 和 metrics；
- E02/E03 使用同一 eval set；
- 主结果表自动生成；
- 错误类型表存在；
- 至少 6 个 qualitative cases。

### 12.2 标准验收

- val_1k 和更大 val subset 均有结果；
- 至少一个消融；
- 错误类型表经过部分人工复核；
- 训练日志完整；
- 报告中有清楚的 method diagram 或 pipeline 图。

---

## 13. 最终可引用文件

报告中优先引用以下文件：

```text
outputs/results_main.md
outputs/results_main.csv
outputs/error_comparison.md
outputs/error_comparison.csv
outputs/case_studies.md
outputs/E*/metrics.json
outputs/E*/predictions.jsonl
checkpoints/*/train_config.yaml
```

报告中的数字不得来自聊天记录或手工估计，必须可追溯到上述文件。
