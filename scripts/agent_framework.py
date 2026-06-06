#!/usr/bin/env python3
"""Generate and validate FD-VIT coding-agent instruction adapters."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REL = Path(".agents/skills/fd-vit-task-runner")
CANONICAL = ROOT / CANONICAL_REL

SKILL_FILES = [
    Path("SKILL.md"),
    Path("references/doc-routing.md"),
    Path("references/task-execution-protocol.md"),
    Path("references/critical-invariants.md"),
    Path("references/output-template.md"),
]

MIRROR_RELS = [
    Path(".claude/skills/fd-vit-task-runner"),
    Path(".windsurf/skills/fd-vit-task-runner"),
]

ADAPTER_RELS = [
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path(".cursor/rules/fd-vit-agent.mdc"),
    Path(".github/copilot-instructions.md"),
]

GENERATED_HEADER = (
    "<!-- Generated from .agents/skills/fd-vit-task-runner by "
    "scripts/agent_framework.py. Do not edit directly. -->"
)

REQUIRED_DOCS = [
    Path("docs/README.md"),
    Path("docs/FD_VIT_CODING_AGENT_GUIDE.md"),
    Path("docs/CODING_AGENT_TASK_CARDS.md"),
    Path("docs/DATA_AND_FORMAT_CONTRACT.md"),
    Path("docs/EXPERIMENT_PROTOCOL.md"),
    Path("docs/ERROR_TAXONOMY.md"),
    Path("docs/REPORT_CHECKLIST.md"),
    Path("docs/REQUIREMENTS_TRACEABILITY.md"),
    Path("docs/references/project_requirements.md"),
]

OPTIONAL_DOC_GROUPS = [
    [Path("docs/FD_VIT_DOCS_ALL_IN_ONE.md"), Path("docs/FD_VIT_DOCS_ALL_IN_ONE_old.md")],
    [Path("docs/references/project_requirements.docx")],
]

KEY_SNIPPETS = [
    "DATA_AND_FORMAT_CONTRACT.md",
    "EXPERIMENT_PROTOCOL.md",
    "CODING_AGENT_TASK_CARDS.md",
    "ERROR_TAXONOMY.md",
    "README.md",
    "REQUIREMENTS_TRACEABILITY.md",
    "docs/references/project_requirements.md",
    "Do not expand the experiment matrix",
    "Do not use raw string matching",
    "Never invent experiment results",
]

LINE_BUDGETS = {
    Path("AGENTS.md"): 100,
    Path("CLAUDE.md"): 80,
    Path(".cursor/rules/fd-vit-agent.mdc"): 100,
    Path(".github/copilot-instructions.md"): 100,
}


def rel(path: Path) -> str:
    return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, *, force: bool = False) -> str:
    content = content.rstrip() + "\n"
    if path.exists():
        old = read_text(path)
        if old == content:
            return "unchanged"
        if not force and GENERATED_HEADER not in old:
            raise RuntimeError(
                f"Refusing to overwrite non-generated file: {rel(path.relative_to(ROOT))}. "
                "Use --force if you intentionally want to replace it."
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "updated"


def require_canonical() -> None:
    missing = [rel(CANONICAL_REL / file) for file in SKILL_FILES if not (CANONICAL / file).exists()]
    if missing:
        raise RuntimeError("Missing canonical skill files:\n" + "\n".join(f"- {item}" for item in missing))


def agents_md() -> str:
    return f"""{GENERATED_HEADER}
# AGENTS.md

## Repository Expectations

- This repo implements FD-VIT: Qwen3-VL + OK-VQA/VQA + baseline probing + LoRA random/failure-driven tuning.
- For any coding task, use the FD-VIT task runner skill if your agent supports skills.
- If skills are unavailable, read `{rel(CANONICAL_REL / "SKILL.md")}` and follow its references manually.
- Repository docs are the source of truth; the skill only routes and enforces the workflow.
- Start with `docs/README.md` for the current docs overview and scope layers.

## Required Reading Flow

