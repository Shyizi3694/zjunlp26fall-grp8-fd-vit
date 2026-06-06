# FD-VIT 报告与展示清单

本文档用于确保 coding 产物可以顺利转化为课程大作业报告、PPT 和答辩材料。

---

## 1. 报告标题

推荐标题：

> 基于失败驱动指令微调的多模态视觉推理增强：以 Qwen3-VL 为例

英文可用：

> FD-VIT: Failure-Driven Visual Instruction Tuning for Multimodal Visual Reasoning

---

## 2. 报告核心故事线

报告应围绕一个问题展开：

> 对 VQA / OK-VQA 视觉推理任务，少量 failure-driven 视觉指令数据是否比同规模 random 数据更有效？

不要把报告写成“我们试了很多模型和很多任务”。主线越清楚越好。

---

## 3. 推荐报告结构

### 3.1 Introduction

要说明：

- 多模态大模型在视觉问答上已经很强；
- 但在细粒度视觉推理、常识推理、输出格式控制上仍会失败；
- 课程项目关注 instruction tuning；
- 本项目提出 failure-driven visual instruction tuning；
- 研究问题是 failure-driven sampling 是否比 random sampling 更有效。

建议贡献点：

1. 构建面向 OK-VQA/VQA 的多模板视觉指令微调流程；
2. 提出 failure-driven sampling 策略，从 baseline 错误中构造 hard training subset；
3. 在 zero-shot、prompt-only、random LoRA 和 failure-driven LoRA 间做系统对比；
4. 按错误类型分析微调带来的改善与局限。

### 3.2 Related Work

建议覆盖：

- Multimodal Large Language Models；
- Visual Instruction Tuning；
- VQA / OK-VQA；
- Parameter-Efficient Fine-Tuning / LoRA / QLoRA；
- Visual Agent / GUI Grounding，若做 bonus。

注意：不要堆论文摘要，要围绕“为什么选择 Qwen3-VL + OK-VQA + LoRA + failure-driven sampling”。

### 3.3 Method

建议分三阶段：

```text
Stage 1: Baseline probing
Stage 2: Task-aware visual instruction tuning
Stage 3: Failure-driven refinement
```

方法图应包含：

```text
OK-VQA train/val
    ↓
Data conversion + prompt templates
    ↓
Qwen3-VL zero-shot probing
    ↓
Failure mining + error taxonomy
    ↓
Random subset        Failure-driven subset
    ↓                ↓
LoRA-random          LoRA-failure
    ↓                ↓
Unified evaluation + error analysis
```

### 3.4 Experimental Setup

必须写清楚：

- 模型版本；
- 数据集与 split；
- 训练样本数；
- 评测样本数；
- prompt 模板；
- LoRA 参数；
- 训练硬件；
- 推理 generation config；
- 答案 normalization；
- 指标定义；
- random seed；
- failure-driven subset 如何构造；
- 没有使用最终评测集训练。

### 3.5 Results

至少三张表：

1. 主结果表；
2. 消融实验表；
3. 错误类型表。

主结果表模板：

| Setting | Train n | Sampling | acc_any | acc_soft | format_error_rate | Δ vs zero-shot | Δ vs random |
|---|---:|---|---:|---:|---:|---:|---:|
| Zero-shot | 0 | - | - | - | - | - | - |
| Prompt-only | 0 | - | - | - | - | - | - |
| LoRA-random | 2k | random | - | - | - | - | - |
| LoRA-failure | 2k | failure | - | - | - | - | - |

### 3.6 Error Analysis

要回答：

- 哪些错误类型改善最多；
- 哪些错误类型仍然困难；
- failure-driven 是否降低 format error；
- random LoRA 与 failure LoRA 的差异在哪；
- 是否存在过拟合某类错误的迹象。

错误类型表模板：

| Error type | Zero-shot | Prompt-only | Random LoRA | Failure LoRA | Observation |
|---|---:|---:|---:|---:|---|
| answer_format | - | - | - | - | - |
| counting | - | - | - | - | - |
| ocr_text | - | - | - | - | - |
| spatial | - | - | - | - | - |
| attribute | - | - | - | - | - |
| commonsense | - | - | - | - | - |

### 3.7 Qualitative Analysis

至少 6–10 个 case：

- 微调前错，failure-driven 后对；
- random LoRA 错，failure-driven 对；
- failure-driven 仍错；
- format error 修复；
- counting / spatial / commonsense 各至少一个。

case 表模板：

| Case | Question | GT | Zero-shot | Random LoRA | Failure LoRA | Error Type | Note |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... | ... |

如果报告格式允许，可以配图；如果配图，注意数据集许可与清晰度。

