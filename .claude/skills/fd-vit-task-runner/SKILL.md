---
name: fd-vit-task-runner
description: Use for any FD-VIT repository task that changes code, configs, data scripts, experiment scripts, evaluation, reports, or agent instructions. Guides coding agents to read the correct project docs before implementation, obey data/experiment contracts, avoid test leakage, run task-specific checks, and report outputs consistently.
---

# FD-VIT Task Runner

Use this skill as the entrypoint for FD-VIT coding work. The repository docs are the source of truth; this skill routes you to the right docs and enforces the workflow.

## Core Workflow

1. Classify the request into a Phase or Task card.
2. Read the minimal docs required by `references/doc-routing.md`.
3. Before editing, identify the task input files, output files, contract impact, leakage risk, and self-test command.
4. Implement only the requested task. Do not expand the experiment matrix.
5. Validate using the task card's self-test and any affected contract checks.
6. Report changed files, commands run, generated artifacts, test result, unresolved risks, and next step.

## Required References

- Read `references/doc-routing.md` before deciding which project docs to load.
- Read `references/task-execution-protocol.md` before implementation tasks.
- Read `references/critical-invariants.md` whenever touching data, prompts, inference, evaluation, training, outputs, or reports.
- Use `references/output-template.md` for final task summaries.

## Operating Rules

- Prefer `docs/README.md` for the current docs overview and reading order.
- Prefer `docs/CODING_AGENT_TASK_CARDS.md` for concrete task requirements.
- Prefer `docs/DATA_AND_FORMAT_CONTRACT.md` for schemas and validators.
- Prefer `docs/EXPERIMENT_PROTOCOL.md` for experiment IDs, seeds, splits, metrics, and output directories.
- Prefer `docs/ERROR_TAXONOMY.md` for failure mining and error analysis.
- Prefer `docs/REPORT_CHECKLIST.md` for report, slides, and final submission work.
- Use `docs/REQUIREMENTS_TRACEABILITY.md` as the scope gate for course coverage and optional directions.
- Treat `docs/references/project_requirements.md` as original course-source background, not permission to broaden the project.

If a required doc is missing, say which path is missing and use the nearest current replacement. Do not silently invent requirements.
