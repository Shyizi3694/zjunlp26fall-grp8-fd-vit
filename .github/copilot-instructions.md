<!-- Generated from .codex/skills/fd-vit-task-runner by scripts/agent_framework.py. Do not edit directly. -->
# FD-VIT Copilot Instructions

Use `AGENTS.md` as the repository entrypoint and `.codex/skills/fd-vit-task-runner/SKILL.md` as the canonical task skill.

For coding tasks:

- First identify the Phase and Task card in `docs/CODING_AGENT_TASK_CARDS.md`.
- Read `docs/FD_VIT_CODING_AGENT_GUIDE.md` for global rules.
- Route task-specific reading via `.codex/skills/fd-vit-task-runner/references/doc-routing.md`.
- Follow `docs/DATA_AND_FORMAT_CONTRACT.md` for data, prediction, metrics, Qwen format, and validator schemas.
- Follow `docs/EXPERIMENT_PROTOCOL.md` for E00-E03, seeds, eval splits, generation config, metrics, and output directories.
- Follow `docs/ERROR_TAXONOMY.md` for failure mining and error analysis.
- Do not expand the experiment matrix, train on final eval data, use raw string matching as the only VQA metric, or invent experiment results.
- Report changed files, commands run, generated artifacts, validation result, risks, and next step.
