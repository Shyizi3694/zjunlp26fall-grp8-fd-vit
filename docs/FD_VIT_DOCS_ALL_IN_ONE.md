# FD-VIT Docs All In One

> Version: 2026-06-06-regenerated  
> This file concatenates the main FD-VIT documentation files for convenient reading by coding agents.  
> The individual files remain the source of truth for editing.  
> Regenerate this file after changing any document listed below.

## Included Files

- `README.md`
- `project_requirements.md`
- `REQUIREMENTS_TRACEABILITY.md`
- `FD_VIT_CODING_AGENT_GUIDE.md`
- `DATA_AND_FORMAT_CONTRACT.md`
- `EXPERIMENT_PROTOCOL.md`
- `ERROR_TAXONOMY.md`
- `CODING_AGENT_TASK_CARDS.md`
- `REPORT_CHECKLIST.md`

---



# File: README.md

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


---


# File: project_requirements.md

# Project Requirements: 选题一、基于多模态大模型的视觉推理

> 本文件由课程原始 Word 文档 `选题一 基于多模态大模型的视觉推理.docx` 转写而来，用作项目要求的溯源参考。  
> 本文件不是 FD-VIT 的执行方案；实际 coding agent 执行时应以 `FD_VIT_CODING_AGENT_GUIDE.md`、`DATA_AND_FORMAT_CONTRACT.md` 和 `EXPERIMENT_PROTOCOL.md` 为准。

## 1. 作业要求

自由选择开源的多模态大模型，例如 QwenVL、Janus-Pro 等，以及下游的视觉推理任务，例如 VQA、image-caption、image-generation，也可以是 visual agentic 任务。

需要尝试对多模态模型做简单的指令微调，并测试其在下游任务中的性能。

在这个大范围下，欢迎同学们自由发挥。

## 2. 可供选择的大模型

### 2.1 Qwen3-VL（推荐）

- 论文：<https://arxiv.org/abs/2511.21631>
- GitHub：<https://github.com/QwenLM/Qwen3-VL.git>
- 建议使用 4B 小模型：<https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct>

**图片说明：** 原 Word 在此处配有一张 Qwen3-VL 架构图，展示了 Vision Encoder 与 Qwen3 LM Dense/MoE Decoder 的连接方式，以及图像、视频 token 如何输入到语言模型中。该图主要用于说明 Qwen3-VL 是面向图像和视频理解的多模态模型。

### 2.2 Janus-Pro（推荐）

Janus-Pro: Unified Multimodal Understanding and Generation with Data and Model Scaling

- 论文：<https://arxiv.org/abs/2501.17811>
- GitHub：<https://github.com/deepseek-ai/Janus.git>

**图片说明：** 原 Word 在此处配有一张 Janus-Pro 架构图，展示其同时支持 multimodal understanding 与 image generation：左侧是图像理解路径，右侧是图像生成路径，中间共享 auto-regressive transformer。该图主要用于说明 Janus-Pro 适合理解与生成统一建模。

### 2.3 其他模型

可供选择的大模型包括但不限于上述两个模型。请同学们仔细阅读所选择模型的对应论文，并研究对应的项目 GitHub。

## 3. 可供选择的下游任务测试数据

### 3.1 Image Caption

- Flickr30K 测试集：<https://huggingface.co/datasets/nlphuji/flickr30k/tree/main>

### 3.2 VQA

- VQA 数据：<https://drive.google.com/open?id=1_VvBqqxPW_5HQxE6alZ7_-SGwbEt2_zn>
- OKVQA-testset：<https://okvqa.allenai.org/download.html>

### 3.3 Image Generation

对于 Janus-Pro 等统一图像理解生成模型，还可以考虑图像生成等任务。

### 3.4 Visual Agent（BONUS）

可以考虑一些视觉智能体（Visual Agent）任务，例如 GUI Agent / Computer Use Agent 等。

该类任务相比传统 VQA、Caption 等静态视觉理解任务，进一步要求模型具备多步推理、环境交互、动作决策和长程任务规划等能力，因此任务复杂度和难度都更高。选择该方向将视工作量和完成度进行适当加分。

