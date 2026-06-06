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
