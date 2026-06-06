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