可参考数据或基准：

- ScreenSpot：<https://huggingface.co/datasets/rootsautomation/ScreenSpot>
- VisualAgentBench：<https://github.com/THUDM/VisualAgentBench>
- ……

同学可以从中，也可以不局限于此，任选下游数据集进行测试。

## 4. 可供选择的指令微调数据

- COCO 数据：<https://cocodataset.org/#download>
- Flickr30K 训练数据：<https://huggingface.co/datasets/nlphuji/flickr30k/tree/main>
- 一些 VQA 数据：<https://visualqa.org/download.html>
- RICO 数据（GUI screenshot 与 widget 数据）：<https://huggingface.co/datasets/Voxel51/rico>
- GUI grounding / interaction trajectory 数据：<https://github.com/njucckevin/SeeClick>
- ……

具体选择哪些数据以及使用多大量级的指令微调数据不做任何限制。请同学们根据自己的目标下游任务选择合适的训练数据。

## 5. 指令微调方法

### 5.1 数据预处理

将训练数据按照指令模板构建成特定格式。原 Word 提到可参考 InstructBLIP: Towards General-purpose Vision-Language Models with Instruction Tuning 的最后一页：

- InstructBLIP 论文：<https://arxiv.org/pdf/2305.06500>

**图片说明：** 原 Word 在此处配有一张指令模板表，列出了 Image Captioning 与 VQA 的多种 `<Image>` prompt 写法。例如 caption 模板要求模型描述图像内容，VQA 模板则把 `{Question}` 填入提示词并要求短答案。该图对本项目最有用，因为它提示我们应使用多模板 instruction tuning，而不是只用单一 prompt。

### 5.2 微调参数

在显存有限的情况下，可以只微调连接视觉模块和 LLM 的线性映射层，参考 MiniGPT-4 的文章和代码。

在显存比较充足的情况下，可以采用 LoRA（Low-Rank Adaptation of Large Language Models）的方式微调 LLM，参考 MiniGPT-v2: Large Language Model As a Unified Interface for Vision-Language Multi-task Learning 的文章和代码。

具体请参考所选择的大模型对应的论文和 GitHub 库。


---


# File: REQUIREMENTS_TRACEABILITY.md

# Requirements Traceability

> 本文件用于说明课程 Word 要求如何被 FD-VIT 项目方案覆盖。  
> `project_requirements.md` 是课程要求的溯源文件；本文件是“要求 → 项目决策 → 实现文档/产物”的映射。  
> Coding agent 不应依据课程要求自由扩展范围，而应按照本文件和 `FD_VIT_CODING_AGENT_GUIDE.md` 中的边界执行。

## 1. FD-VIT 对课程要求的总体覆盖

课程要求的核心是：选择开源多模态大模型，选择视觉推理下游任务，构造指令微调数据，进行简单指令微调，并测试下游性能。

FD-VIT 对应的执行主线是：

```text
Qwen3-VL-4B-Instruct
→ OK-VQA / VQA 子集
→ zero-shot baseline
→ prompt-only baseline
→ LoRA-random instruction tuning
→ LoRA-failure-driven instruction tuning
→ VQA accuracy / OK-VQA accuracy / 错误类型分析
→ 可选 GUI grounding bonus
```

该主线保持一个模型、一个主任务族、一个核心创新变量，即 `random sampling vs failure-driven sampling`。这样可以避免实验矩阵爆炸，同时满足课程对“指令微调 + 下游性能测试”的要求。

## 2. 课程要求到项目决策的映射

