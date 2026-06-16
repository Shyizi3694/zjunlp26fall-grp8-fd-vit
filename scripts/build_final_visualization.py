#!/usr/bin/env python3
"""Build a compact final dashboard across FD-VIT experiments."""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


VQA_METRICS = [
    ("main_val1k", "E00_zero_shot_basic", "Zero-shot", "none", 0, ROOT / "outputs/E00_zero_shot_basic/metrics.json"),
    ("main_val1k", "E01_prompt_strict", "Prompt-only", "none", 0, ROOT / "outputs/E01_prompt_strict/metrics.json"),
    ("main_val1k", "E02_lora_random_2k_r8", "LoRA random", "random", 2000, ROOT / "outputs/E02_lora_random_2k_r8/metrics.json"),
    ("main_val1k", "E03_lora_failure_2k_r8", "LoRA failure", "failure", 2000, ROOT / "outputs/E03_lora_failure_2k_r8/metrics.json"),
    ("main_val1k", "E04_lora_random_5k_r8_val1k", "LoRA random", "random", 5000, ROOT / "outputs/lora_5k_ablation_val1k/E04_lora_random_5k_r8_val1k/metrics.json"),
    ("main_val1k", "E05_lora_failure_5k_r8_val1k", "LoRA failure", "failure", 5000, ROOT / "outputs/lora_5k_ablation_val1k/E05_lora_failure_5k_r8_val1k/metrics.json"),
    ("prompt_ablation", "E06_prompt_template_001_val1k", "Prompt template 001", "none", 0, ROOT / "outputs/prompt_ablation_val1k/E06_prompt_template_001_val1k/metrics.json"),
    ("prompt_ablation", "E06_prompt_template_002_val1k", "Prompt template 002", "none", 0, ROOT / "outputs/prompt_ablation_val1k/E06_prompt_template_002_val1k/metrics.json"),
    ("prompt_ablation", "E06_prompt_template_003_val1k", "Prompt template 003", "none", 0, ROOT / "outputs/prompt_ablation_val1k/E06_prompt_template_003_val1k/metrics.json"),
    ("prompt_ablation", "E06_prompt_template_004_val1k", "Prompt template 004", "none", 0, ROOT / "outputs/prompt_ablation_val1k/E06_prompt_template_004_val1k/metrics.json"),
    ("prompt_ablation", "E06_prompt_template_005_val1k", "Prompt template 005", "none", 0, ROOT / "outputs/prompt_ablation_val1k/E06_prompt_template_005_val1k/metrics.json"),
    ("prompt_ablation", "E06_prompt_template_006_val1k", "Prompt template 006", "none", 0, ROOT / "outputs/prompt_ablation_val1k/E06_prompt_template_006_val1k/metrics.json"),
    ("val5k", "E00_zero_shot_basic_val5k", "Zero-shot", "none", 0, ROOT / "outputs/val5k_main/E00_zero_shot_basic_val5k/metrics.json"),
    ("val5k", "E01_prompt_strict_val5k", "Prompt-only", "none", 0, ROOT / "outputs/val5k_main/E01_prompt_strict_val5k/metrics.json"),
    ("val5k", "E02_lora_random_2k_r8_val5k", "LoRA random", "random", 2000, ROOT / "outputs/val5k_main/E02_lora_random_2k_r8_val5k/metrics.json"),
    ("val5k", "E03_lora_failure_2k_r8_val5k", "LoRA failure", "failure", 2000, ROOT / "outputs/val5k_main/E03_lora_failure_2k_r8_val5k/metrics.json"),
    ("val5k", "E04_lora_random_5k_r8_val5k", "LoRA random", "random", 5000, ROOT / "outputs/lora_5k_ablation_val5k/E04_lora_random_5k_r8_val5k/metrics.json"),
    ("val5k", "E05_lora_failure_5k_r8_val5k", "LoRA failure", "failure", 5000, ROOT / "outputs/lora_5k_ablation_val5k/E05_lora_failure_5k_r8_val5k/metrics.json"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output_dir", default="outputs/final_visualization")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def collect_vqa_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for eval_set, exp_id, setting, sampling, train_n, path in VQA_METRICS:
        metrics = read_json(path)
        if metrics is None:
            continue
        rows.append(
            {
                "group": eval_set,
                "exp_id": exp_id,
                "setting": setting,
                "sampling": sampling,
                "train_n": train_n,
                "num_samples": metrics.get("num_samples", ""),
                "acc_any": float(metrics.get("acc_any", 0.0)),
                "acc_soft": float(metrics.get("acc_soft", 0.0)),
                "format_error_rate": float(metrics.get("format_error_rate", 0.0)),
                "metrics_path": path.relative_to(ROOT).as_posix(),
            }
        )
    return rows


def collect_gui_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for label, path in [
        ("B01 small GUI demo", ROOT / "outputs/B01_gui_grounding_demo/metrics.json"),
        ("B02 larger GUI demo", ROOT / "outputs/B02_gui_grounding_larger/metrics.json"),
    ]:
        metrics = read_json(path)
        if metrics is None:
            continue
        rows.append(
            {
                "exp_id": label,
                "num_samples": metrics.get("num_samples", ""),
                "parse_success_rate": float(metrics.get("parse_success_rate", 0.0)),
                "point_in_bbox_acc": float(metrics.get("point_in_bbox_acc", 0.0)),
                "center_distance_norm": metrics.get("center_distance_norm", ""),
                "metrics_path": path.relative_to(ROOT).as_posix(),
            }
        )
    return rows


def bar_svg(rows: list[dict[str, Any]], value_key: str, label_key: str, title: str) -> str:
    if not rows:
        return "<p>No data.</p>"
    width = 920
    row_h = 28
    left = 260
    max_w = 560
    height = 52 + row_h * len(rows)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="22" class="chart-title">{html.escape(title)}</text>',
    ]
    for idx, row in enumerate(rows):
        y = 46 + idx * row_h
        value = float(row.get(value_key, 0.0))
        label = str(row.get(label_key, ""))
        color = "#2f6f73" if row.get("sampling") == "failure" else "#586f9f"
        if row.get("sampling") == "random":
            color = "#a05a2c"
        if "GUI" in label:
            color = "#6b5ca5"
        parts.append(f'<text x="0" y="{y + 16}" class="bar-label">{html.escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{max_w}" height="18" rx="3" class="bar-bg" />')
        parts.append(f'<rect x="{left}" y="{y}" width="{max(1, value * max_w):.1f}" height="18" rx="3" fill="{color}" />')
        parts.append(f'<text x="{left + max_w + 12}" y="{y + 14}" class="bar-value">{value:.4f}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def table_html(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "<p>No data.</p>"
    head = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
    body = []
    for row in rows:
        cells = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                text = f"{value:.4f}"
            else:
                text = str(value)
            cells.append(f"<td>{html.escape(text)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_html(vqa_rows: list[dict[str, Any]], gui_rows: list[dict[str, Any]], sig_rows: list[dict[str, str]]) -> str:
    val1k_rows = [row for row in vqa_rows if row["group"] == "main_val1k"]
    prompt_rows = [row for row in vqa_rows if row["group"] == "prompt_ablation"]
    val5k_rows = [row for row in vqa_rows if row["group"] == "val5k"]
    gui_chart_rows = [{**row, "label": row["exp_id"]} for row in gui_rows]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>FD-VIT Final Experiment Dashboard</title>
  <style>
    :root {{ color-scheme: light; --ink: #1f2933; --muted: #64707d; --line: #d9dee5; --panel: #f7f8fa; }}
    body {{ margin: 0; font-family: Inter, Arial, sans-serif; color: var(--ink); background: #ffffff; }}
    header {{ padding: 28px 34px 18px; border-bottom: 1px solid var(--line); }}
    h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 20px; }}
    p {{ color: var(--muted); line-height: 1.5; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 18px 28px 42px; }}
    section {{ padding: 8px 0 16px; border-bottom: 1px solid var(--line); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 9px; text-align: left; }}
    th {{ background: var(--panel); font-weight: 650; }}
    svg {{ width: 100%; height: auto; margin: 4px 0 10px; }}
    .chart-title {{ font-size: 18px; font-weight: 700; fill: var(--ink); }}
    .bar-label {{ font-size: 12px; fill: var(--ink); }}
    .bar-value {{ font-size: 12px; fill: var(--muted); }}
    .bar-bg {{ fill: #e8ecf1; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 18px; }}
  </style>
</head>
<body>
<header>
  <h1>FD-VIT Final Experiment Dashboard</h1>
  <p>Unified view of OK-VQA mainline, val_5k extension, LoRA 5k ablation, paired significance, and GUI grounding bonus.</p>
</header>
<main>
  <section>
    <h2>OK-VQA val_1k Accuracy</h2>
    {bar_svg(val1k_rows, "acc_soft", "exp_id", "Soft accuracy on val_1k")}
    {table_html(val1k_rows, ["exp_id", "setting", "sampling", "train_n", "num_samples", "acc_any", "acc_soft", "format_error_rate"])}
  </section>
  <section>
    <h2>Prompt Template Ablation</h2>
    {bar_svg(prompt_rows, "acc_soft", "exp_id", "Soft accuracy by prompt template on val_1k")}
    {table_html(prompt_rows, ["exp_id", "setting", "num_samples", "acc_any", "acc_soft", "format_error_rate"])}
  </section>
  <section>
    <h2>OK-VQA val_5k Accuracy</h2>
    {bar_svg(val5k_rows, "acc_soft", "exp_id", "Soft accuracy on val_5k")}
    {table_html(val5k_rows, ["exp_id", "setting", "sampling", "train_n", "num_samples", "acc_any", "acc_soft", "format_error_rate"])}
  </section>
  <section>
    <h2>Paired Significance</h2>
    {table_html(sig_rows, ["comparison", "metric", "n", "baseline_mean", "treatment_mean", "diff_treatment_minus_baseline", "bootstrap_ci_low", "bootstrap_ci_high", "paired_randomization_p", "wins", "losses", "ties"])}
  </section>
  <section>
    <h2>GUI Grounding Bonus</h2>
    {bar_svg(gui_chart_rows, "point_in_bbox_acc", "label", "Point-in-bbox accuracy")}
    {table_html(gui_rows, ["exp_id", "num_samples", "parse_success_rate", "point_in_bbox_acc", "center_distance_norm"])}
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    vqa_rows = collect_vqa_rows()
    gui_rows = collect_gui_rows()
    sig_rows = read_csv(ROOT / "outputs/significance/paired_significance.csv")

    write_csv(
        output_dir / "all_vqa_results.csv",
        vqa_rows,
        ["group", "exp_id", "setting", "sampling", "train_n", "num_samples", "acc_any", "acc_soft", "format_error_rate", "metrics_path"],
        overwrite=args.overwrite,
    )
    write_csv(
        output_dir / "gui_results.csv",
        gui_rows,
        ["exp_id", "num_samples", "parse_success_rate", "point_in_bbox_acc", "center_distance_norm", "metrics_path"],
        overwrite=args.overwrite,
    )
    html_text = build_html(vqa_rows, gui_rows, sig_rows)
    html_path = output_dir / "dashboard.html"
    if html_path.exists() and not args.overwrite:
        raise FileExistsError(f"Refusing to overwrite: {html_path}")
    html_path.write_text(html_text, encoding="utf-8")
    print(f"wrote final visualization to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
