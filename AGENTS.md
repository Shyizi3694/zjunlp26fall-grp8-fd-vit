<!-- Generated from .codex/skills/fd-vit-task-runner by scripts/agent_framework.py. Do not edit directly. -->
# AGENTS.md

## Repository Expectations

- This repo implements FD-VIT: Qwen3-VL + OK-VQA/VQA + baseline probing + LoRA random/failure-driven tuning.
- For any coding task, use the FD-VIT task runner skill if your agent supports skills.
- If skills are unavailable, read `.codex/skills/fd-vit-task-runner/SKILL.md` and follow its references manually.
- Repository docs are the source of truth; the skill only routes and enforces the workflow.
- Start with `docs/README.md` for the current docs overview and scope layers.

## Required Reading Flow

1. Classify the user request into a Phase or Task card.
2. Read `docs/FD_VIT_CODING_AGENT_GUIDE.md` for phase and global constraints.
3. Read `docs/CODING_AGENT_TASK_CARDS.md` for exact inputs, outputs, implementation requirements, self-tests, and done criteria.
4. Read only the task-specific docs routed by `.codex/skills/fd-vit-task-runner/references/doc-routing.md`.

## Non-Negotiable Constraints

- Do not expand the experiment matrix beyond E00-E03 unless the user explicitly asks for optional experiments.
- Do not treat Janus-Pro, image generation, or full GUI Agent as the mainline.
- Use `docs/REQUIREMENTS_TRACEABILITY.md` as the gate for course-coverage and scope decisions.
- Do not contaminate val/test data or train on final eval samples.
- Do not use raw string matching as the only VQA evaluation; follow `docs/DATA_AND_FORMAT_CONTRACT.md` and `docs/EXPERIMENT_PROTOCOL.md`.
- Always save per-sample `predictions.jsonl`; aggregate metrics alone are insufficient.
- Never invent experiment results or report numbers that are not traceable to output files.
- All scripts should expose CLI input/output paths, seed, logging, and limit/overwrite controls when applicable.

## Completion Report

Every task response should include changed files, commands run, generated artifacts, validation result, remaining risks, and the next practical step.