| 课程要求 / 可选范围 | FD-VIT 项目决策 | 覆盖方式 | 主要文档 / 产物 |
|---|---|---|---|
| 自由选择开源多模态大模型 | 主模型选择 `Qwen3-VL-4B-Instruct` | 使用开源 MLLM 完成视觉理解与 VQA 推理 | `FD_VIT_CODING_AGENT_GUIDE.md`, `EXPERIMENT_PROTOCOL.md` |
| 可选模型包括 QwenVL / Qwen3-VL / Janus-Pro 等 | 采用 Qwen3-VL；Janus-Pro 不作为主线 | Qwen3-VL 更适合可量化 VQA 主线；Janus-Pro 只作为 related work 或可选对比 | `project_requirements.md`, `REPORT_CHECKLIST.md` |
| 下游视觉推理任务可选 VQA、image-caption、image-generation、visual agentic task | 主任务选择 OK-VQA / VQA；GUI grounding 只作为 bonus | VQA / OK-VQA 有成熟评价指标，视觉推理属性更强；GUI 不压主线 | `EXPERIMENT_PROTOCOL.md`, `ERROR_TAXONOMY.md` |
| 尝试对多模态模型做简单指令微调 | 使用 LoRA / QLoRA；显存不足时降级 projector-only | 满足“简单指令微调”，控制显存与工程风险 | `FD_VIT_CODING_AGENT_GUIDE.md`, `EXPERIMENT_PROTOCOL.md` |
| 测试下游任务性能 | 跑 zero-shot、prompt-only、LoRA-random、LoRA-failure-driven | 用统一评测脚本输出 accuracy、逐样本预测、错误类型统计 | `EXPERIMENT_PROTOCOL.md`, `DATA_AND_FORMAT_CONTRACT.md` |
| 可使用 Flickr30K 测试集做 Image Caption | 不作为主线；可作为辅助视觉描述能力数据或报告扩展 | 主线聚焦 VQA/OK-VQA；caption 不进入必做实验 | `REQUIREMENTS_TRACEABILITY.md` |
| 可使用 VQA / OKVQA 测试集 | 采用 OK-VQA / VQA 子集作为主测试任务 | 与视觉推理定位一致，便于量化 | `DATA_AND_FORMAT_CONTRACT.md`, `EXPERIMENT_PROTOCOL.md` |
| 可考虑 Janus-Pro 图像生成任务 | 不做主线；不进行图像生成训练或主观生成评测 | 图像生成评测主观、训练成本高，不适合保底主线 | `FD_VIT_CODING_AGENT_GUIDE.md`, `REPORT_CHECKLIST.md` |
| Visual Agent / GUI Agent / Computer Use Agent 为 BONUS | 仅保留轻量 GUI grounding demo / 小样本评测 | 不做完整 agent，不做环境交互闭环；只评估点选或 bbox 命中 | `EXPERIMENT_PROTOCOL.md` |
| 可用 COCO、Flickr30K、VQA、RICO、SeeClick 等训练数据 | 主训练数据使用 VQA / OK-VQA；GUI 数据仅 bonus | 训练数据与目标评测任务保持一致，降低数据转换复杂度 | `DATA_AND_FORMAT_CONTRACT.md` |
| 按 InstructBLIP 风格构造指令模板 | 使用多模板 VQA prompt，并统一 short-answer 约束 | 训练和推理都采用 `<image>` + question + short answer 格式 | `prompts/`, `DATA_AND_FORMAT_CONTRACT.md` |
| 显存有限时可只调视觉模块与 LLM 的线性映射层 | 作为 fallback：projector-only | 当 LoRA / QLoRA 环境或显存失败时保底 | `EXPERIMENT_PROTOCOL.md` |
| 显存充足时可用 LoRA 微调 LLM | 标准方案使用 LoRA，固定 rank 优先 r=8 | 主实验不做大规模 rank sweep | `EXPERIMENT_PROTOCOL.md` |
| 参考所选模型论文和 GitHub | 报告中说明 Qwen3-VL、LoRA、VQA/OK-VQA、InstructBLIP 等相关工作 | 保证方法来源清楚，不只是工程堆砌 | `REPORT_CHECKLIST.md` |

## 3. 必须完成的课程覆盖项

以下项目完成后，可以认为课程 Word 的核心要求已被覆盖：

