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
