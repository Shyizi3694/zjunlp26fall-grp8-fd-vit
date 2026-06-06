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