| 编号 | 必须项 | 最低验收标准 |
|---|---|---|
| R1 | 选择并运行开源 MLLM | 能用 Qwen3-VL-4B-Instruct 或降级模型完成批量推理 |
| R2 | 选择视觉推理下游任务 | OK-VQA / VQA 子集已准备，包含图像路径、问题、标准答案 |
| R3 | 构造指令微调数据 | 训练数据已转换为 Qwen 风格 conversation JSON，包含 `<image>` 与 short-answer prompt |
| R4 | 完成 baseline 测试 | 至少完成 zero-shot 与 prompt-only 两组评测 |
| R5 | 完成简单指令微调 | 至少完成 LoRA-random 与 LoRA-failure-driven 两组之一；推荐两组都完成用于对照 |
| R6 | 完成下游性能测试 | 输出 VQA accuracy / OK-VQA accuracy、逐样本 prediction、metrics JSON |
| R7 | 完成错误分析 | 至少按 answer_format、counting、OCR/text-rich、spatial、attribute、commonsense、hallucination 等类型统计 |
| R8 | 完成报告可复现说明 | 记录模型版本、数据规模、prompt 模板、训练参数、硬件、随机种子、checkpoint 路径 |

## 4. 推荐完成的主实验覆盖项

最终报告最推荐呈现以下实验表：

| Exp ID | Setting | 作用 | 是否主线必需 |
|---|---|---|---|
| E00 | Qwen3-VL zero-shot | 原始模型能力 | 必须 |
| E01 | Prompt-only | 验证 prompt 优化能带来的提升 | 必须 |
| E02 | LoRA-random | 普通指令微调 baseline | 必须 |
| E03 | LoRA-failure-driven | FD-VIT 核心方法 | 必须 |
| E04 | 模板数量消融 | 验证多模板 instruction 是否改善鲁棒性 | 可选 |
| E05 | 数据规模消融 | 验证 1k / 2k / 5k 规模影响 | 可选 |
| E06 | GUI grounding 小样本 demo | 对应 Visual Agent bonus | 可选 |

最低可交付版本应优先保证 E00–E03，不要先投入 E04–E06。

## 5. 明确不作为主线的内容

| 内容 | 状态 | 原因 |
|---|---|---|
| Janus-Pro 主实验 | 不做主线 | 图像生成与统一理解生成评测成本高，容易分散主线 |
| Image generation 训练 / 评测 | 不做主线 | 主观评价强、工程复杂度高，不利于课程保底 |
| 完整 GUI Agent / Computer Use Agent | 不做主线 | 需要环境交互、多步规划、动作执行与复杂评测协议 |
| 多模型大横评 | 不做主线 | 容易变成模型 benchmark，削弱 failure-driven tuning 贡献 |
| 大规模 LoRA rank sweep | 不做主线 | 训练成本高，且不是核心研究问题 |
| 10k+ 大规模训练 | 不作为第一阶段目标 | 先保证 2k–5k 小规模稳定复现 |

## 6. 对 coding agent 的执行约束

Coding agent 在任何阶段都必须遵守以下规则：

1. 不要因为 `project_requirements.md` 中列出了 Janus-Pro、image generation、Visual Agent 等选项，就自动扩大项目范围。
2. 当前主线只允许围绕 Qwen3-VL + OK-VQA/VQA + LoRA/QLoRA + failure-driven sampling 展开。
3. 所有数据格式必须遵守 `DATA_AND_FORMAT_CONTRACT.md`。
4. 所有实验编号、输出目录和指标必须遵守 `EXPERIMENT_PROTOCOL.md`。
5. 所有错误分析标签必须遵守 `ERROR_TAXONOMY.md`。
6. 所有报告结论必须能追溯到 E00–E03 的结果表、metrics JSON 和逐样本 prediction 文件。
7. 任何新增实验必须先被标记为 optional，并不得影响 E00–E03 的交付。

## 7. 最终交付与课程要求的对应关系

