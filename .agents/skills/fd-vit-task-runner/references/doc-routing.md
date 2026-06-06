# FD-VIT Doc Routing

Read only the docs needed for the current task. Avoid loading the all-in-one backup unless a primary doc is missing.

## Always Start Here

- `docs/README.md`: current docs overview, document layers, reading order, and maintenance rules.
- `docs/FD_VIT_CODING_AGENT_GUIDE.md`: project phases, global rules, acceptance gates, risks.
- `docs/CODING_AGENT_TASK_CARDS.md`: concrete per-task inputs, outputs, implementation requirements, self-tests.

## Route by Work Type

| Work type | Required docs |
|---|---|
| repo skeleton, env checks, configs | `FD_VIT_CODING_AGENT_GUIDE.md`, `CODING_AGENT_TASK_CARDS.md` Task 0 |
| OK-VQA/VQA data conversion | Task 1, `DATA_AND_FORMAT_CONTRACT.md`, `EXPERIMENT_PROTOCOL.md` split rules |
| validators or schema changes | Task 2, `DATA_AND_FORMAT_CONTRACT.md` |
| prompt templates | Task 3, `DATA_AND_FORMAT_CONTRACT.md` prompt section |
| Qwen training format | Task 4, `DATA_AND_FORMAT_CONTRACT.md` Qwen format section |
| VQA normalization/evaluation | Task 5, `EXPERIMENT_PROTOCOL.md` metrics, `DATA_AND_FORMAT_CONTRACT.md` predictions/metrics |
| inference or baseline runs | Tasks 6-7, `EXPERIMENT_PROTOCOL.md`, `DATA_AND_FORMAT_CONTRACT.md` prediction schema |
| failure mining/error analysis | Tasks 8 and 13, `ERROR_TAXONOMY.md`, `DATA_AND_FORMAT_CONTRACT.md` error schema |
| train subset construction | Task 9, `EXPERIMENT_PROTOCOL.md` split/leakage rules, `ERROR_TAXONOMY.md` sampling guidance |
| LoRA/QLoRA training | Tasks 10-11, `EXPERIMENT_PROTOCOL.md`, `FD_VIT_CODING_AGENT_GUIDE.md` risks |
| result aggregation | Task 12, `EXPERIMENT_PROTOCOL.md`, `REPORT_CHECKLIST.md` |
| GUI grounding bonus | Task 14, `DATA_AND_FORMAT_CONTRACT.md` GUI section, `EXPERIMENT_PROTOCOL.md` GUI metrics |
| report/slides/submission | `REPORT_CHECKLIST.md`, `REQUIREMENTS_TRACEABILITY.md` |

## Scope Gate

Read both files below before changing model choice, task scope, course-coverage claims, bonus work, report conclusions, or the experiment matrix:

- `docs/REQUIREMENTS_TRACEABILITY.md`: maps broad course requirements to the narrowed FD-VIT execution scope.
- `docs/references/project_requirements.md`: Markdown source of the original course requirement.

Use traceability to reject scope creep. Do not treat broad options in the original requirement as permission to add mainline work.

## Background Only

- `docs/references/project_requirements.md`: source course requirement, not the execution plan.
- `docs/REQUIREMENTS_TRACEABILITY.md`: maps course requirements to FD-VIT scope; use it to reject scope creep.
- `docs/aigc/proj_layout/*.md`: rationale and feasibility background.
- `docs/FD_VIT_DOCS_ALL_IN_ONE.md`: merged reading copy only; edit independent docs first.

## Task Lookup

Use `rg -n "^# Task N" docs/CODING_AGENT_TASK_CARDS.md` to locate a specific task card. Read the whole card before implementing.
