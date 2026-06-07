"""Prompt template utilities for FD-VIT.

This module enforces the repo contract for prompt templates:
- unique template_id
- VQA task templates must include `{question}` and `<image>`
- short-answer style instruction should be present
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fdvit_prep_common import append_log, repo_path

PROMPT_CONSTRAINT_KEYWORDS = (
    "short phrase",
    "short answer",
    "answer:",
    "only",
    "do not explain",
)


class PromptError(RuntimeError):
    """Raised for invalid prompt template content."""


def _read_json(path: str | Path) -> Any:
    template_path = repo_path(path)
    with template_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(frozen=True)
class PromptTemplate:
    template_id: str
    task: str
    text: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"template_id": self.template_id, "task": self.task, "text": self.text}
        if self.note is not None:
            payload["note"] = self.note
        return payload


def validate_template(template: dict[str, Any]) -> PromptTemplate:
    if not isinstance(template, dict):
        raise PromptError("template must be an object")
    template_id = template.get("template_id")
    task = template.get("task")
    text = template.get("text")
    if not isinstance(template_id, str) or not template_id.strip():
        raise PromptError("template_id is required and must be non-empty string")
    if task not in {"vqa", "caption", "gui_grounding"}:
        raise PromptError(f"{template_id}: unsupported task '{task}'")
    if not isinstance(text, str) or not text.strip():
        raise PromptError(f"{template_id}: text is required")
    if "<image>" not in text:
        raise PromptError(f"{template_id}: text must contain <image>")
    if task == "vqa":
        if "{question}" not in text:
            raise PromptError(f"{template_id}: vqa template must contain {{question}}")
        if not _has_short_answer_constraint(text):
            raise PromptError(f"{template_id}: vqa template missing short-answer constraint")
    return PromptTemplate(template_id=template_id.strip(), task=task, text=text.strip(), note=template.get("note"))


def _has_short_answer_constraint(text: str) -> bool:
    normalized = text.lower()
    return any(keyword in normalized for keyword in PROMPT_CONSTRAINT_KEYWORDS)


def validate_template_library(templates: list[dict[str, Any]], *, task: str | None = None) -> list[PromptTemplate]:
    items = []
    seen: set[str] = set()
    for template in templates:
        validated = validate_template(template)
        if validated.template_id in seen:
            raise PromptError(f"duplicate template_id: {validated.template_id}")
        seen.add(validated.template_id)
        if task is None or validated.task == task:
            items.append(validated)
    return items


def load_template_library(path: str | Path, *, task: str | None = None, log_file: str | None = None) -> list[PromptTemplate]:
    payload = _read_json(path)
    if not isinstance(payload, list):
        raise PromptError(f"template file must be a list: {path}")
    templates = validate_template_library(payload, task=task)
    append_log(
        log_file,
        f"loaded {len(templates)} templates from {repo_path(path)} (task filter: {task or 'all'})",
    )
    return templates


def pick_template_by_id(templates: list[PromptTemplate], template_id: str) -> PromptTemplate:
    for template in templates:
        if template.template_id == template_id:
            return template
    raise PromptError(f"template_id not found: {template_id}")


def _stable_template_index(index: int, total: int, seed: int) -> int:
    if total <= 0:
        raise ValueError("total must be positive")
    return (index + seed) % total


def pick_template(
    templates: list[PromptTemplate],
    *,
    template_id: str | None = None,
    seed: int = 42,
    position: int = 0,
) -> PromptTemplate:
    if template_id is not None:
        return pick_template_by_id(templates, template_id)
    idx = _stable_template_index(position, len(templates), seed)
    return templates[idx]


def render_prompt(template: PromptTemplate, *, question: str) -> str:
    try:
        return template.text.format(question=question or "")
    except KeyError as exc:
        raise PromptError(f"{template.template_id} missing placeholder: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 - fallback with explicit CLI-friendly error.
        raise PromptError(f"failed to render template {template.template_id}: {exc}") from exc


def detect_short_answer_violation(answer: str) -> bool:
    text = (answer or "").strip().lower()
    too_short = len(text) > 80
    too_verbose = any(flag in text for flag in (" because ", " because", "i think", "the answer is", "it is"))
    newline_or_punc = "\n" in text or text.count(".") > 1
    return too_short or too_verbose or newline_or_punc