| 最终交付物 | 对应课程要求 |
|---|---|
| 代码仓库与 README | 展示所选模型、任务、运行方式和复现实验流程 |
| 数据转换脚本 | 展示如何将下游数据构造成 instruction tuning 格式 |
| LoRA / QLoRA 训练脚本或配置 | 展示对多模态模型的简单指令微调 |
| 推理与评测脚本 | 展示下游任务性能测试 |
| 主结果表 | 展示微调前后性能差异 |
| 错误类型分析表 | 展示 failure-driven sampling 的动机与效果 |
| qualitative cases | 展示模型微调前后的具体能力变化 |
| 最终报告 | 汇总模型、数据、方法、实验、分析与局限 |

## 8. 一句话执行边界

> 课程要求允许自由发挥；FD-VIT 的策略是只选择其中最稳、最可量化的一条路径：Qwen3-VL + OK-VQA/VQA + LoRA 指令微调 + failure-driven sampling。其他方向只作为背景、附录或可选 bonus，不进入主线。


---


# File: FD_VIT_CODING_AGENT_GUIDE.md

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

## 12.4 指标

| 指标 | 含义 |
|---|---|
| point_in_bbox_acc | 预测点是否落在 GT bbox 内 |
| center_distance | 预测点到目标中心点的归一化距离 |
| parse_success_rate | 模型输出是否能解析出坐标 |
| control_type_acc | 按按钮、菜单、输入框等类型统计准确率 |

## 12.5 验收标准

- 只做小样本；
- 不训练完整 agent；
- 不引入复杂交互环境；
- 坐标归一化规则写清楚；
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


---


# File: DATA_AND_FORMAT_CONTRACT.md

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


---


# File: EXPERIMENT_PROTOCOL.md

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


---


# File: ERROR_TAXONOMY.md

# FD-VIT 错误类型分类标准

本文档用于统一 VQA / OK-VQA 错误分析、failure-driven sampling 和 qualitative case study。所有错误样本应尽量标注一个主错误类型；如存在多个错误原因，可记录 secondary error type。

---

## 1. 标注原则

1. 优先标注导致最终答案错误的主要原因。
2. 如果模型答案本质正确但格式导致评测错误，标为 `answer_format`。
3. 如果问题/GT 本身有歧义，标为 `ambiguous`，不要强行归入模型能力问题。
4. 如果仅凭预测文本无法判断，保留 `other`，后续人工看图复核。
5. 自动弱标注只能作为初稿，报告中的关键结论最好经过人工抽样复核。

---

## 2. 错误类型总览

| error_type | 中文名 | 简要说明 |
|---|---|---|
| `answer_format` | 答案格式错误 | 输出太长、带解释、空输出、未按短答案输出 |
| `counting` | 数量错误 | 物体数量、人数、次数等判断错误 |
| `ocr_text` | OCR/文字错误 | 图中文字、数字、招牌、屏幕、菜单等识别错误 |
| `spatial` | 空间关系错误 | 左右、前后、上下、遮挡、相对位置判断错误 |
| `attribute` | 属性错误 | 颜色、材质、类别、状态、动作等识别错误 |
| `commonsense` | 常识/外部知识错误 | 需要常识、地理、品牌、用途、文化知识等 |
| `hallucination` | 幻觉 | 编造图中不存在的物体、关系或场景 |
| `ambiguous` | 问题/标注歧义 | 问题不清、多个合理答案、GT 不充分 |
| `other` | 其他 | 无法归类或需要人工复核 |

---

## 3. 各类型详细定义

### 3.1 `answer_format`

定义：模型知道答案或可能接近答案，但输出格式不符合 VQA 短答案评测要求。

常见表现：

- 输出完整句子：`The answer is tennis.`；
- 输出解释：`It is tennis because the person is holding a racket.`；
- 输出多个候选：`tennis or badminton`；
- 输出空字符串；
- 输出无法解析的内容；
- 输出与答案有关但包含多余前缀后缀。

自动规则示例：

- prediction token 数 > 6；
- 包含 `because`, `I think`, `the answer is`, `it is`, `there are`；
- prediction 为空。

注意：如果模型输出长句但 normalization 后仍能正确匹配，可以不计入错误；但可在 format analysis 中记录。

---

### 3.2 `counting`

定义：问题核心是数量，模型数量判断错误。