1. Classify the user request into a Phase or Task card.
2. Read `docs/FD_VIT_CODING_AGENT_GUIDE.md` for phase and global constraints.
3. Read `docs/CODING_AGENT_TASK_CARDS.md` for exact inputs, outputs, implementation requirements, self-tests, and done criteria.
4. Read only the task-specific docs routed by `{rel(CANONICAL_REL / "references/doc-routing.md")}`.

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
"""


def claude_md() -> str:
    return f"""{GENERATED_HEADER}
@AGENTS.md

## Claude Code

- Use `/fd-vit-task-runner` for FD-VIT implementation, data, experiment, evaluation, and report tasks.
- The project skill mirror lives at `.claude/skills/fd-vit-task-runner/SKILL.md`.
- If the slash command is unavailable, read `{rel(CANONICAL_REL / "SKILL.md")}` and then follow the routed references.
- Keep `CLAUDE.local.md` for personal machine notes only; do not commit private paths, tokens, or cache locations.
"""


def cursor_rule() -> str:
    return f"""---
description: FD-VIT repository workflow. Use for coding tasks, scripts, configs, data conversion, inference, evaluation, training, report generation, or agent instruction updates.
globs: "**/*"
alwaysApply: true
---

{GENERATED_HEADER}

# FD-VIT Agent Rule

- Use `AGENTS.md` as the short repository entrypoint.
- Use `{rel(CANONICAL_REL / "SKILL.md")}` as the canonical skill source.
- Before coding, identify the Phase/Task card in `docs/CODING_AGENT_TASK_CARDS.md`.
- Read task-specific docs through `{rel(CANONICAL_REL / "references/doc-routing.md")}`.
- Obey `docs/DATA_AND_FORMAT_CONTRACT.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/ERROR_TAXONOMY.md` for schemas, metrics, splits, and errors.
- Do not expand the experiment matrix, contaminate val/test, use raw string matching as the only VQA metric, or invent results.
- Finish with changed files, commands, generated artifacts, validation, risks, and next step.
"""


def copilot_instructions() -> str:
    return f"""{GENERATED_HEADER}
# FD-VIT Copilot Instructions

Use `AGENTS.md` as the repository entrypoint and `{rel(CANONICAL_REL / "SKILL.md")}` as the canonical task skill.

For coding tasks:

