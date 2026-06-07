#!/usr/bin/env python3
"""Preview rendered prompts for sampled VQA records."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from fdvit_prep_common import append_log, display_path, emit, repo_path, utc_now
from fdvit.prompts import PromptError, load_template_library, pick_template, render_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input JSONL/JSON sample file")
    parser.add_argument("--template_file", required=True, help="Prompt template json file")
    parser.add_argument("--output", required=True, help="Markdown preview output")
    parser.add_argument("--template_id", default=None, help="Use a fixed template_id")
    parser.add_argument("--templates_per_sample", type=int, default=2, help="How many templates to render per sample")
    parser.add_argument("--limit", type=int, default=0, help="Preview sample limit (0 means all)")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic template assignment")
    parser.add_argument("--log_file", default=None, help="Optional log file path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists")
    return parser.parse_args()


def read_json_like(path: str | Path) -> list[dict[str, Any]]:
    sample_path = repo_path(path)
    if not sample_path.exists():
        raise FileNotFoundError(f"input not found: {display_path(sample_path)}")
    raw = sample_path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    if raw[0] == "[":
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("input JSON must be list when parsed as JSON")
        return [x for x in payload if isinstance(x, dict)]

    records = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            continue
        records.append(obj)
    return records


def select_templates(templates: list[Any], args: argparse.Namespace) -> list[Any]:
    if args.template_id is not None:
        return [t for t in templates if t.template_id == args.template_id]
    selected_count = max(1, args.templates_per_sample)
    return templates[:selected_count]


def build_markdown(records: list[dict[str, Any]], templates: list[Any], *, args: argparse.Namespace) -> str:
    selected_records: list[dict[str, Any]] = records[: args.limit] if args.limit > 0 else records
    rng = random.Random(args.seed)
    selected_samples = selected_records
    if not selected_samples:
        return (
            f"# Prompt preview\n\nGenerated: {utc_now()}\n\nNo sample records found.\n"
        )

    if args.template_id is not None:
        selected_templates = select_templates(templates, args)[:1]
    else:
        rng.shuffle(selected_templates := templates.copy())
        selected_templates = selected_templates[: max(1, args.templates_per_sample)]

    lines: list[str] = [
        "# Prompt preview",
        "",
        f"- Generated: {utc_now()}",
        f"- Input: {display_path(repo_path(args.input))}",
        f"- Template file: {display_path(repo_path(args.template_file))}",
    ]
    if args.template_id is not None:
        lines.append(f"- Fixed template: {args.template_id}")
    lines.extend(["", "## Rendered prompts", ""])

    for row_idx, record in enumerate(selected_samples):
        question = str(record.get("question", ""))
        lines.append(f"### Sample {row_idx + 1}")
        lines.append("")
        lines.append(f"- sample_id: {record.get('sample_id', 'N/A')}")
        lines.append(f"- image_path: {record.get('image_path', 'N/A')}")
        lines.append(f"- question: {question}")
        lines.append("")
        lines.append("| template_id | rendered prompt |")
        lines.append("|---|---|")
        for template in selected_templates:
            if args.template_id is not None:
                template = template
            prompt = render_prompt(template, question=question)
            safe_prompt = prompt.replace("|", "\\|")
            lines.append(f"| {template.template_id} | `{safe_prompt}` |")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        templates = load_template_library(args.template_file, task="vqa", log_file=args.log_file)
        records = read_json_like(args.input)
        if args.template_id is not None:
            try:
                pick_template(templates, template_id=args.template_id)
            except PromptError as exc:
                raise ValueError(str(exc))

        rendered = build_markdown(records, templates, args=args)
        output_path = repo_path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {display_path(output_path)}")
        output_path.write_text(rendered, encoding="utf-8")
        emit(f"wrote {display_path(output_path)}", log_file=args.log_file)
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