### 3.8 Bonus: GUI Grounding

只有主线完成后再写。内容包括：

- 任务定义；
- 数据小样本；
- 输出坐标格式；
- point-in-bbox 指标；
- 1–2 个示例；
- 明确说明不是完整 GUI Agent。

### 3.9 Conclusion

应总结：

- failure-driven sampling 相比 random 的效果；
- 多模板/短答案约束的作用；
- 哪些错误类型仍然难；
- 项目局限与未来工作。

---

## 4. 必备图表清单

### 4.1 必备表格

- `Table 1`: 主结果表；
- `Table 2`: 消融实验表；
- `Table 3`: 错误类型对比表；
- `Table 4`: 训练配置表，可选。

### 4.2 必备图

- 方法 pipeline 图；
- 错误类型分布柱状图，可选；
- qualitative case 图，可选。

### 4.3 自动生成来源

所有表格数字应来自：

```text
outputs/results_main.csv
outputs/error_comparison.csv
outputs/E*/metrics.json
```

不要从聊天记录或手工笔记中抄数字。

---

## 5. 实验结果写作模板

### 5.1 如果 failure-driven 明显更好

可写：

> Under the same base model, training size, LoRA rank, and evaluation protocol, the failure-driven LoRA model outperforms the random LoRA baseline. This suggests that mining errors from baseline probing can produce a more informative visual instruction subset than uniform random sampling.

中文：

> 在相同基础模型、训练规模、LoRA 配置和评测协议下，failure-driven LoRA 优于 random LoRA，说明从 baseline 错误中挖掘高价值样本能够比均匀随机采样产生更有效的视觉指令数据。

### 5.2 如果 failure-driven 持平

可写：

> Although failure-driven sampling does not significantly improve the overall accuracy over random sampling, it changes the error distribution and reduces specific failure types such as answer format errors. This indicates that the current sampling strategy may be more effective for targeted behavior correction than for broad capability improvement.

中文：

> 虽然 failure-driven sampling 没有显著提高总体准确率，但它改变了错误分布，并可能降低特定错误类型，例如答案格式错误。这说明当前采样策略更适合定向行为修正，而不一定能全面提升模型能力。

### 5.3 如果 failure-driven 更差

可写：

> Failure-driven sampling underperforms random sampling in our current setup, possibly because the mined subset is too narrow or noisy. This negative result is still informative: it shows that failure-driven data construction requires careful balancing between hard examples and distribution coverage.

中文：

> 在当前设置下，failure-driven sampling 低于 random sampling，可能是因为挖掘出的 hard subset 过窄或噪声较大。这个负结果仍有价值，因为它说明失败驱动的数据构造需要在困难样本和分布覆盖之间取得平衡。

---

## 6. 答辩 PPT 建议结构

10–12 页即可：

1. 题目与团队；
2. 背景：MLLM 在视觉推理中的问题；
3. 研究问题：failure-driven 是否优于 random；
4. 方法 pipeline；
5. 数据与模型设置；
6. 实验矩阵；
7. 主结果表；
8. 错误类型分析；
9. qualitative cases；
10. bonus GUI grounding，可选；
11. 局限；
12. 总结。

---

## 7. 最终提交文件建议

```text
final_submission/
├── report.pdf
├── slides.pdf 或 slides.pptx
├── code.zip
├── README.md
├── requirements.txt
├── docs/
├── configs/
├── scripts/
├── src/
└── outputs_summary/
    ├── results_main.csv
    ├── error_comparison.csv
    ├── case_studies.md
    └── metrics_json/
```

不要提交：

- 大模型权重；
- 原始 COCO 图片；
- 大量 checkpoint；
- 私有路径；
- token 或账号信息。

---

## 8. 最终报告自检

提交前逐项确认：

- [ ] 标题与主线一致；
- [ ] 明确说明数据集和模型；
- [ ] 明确说明 zero-shot baseline；
- [ ] 明确说明 prompt-only baseline；
- [ ] random LoRA 与 failure LoRA 公平对比；
- [ ] 指标定义清楚；
- [ ] 答案 normalization 说明清楚；
- [ ] 没有测试集污染；
- [ ] 主结果表有数值；
- [ ] 错误类型表有数值；
- [ ] qualitative cases 可读；
- [ ] 局限没有回避；
- [ ] 所有数字可追溯到输出文件；
- [ ] 没有夸大结论。

---

## 9. 最后一句话

报告的核心不是“我们训练了一个多模态大模型”，而是：

> 我们用 baseline 失败样本反向指导视觉指令数据构造，并通过严格 baseline、统一评测和错误类型分析验证这种数据策略是否比随机采样更有效。