关键词：

- `how many`；
- `number of`；
- `count`；
- `several`；
- `both`；
- `one/two/three` 等数量回答。

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| How many dogs are on the couch? | 2 | 3 | counting |
| How many people are wearing hats? | one | two | counting |

常见原因：

- 遮挡；
- 小目标；
- 多实例混淆；
- 背景物体误计入。

---

### 3.3 `ocr_text`

定义：问题需要读取图中文字、数字、标牌、菜单、屏幕内容、车牌、衣服文字等。

关键词：

- `what does the sign say`；
- `read`；
- `text`；
- `word`；
- `number`；
- `license plate`；
- `menu`；
- `screen`；
- `label`。

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| What word is on the sign? | stop | slow | ocr_text |
| What number is on the bus? | 42 | 24 | ocr_text |

注意：如果问题问数量而答案是数字，不一定是 OCR；要看是否需要读图中文字。

---

### 3.4 `spatial`

定义：问题需要判断空间方位或物体相对关系。

关键词：

- `left` / `right`；
- `above` / `below`；
- `in front of` / `behind`；
- `next to`；
- `between`；
- `on top of` / `under`；
- `closest` / `farthest`。

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| What is to the left of the laptop? | cup | phone | spatial |
| Is the cat under the table? | yes | no | spatial |

常见原因：

- 左右视角混淆；
- 遮挡；
- 多对象关系复杂；
- 参照物识别错误。

---

### 3.5 `attribute`

定义：问题主要考察物体属性，包括颜色、材质、类别、状态、动作、大小等。

子类：

| subtype | 示例 |
|---|---|
| color | What color is the bus? |
| material | What is the table made of? |
| category | What animal is shown? |
| state | Is the door open? |
| action | What is the man doing? |
| size | Which object is larger? |

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| What color is the umbrella? | red | orange | attribute |
| What is the man holding? | racket | bat | attribute |

注意：如果错误来自常识而不是图像属性，标 `commonsense`。

---

### 3.6 `commonsense`

定义：问题需要图像内容之外的常识、用途、背景知识或推理。

常见问题：

- 根据物体判断场景或活动；
- 根据制服/工具判断职业；
- 根据食物/品牌/地标判断名称；
- 根据物理常识判断用途；
- OK-VQA 中大量外部知识问题。

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| What sport uses this type of racket? | tennis | badminton | commonsense |
| What country is this flag from? | Canada | USA | commonsense |

注意：如果错误主要是看错图中物体，例如把 tennis racket 看成 bat，优先标 `attribute`；如果物体识别对但知识关联错，标 `commonsense`。

---

### 3.7 `hallucination`

定义：模型编造了图中不存在的物体、关系、文字或事件。

表现：

- 问图中没有的东西却给出具体答案；
- 描述不存在的物体；
- 给出没有证据的场景推断；
- 把常见共现物体硬套到图片中。

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| What animal is on the sofa? | none | dog | hallucination |
| What logo is on the shirt? | no logo | Nike | hallucination |

注意：如果 GT 本身没有 `none` 类答案，需人工看图确认是否真是幻觉。

---

### 3.8 `ambiguous`

定义：问题或答案本身存在歧义，多个答案可能合理。

表现：

- 图片中有多个可能对象；
- 问题指代不清；
- GT answers 分歧很大；
- 模型答案与 GT 不同但看图可能合理；
- 图像质量太差无法判断。

例子：

| Question | GT | Prediction | error_type |
|---|---|---|---|
| What is the person holding? | phone | remote | ambiguous |
| What color is the object? | blue | gray | ambiguous |

报告中可以把 ambiguous 单独列出，不作为模型失败的强证据。

---

### 3.9 `other`

定义：无法归入以上类型，或自动脚本无法判断。

要求：

- `other` 不应过高；
- 如果 `other` > 30%，需要人工抽样检查并扩展 taxonomy 或修正规则。

---

## 4. 自动弱标注规则

`mine_failures.py` 可以使用以下启发式：