- First identify the Phase and Task card in `docs/CODING_AGENT_TASK_CARDS.md`.
- Read `docs/FD_VIT_CODING_AGENT_GUIDE.md` for global rules.
- Route task-specific reading via `{rel(CANONICAL_REL / "references/doc-routing.md")}`.
- Follow `docs/DATA_AND_FORMAT_CONTRACT.md` for data, prediction, metrics, Qwen format, and validator schemas.
- Follow `docs/EXPERIMENT_PROTOCOL.md` for E00-E03, seeds, eval splits, generation config, metrics, and output directories.
- Follow `docs/ERROR_TAXONOMY.md` for failure mining and error analysis.
- Do not expand the experiment matrix, train on final eval data, use raw string matching as the only VQA metric, or invent experiment results.
- Report changed files, commands run, generated artifacts, validation result, risks, and next step.
"""


def adapters() -> dict[Path, str]:
    return {
        Path("AGENTS.md"): agents_md(),
        Path("CLAUDE.md"): claude_md(),
        Path(".cursor/rules/fd-vit-agent.mdc"): cursor_rule(),
        Path(".github/copilot-instructions.md"): copilot_instructions(),
    }


def mirror_skill() -> list[str]:
    require_canonical()
    actions: list[str] = []
    for mirror_rel in MIRROR_RELS:
        mirror = ROOT / mirror_rel
        mirror.mkdir(parents=True, exist_ok=True)
        for file_rel in SKILL_FILES:
            src = CANONICAL / file_rel
            dst = mirror / file_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            content = read_text(src)
            old = read_text(dst) if dst.exists() else None
            if old == content:
                actions.append(f"unchanged {rel(mirror_rel / file_rel)}")
                continue
            dst.write_text(content, encoding="utf-8")
            actions.append(f"updated {rel(mirror_rel / file_rel)}")
    return actions


def generate(*, force: bool = False) -> list[str]:
    require_canonical()
    actions = mirror_skill()
    for adapter_rel, content in adapters().items():
        status = write_text(ROOT / adapter_rel, content, force=force)
        actions.append(f"{status} {rel(adapter_rel)}")
    return actions


def check_generated_content() -> list[str]:
    errors: list[str] = []
    for adapter_rel, expected in adapters().items():
        path = ROOT / adapter_rel
        if not path.exists():
            errors.append(f"Missing adapter: {rel(adapter_rel)}")
            continue
        if read_text(path) != expected.rstrip() + "\n":
            errors.append(f"Adapter drifted: {rel(adapter_rel)}")
        budget = LINE_BUDGETS[adapter_rel]
        line_count = len(read_text(path).splitlines())
        if line_count > budget:
            errors.append(f"Adapter exceeds line budget ({line_count}>{budget}): {rel(adapter_rel)}")
    return errors


def check_mirrors() -> list[str]:
    errors: list[str] = []
    for mirror_rel in MIRROR_RELS:
        for file_rel in SKILL_FILES:
            src = CANONICAL / file_rel
            dst = ROOT / mirror_rel / file_rel
            if not dst.exists():
                errors.append(f"Missing mirror file: {rel(mirror_rel / file_rel)}")
                continue
            if read_text(src) != read_text(dst):
                errors.append(f"Mirror drifted: {rel(mirror_rel / file_rel)}")
    return errors


def check_docs() -> list[str]:
    errors: list[str] = []
    for doc in REQUIRED_DOCS:
        if not (ROOT / doc).exists():
            errors.append(f"Missing required doc: {rel(doc)}")
    for group in OPTIONAL_DOC_GROUPS:
        if not any((ROOT / doc).exists() for doc in group):
            errors.append("Missing optional doc group; expected one of: " + ", ".join(rel(doc) for doc in group))

    task_cards = ROOT / "docs/CODING_AGENT_TASK_CARDS.md"
    if task_cards.exists():
        text = read_text(task_cards)
        for index in range(15):
            if f"# Task {index}" not in text:
                errors.append(f"Missing Task {index} in docs/CODING_AGENT_TASK_CARDS.md")
    return errors


def check_snippets() -> list[str]:
    errors: list[str] = []
    files_to_scan = [CANONICAL / file for file in SKILL_FILES] + [ROOT / rel_path for rel_path in ADAPTER_RELS]
    combined = "\n".join(read_text(path) for path in files_to_scan if path.exists())
    for snippet in KEY_SNIPPETS:
        if snippet not in combined:
            errors.append(f"Missing key instruction snippet: {snippet}")
    return errors


def check() -> list[str]:
    require_canonical()
    errors: list[str] = []
    errors.extend(check_docs())
    errors.extend(check_mirrors())
    errors.extend(check_generated_content())
    errors.extend(check_snippets())
    return errors


def install_codex(*, force: bool = False) -> list[str]:
    require_canonical()
    target = Path.home() / ".agents/skills/fd-vit-task-runner"
    if target.exists() and not force:
        current = {file_rel: read_text(target / file_rel) for file_rel in SKILL_FILES if (target / file_rel).exists()}
        expected = {file_rel: read_text(CANONICAL / file_rel) for file_rel in SKILL_FILES}
        if current != expected:
            raise RuntimeError(f"Refusing to overwrite existing Codex user skill at {target}; use --force.")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(CANONICAL, target)
    return [f"installed {target}"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["generate", "check", "install-codex"])
    parser.add_argument("--force", action="store_true", help="overwrite existing generated targets")
    args = parser.parse_args(argv)

    try:
        if args.command == "generate":
            actions = generate(force=args.force)
            print("\n".join(actions))
            return 0
        if args.command == "check":
            errors = check()
            if errors:
                print("Agent framework check failed:", file=sys.stderr)
                print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
                return 1
            print("Agent framework check passed.")
            return 0
        if args.command == "install-codex":
            actions = install_codex(force=args.force)
            print("\n".join(actions))
            return 0
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