```python
if prediction_empty or too_long or has_explanation:
    error_type_auto = "answer_format"
elif question_lower.startswith("how many") or "number of" in question_lower:
    error_type_auto = "counting"
elif any(k in question_lower for k in ["sign", "text", "word", "read", "license", "menu", "screen", "label"]):
    error_type_auto = "ocr_text"
elif any(k in question_lower for k in ["left", "right", "above", "below", "behind", "front", "next to", "between", "under"]):
    error_type_auto = "spatial"
elif any(k in question_lower for k in ["color", "wearing", "holding", "made of", "type of", "kind of"]):
    error_type_auto = "attribute"
else:
    error_type_auto = "other"
```

对于 OK-VQA，可额外根据问题词和答案分布判断 commonsense，但自动 commonsense 标注容易误判，建议人工复核。

---

## 5. 人工复核表格式

建议导出 CSV：

| sample_id | image_path | question | gt_answers | prediction | error_type_auto | error_type_manual | note |
|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | counting | counting | object partially occluded |

人工复核规则：

- 每个主要实验至少抽样 50–100 条错误；
- 优先复核用于报告 case study 的样本；
- `error_type_manual` 只填 taxonomy 中定义的类型；
- 不确定填 `ambiguous` 或 `other`，并写 note。

---

## 6. Failure-driven sampling 中的使用方式

构造 failure-driven subset 时：

1. 先基于 baseline train-probe 错误生成 `failures_mined.jsonl`；
2. 统计各错误类型数量；
3. 对高价值错误类型提高采样权重；
4. 对 `answer_format` 限制比例，避免训练集只学格式；
5. 对 `ambiguous` 降权或排除；
6. 保证最终 subset 与 random subset 同规模；
7. 保存每条样本的 `source_error_type`。

推荐采样比例上限：

| error_type | 建议上限 |
|---|---:|
| answer_format | 20% |
| counting | 25% |
| ocr_text | 20% |
| spatial | 20% |
| commonsense | 35% |
| attribute | 30% |
| ambiguous | 5% |

这些比例不是硬性科学结论，只是为了避免 subset 过窄。

---

## 7. 报告中的表述建议

可以写：

- “我们将错误按 answer format、counting、OCR/text-rich、spatial、attribute、commonsense 等类别分析。”
- “failure-driven 数据主要来自 baseline 失败样本，并按错误类型重采样。”
- “错误类型标注先由启发式规则自动生成，再对 case study 与部分样本进行人工复核。”

不要写：

- “模型已经解决了 counting 问题”，除非有充足统计；
- “commonsense reasoning 显著提升”，除非在该类别上有稳定提升；
- “自动错误分类完全准确”。

---

## 8. 最终输出文件

错误分析阶段应至少产出：

```text
outputs/E*/errors.jsonl
outputs/E*/failures_mined.jsonl
outputs/E*/error_summary.csv
outputs/error_comparison.csv
outputs/error_comparison.md
outputs/case_studies.md
```

`error_summary.csv` 字段：

```text
experiment_id,error_type,num_errors,error_rate,num_samples,notes
```

`error_comparison.csv` 字段：

```text
error_type,E00_errors,E01_errors,E02_errors,E03_errors,E03_minus_E02
```


---


# File: CODING_AGENT_TASK_CARDS.md

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
data/processed/gui/val_small.jsonl
```

## 输出

```text
outputs/B01_gui_grounding_demo/predictions.jsonl
outputs/B01_gui_grounding_demo/metrics.json
```

## 实现要求

- 预测坐标点；
- 解析 `(x, y)`；
- 计算 point-in-bbox；
- 计算 center distance；
- 只做 demo，不加入主结果表。

## 自测命令

```bash
python scripts/evaluate_gui_grounding.py \
  --predictions outputs/B01_gui_grounding_demo/predictions.jsonl \
  --output outputs/B01_gui_grounding_demo/metrics.json
```

## 完成标准

- 小样本可运行；
- 坐标解析成功率有记录；
- 结果作为附录，不干扰主线。


---


# File: REPORT_CHECKLIST.md

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


---
