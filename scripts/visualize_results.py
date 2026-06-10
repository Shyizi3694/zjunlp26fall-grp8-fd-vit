#!/usr/bin/env python3
"""Aggregate experiment outputs and generate a lightweight HTML dashboard."""

from __future__ import annotations

import argparse
import csv
import html
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))
if str(ROOT_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "scripts"))

from fdvit.evaluation import normalize_answer
from fdvit_prep_common import append_log, emit, repo_path
from mine_failures import detect_error_type

ERROR_TYPES = [
    "answer_format",
    "counting",
    "ocr_text",
    "spatial",
    "attribute",
    "commonsense",
    "hallucination",
    "ambiguous",
    "other",
]

PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp_dirs", nargs="+", required=True, help="Experiment output directories")
    parser.add_argument("--output_dir", required=True, help="Directory to store dashboard artifacts")
    parser.add_argument("--title", default="FD-VIT Results Dashboard", help="Dashboard title")
    parser.add_argument("--num_cases", type=int, default=8, help="Number of qualitative cases")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for case sampling")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    parser.add_argument("--log_file", default=None, help="Optional text log file")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            obj = json.loads(line)
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def infer_setting(exp_id: str) -> tuple[str, str, str]:
    lower = exp_id.lower()
    if "zero_shot" in lower:
        return "Zero-shot", "-", "-"
    if "prompt" in lower:
        return "Prompt-only", "-", "-"
    if "random" in lower:
        return "LoRA-random", "random", "8"
    if "failure" in lower:
        return "LoRA-failure", "failure", "8"
    return exp_id, "-", "-"


def infer_train_n(exp_id: str) -> int:
    import re

    match = re.search(r"_(\d+)k", exp_id.lower())
    if not match:
        return 0
    return int(match.group(1)) * 1000


def is_correct(row: dict[str, Any]) -> bool:
    pred = normalize_answer(str(row.get("prediction") or row.get("prediction_raw") or ""))
    answers = [normalize_answer(a) for a in row.get("answers", []) if isinstance(a, str)]
    return bool(answers and pred in answers)


def prediction_text(row: dict[str, Any]) -> str:
    return str(row.get("prediction") or row.get("prediction_raw") or "").strip()


def load_error_counts(exp_dir: Path) -> dict[str, int]:
    failure_path = exp_dir / "failures_mined.jsonl"
    error_path = exp_dir / "errors.jsonl"
    counts = {key: 0 for key in ERROR_TYPES}

    if failure_path.exists():
        for row in read_jsonl(failure_path):
            key = str(row.get("error_type_manual") or row.get("error_type_auto") or "other")
            counts[key] = counts.get(key, 0) + 1
        return counts

    if error_path.exists():
        for row in read_jsonl(error_path):
            key = detect_error_type(row)
            counts[key] = counts.get(key, 0) + 1
    return counts


def load_experiments(exp_dirs: list[str]) -> list[dict[str, Any]]:
    experiments = []
    for idx, raw_dir in enumerate(exp_dirs):
        exp_dir = repo_path(raw_dir)
        metrics_path = exp_dir / "metrics.json"
        predictions_path = exp_dir / "predictions.jsonl"
        if not metrics_path.exists():
            raise FileNotFoundError(f"missing metrics.json: {exp_dir}")
        metrics = read_json(metrics_path)
        predictions = read_jsonl(predictions_path) if predictions_path.exists() else []
        exp_id = str(metrics.get("experiment_id") or exp_dir.name)
        setting, sampling, lora_r = infer_setting(exp_id)
        experiments.append(
            {
                "index": idx,
                "exp_dir": exp_dir,
                "exp_id": exp_id,
                "setting": setting,
                "sampling": sampling,
                "lora_r": lora_r,
                "train_n": infer_train_n(exp_id),
                "metrics": metrics,
                "predictions": predictions,
                "pred_map": {str(row.get("sample_id")): row for row in predictions if row.get("sample_id")},
                "error_counts": load_error_counts(exp_dir),
                "color": PALETTE[idx % len(PALETTE)],
            }
        )
    return experiments


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_summary_rows(experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    zero_soft = next((float(exp["metrics"].get("acc_soft", 0.0)) for exp in experiments if str(exp["exp_id"]).startswith("E00")), 0.0)
    random_soft = next((float(exp["metrics"].get("acc_soft", 0.0)) for exp in experiments if str(exp["exp_id"]).startswith("E02")), 0.0)
    rows = []
    for exp in experiments:
        metrics = exp["metrics"]
        rows.append(
            {
                "exp_id": exp["exp_id"],
                "setting": exp["setting"],
                "train_n": exp["train_n"],
                "sampling": exp["sampling"],
                "lora_r": exp["lora_r"],
                "acc_any": float(metrics.get("acc_any", 0.0)),
                "acc_soft": float(metrics.get("acc_soft", 0.0)),
                "format_error_rate": float(metrics.get("format_error_rate", 0.0)),
                "num_samples": int(metrics.get("num_samples", 0)),
                "delta_acc_soft_vs_E00": float(metrics.get("acc_soft", 0.0)) - zero_soft,
                "delta_acc_soft_vs_E02": float(metrics.get("acc_soft", 0.0)) - random_soft,
                "metrics_path": str(exp["exp_dir"] / "metrics.json"),
            }
        )
    return rows


def build_error_rows(experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    e02 = next((exp for exp in experiments if str(exp["exp_id"]).startswith("E02")), None)
    e03 = next((exp for exp in experiments if str(exp["exp_id"]).startswith("E03")), None)
    for error_type in ERROR_TYPES:
        row: dict[str, Any] = {"error_type": error_type}
        for exp in experiments:
            row[f"{exp['exp_id']}_errors"] = int(exp["error_counts"].get(error_type, 0))
        if e02 is not None and e03 is not None:
            delta = int(e03["error_counts"].get(error_type, 0)) - int(e02["error_counts"].get(error_type, 0))
            row["E03_minus_E02"] = delta
            row["observation"] = "improved vs random" if delta < 0 else ("worse vs random" if delta > 0 else "unchanged vs random")
        rows.append(row)
    return rows


def build_case_rows(experiments: list[dict[str, Any]], *, num_cases: int, seed: int) -> list[dict[str, Any]]:
    if not experiments:
        return []
    common_ids: set[str] | None = None
    for exp in experiments:
        ids = set(exp["pred_map"].keys())
        common_ids = ids if common_ids is None else common_ids & ids
    if not common_ids:
        return []

    rng = random.Random(seed)
    ranked = []
    for sample_id in sorted(common_ids):
        rows = {exp["exp_id"]: exp["pred_map"][sample_id] for exp in experiments}
        correctness = {exp_id: is_correct(row) for exp_id, row in rows.items()}
        e00_ok = next((ok for exp_id, ok in correctness.items() if exp_id.startswith("E00")), False)
        e02_ok = next((ok for exp_id, ok in correctness.items() if exp_id.startswith("E02")), False)
        e03_ok = next((ok for exp_id, ok in correctness.items() if exp_id.startswith("E03")), False)
        if e03_ok and not e02_ok:
            priority = 0
            note = "failure-driven fixes an error that random LoRA misses"
        elif e03_ok and not e00_ok:
            priority = 1
            note = "fine-tuning fixes a zero-shot error"
        elif not e03_ok:
            priority = 2
            note = "failure-driven still fails; useful for limitation analysis"
        else:
            priority = 3
            note = "all stronger systems succeed"
        any_row = next(iter(rows.values()))
        ranked.append(
            {
                "priority": priority,
                "shuffle": rng.random(),
                "sample_id": sample_id,
                "image_path": str(any_row.get("image_path", "")),
                "question": str(any_row.get("question", "")),
                "gt_answers": "; ".join([str(a) for a in any_row.get("answers", [])[:10]]),
                "error_type": detect_error_type(any_row),
                "note": note,
                "rows": rows,
                "correctness": correctness,
            }
        )
    ranked.sort(key=lambda row: (row["priority"], row["shuffle"]))
    return ranked[: max(0, num_cases)]


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def svg_bar_chart(labels: list[str], values: list[float], colors: list[str], *, title: str, width: int = 760, height: int = 280, percent: bool = True) -> str:
    left = 56
    bottom = 36
    top = 30
    right = 20
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_value = max(values) if values else 1.0
    max_value = max(max_value, 1e-6)
    bar_w = max(24, int(plot_w / max(1, len(values) * 2)))
    gap = bar_w
    bars = []
    for idx, (label, value, color) in enumerate(zip(labels, values, colors)):
        x = left + idx * (bar_w + gap) + gap // 2
        h = int((value / max_value) * (plot_h - 10))
        y = top + plot_h - h
        shown = fmt_pct(value) if percent else f"{value:.0f}"
        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" rx="6" fill="{color}" opacity="0.9"></rect>'
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 6}" text-anchor="middle" font-size="11" fill="#243447">{html.escape(shown)}</text>'
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 14}" text-anchor="middle" font-size="11" fill="#4b5563">{html.escape(label)}</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="auto" role="img" aria-label="{html.escape(title)}">'
        f'<text x="{left}" y="18" font-size="15" font-weight="700" fill="#111827">{html.escape(title)}</text>'
        f'<line x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}" stroke="#9ca3af" />'
        f'{"".join(bars)}'
        f'</svg>'
    )


def svg_grouped_error_chart(experiments: list[dict[str, Any]], *, width: int = 980, height: int = 360) -> str:
    left = 80
    bottom = 70
    top = 32
    right = 20
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_value = max((exp["error_counts"].get(err, 0) for exp in experiments for err in ERROR_TYPES), default=1)
    group_w = plot_w / max(1, len(ERROR_TYPES))
    bar_w = max(8.0, group_w / max(2, len(experiments) + 1))
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="auto" role="img" aria-label="Error Type Comparison">',
        f'<text x="{left}" y="18" font-size="15" font-weight="700" fill="#111827">Error Type Comparison</text>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}" stroke="#9ca3af" />',
    ]
    for idx, error_type in enumerate(ERROR_TYPES):
        gx = left + idx * group_w
        for exp_idx, exp in enumerate(experiments):
            value = int(exp["error_counts"].get(error_type, 0))
            h = 0 if max_value <= 0 else (value / max_value) * (plot_h - 10)
            x = gx + 8 + exp_idx * bar_w
            y = top + plot_h - h
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 2:.1f}" height="{h:.1f}" rx="3" fill="{exp["color"]}" opacity="0.9"></rect>'
            )
        parts.append(
            f'<text x="{gx + group_w / 2:.1f}" y="{height - 18}" text-anchor="middle" font-size="10" fill="#4b5563">{html.escape(error_type)}</text>'
        )
    legend_y = height - 48
    for idx, exp in enumerate(experiments):
        lx = left + idx * 180
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="12" height="12" rx="3" fill="{exp["color"]}"></rect>')
        parts.append(f'<text x="{lx + 18}" y="{legend_y + 10}" font-size="11" fill="#374151">{html.escape(exp["exp_id"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def render_html(title: str, summary_rows: list[dict[str, Any]], error_rows: list[dict[str, Any]], case_rows: list[dict[str, Any]], experiments: list[dict[str, Any]]) -> str:
    labels = [row["exp_id"] for row in summary_rows]
    colors = [next(exp["color"] for exp in experiments if exp["exp_id"] == row["exp_id"]) for row in summary_rows]
    acc_soft_svg = svg_bar_chart(labels, [float(row["acc_soft"]) for row in summary_rows], colors, title="Soft Accuracy")
    acc_any_svg = svg_bar_chart(labels, [float(row["acc_any"]) for row in summary_rows], colors, title="Any-Match Accuracy")
    fmt_svg = svg_bar_chart(labels, [float(row["format_error_rate"]) for row in summary_rows], colors, title="Format Error Rate")
    error_svg = svg_grouped_error_chart(experiments)

    metric_cards = []
    for row in summary_rows:
        metric_cards.append(
            "<div class='card metric-card'>"
            f"<div class='eyebrow'>{html.escape(str(row['exp_id']))}</div>"
            f"<h3>{html.escape(str(row['setting']))}</h3>"
            f"<p>acc_soft <strong>{float(row['acc_soft']):.4f}</strong></p>"
            f"<p>acc_any <strong>{float(row['acc_any']):.4f}</strong></p>"
            f"<p>format_error_rate <strong>{float(row['format_error_rate']):.4f}</strong></p>"
            "</div>"
        )

    summary_table_rows = []
    for row in summary_rows:
        summary_table_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['exp_id']))}</td>"
            f"<td>{html.escape(str(row['setting']))}</td>"
            f"<td>{row['train_n']}</td>"
            f"<td>{html.escape(str(row['sampling']))}</td>"
            f"<td>{html.escape(str(row['lora_r']))}</td>"
            f"<td>{float(row['acc_any']):.4f}</td>"
            f"<td>{float(row['acc_soft']):.4f}</td>"
            f"<td>{float(row['format_error_rate']):.4f}</td>"
            f"<td>{float(row['delta_acc_soft_vs_E00']):+.4f}</td>"
            f"<td>{float(row['delta_acc_soft_vs_E02']):+.4f}</td>"
            "</tr>"
        )

    error_headers = ["error_type"] + [f"{row['exp_id']}_errors" for row in summary_rows]
    if error_rows and "E03_minus_E02" in error_rows[0]:
        error_headers.extend(["E03_minus_E02", "observation"])
    error_table_rows = []
    for row in error_rows:
        cells = [html.escape(str(row.get(header, ""))) for header in error_headers]
        error_table_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")

    case_headers = ["sample_id", "question", "gt_answers"] + [row["exp_id"] for row in summary_rows] + ["error_type", "note"]
    case_table_rows = []
    for row in case_rows:
        cells = [
            html.escape(str(row["sample_id"])),
            html.escape(str(row["question"])),
            html.escape(str(row["gt_answers"])),
        ]
        for exp in summary_rows:
            exp_id = str(exp["exp_id"])
            pred = prediction_text(row["rows"][exp_id])
            if row["correctness"].get(exp_id):
                pred = f"{pred} (correct)"
            cells.append(html.escape(pred))
        cells.extend([html.escape(str(row["error_type"])), html.escape(str(row["note"]))])
        case_table_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f7fb;
      --panel: #ffffff;
      --text: #111827;
      --muted: #6b7280;
      --line: #dbe1ea;
      --accent: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background: linear-gradient(180deg, #eef6ff 0%, var(--bg) 220px);
      color: var(--text);
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    .hero {{
      background: linear-gradient(135deg, #ffffff 0%, #f4fbf9 100%);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 28px;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    }}
    .hero p {{ color: var(--muted); max-width: 860px; }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .metrics {{
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin-top: 20px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }}
    .metric-card .eyebrow {{
      font-size: 12px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 10px;
      font-weight: 700;
    }}
    .section {{
      margin-top: 22px;
    }}
    .charts {{
      grid-template-columns: 1fr;
    }}
    .chart-card {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      background: var(--panel);
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f9fafb;
      position: sticky;
      top: 0;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel);
    }}
    .muted {{
      color: var(--muted);
      font-size: 14px;
    }}
    code {{
      background: #eef2f7;
      padding: 2px 6px;
      border-radius: 6px;
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      <p>This dashboard aggregates experiment metrics, error breakdowns, and qualitative examples from the selected output directories. It is designed as a report companion for quickly comparing E00–E03.</p>
      <p class="muted">Experiments: {", ".join(html.escape(str(row["exp_id"])) for row in summary_rows)}</p>
    </section>

    <section class="section">
      <div class="grid metrics">
        {"".join(metric_cards)}
      </div>
    </section>

    <section class="section">
      <h2>Metric Charts</h2>
      <div class="grid charts">
        <div class="card chart-card">{acc_soft_svg}</div>
        <div class="card chart-card">{acc_any_svg}</div>
        <div class="card chart-card">{fmt_svg}</div>
        <div class="card chart-card">{error_svg}</div>
      </div>
    </section>

    <section class="section">
      <h2>Main Results</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Exp</th>
              <th>Setting</th>
              <th>Train n</th>
              <th>Sampling</th>
              <th>LoRA r</th>
              <th>acc_any</th>
              <th>acc_soft</th>
              <th>format_error_rate</th>
              <th>Δ vs E00</th>
              <th>Δ vs E02</th>
            </tr>
          </thead>
          <tbody>
            {"".join(summary_table_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>Error Breakdown</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>{"".join(f"<th>{html.escape(header)}</th>" for header in error_headers)}</tr>
          </thead>
          <tbody>
            {"".join(error_table_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>Qualitative Cases</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>{"".join(f"<th>{html.escape(header)}</th>" for header in case_headers)}</tr>
          </thead>
          <tbody>
            {"".join(case_table_rows) if case_table_rows else "<tr><td colspan='99'>No common prediction rows found.</td></tr>"}
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    try:
        experiments = load_experiments(args.exp_dirs)
        summary_rows = build_summary_rows(experiments)
        error_rows = build_error_rows(experiments)
        case_rows = build_case_rows(experiments, num_cases=args.num_cases, seed=args.seed)

        output_dir = repo_path(args.output_dir)
        if output_dir.exists() and not args.overwrite:
            raise FileExistsError(f"refusing to overwrite existing output dir: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

        write_csv(
            output_dir / "summary_metrics.csv",
            [
                "exp_id",
                "setting",
                "train_n",
                "sampling",
                "lora_r",
                "acc_any",
                "acc_soft",
                "format_error_rate",
                "num_samples",
                "delta_acc_soft_vs_E00",
                "delta_acc_soft_vs_E02",
                "metrics_path",
            ],
            summary_rows,
            overwrite=True,
        )
        error_fieldnames = ["error_type"] + [f"{exp['exp_id']}_errors" for exp in experiments]
        if error_rows and "E03_minus_E02" in error_rows[0]:
            error_fieldnames.extend(["E03_minus_E02", "observation"])
        write_csv(output_dir / "error_breakdown.csv", error_fieldnames, error_rows, overwrite=True)

        case_csv_rows = []
        for row in case_rows:
            payload = {
                "sample_id": row["sample_id"],
                "image_path": row["image_path"],
                "question": row["question"],
                "gt_answers": row["gt_answers"],
                "error_type": row["error_type"],
                "note": row["note"],
            }
            for exp in experiments:
                payload[exp["exp_id"]] = prediction_text(row["rows"][exp["exp_id"]])
            case_csv_rows.append(payload)
        case_fieldnames = ["sample_id", "image_path", "question", "gt_answers"] + [exp["exp_id"] for exp in experiments] + ["error_type", "note"]
        write_csv(output_dir / "case_studies.csv", case_fieldnames, case_csv_rows, overwrite=True)

        dashboard_path = output_dir / "dashboard.html"
        dashboard_path.write_text(render_html(args.title, summary_rows, error_rows, case_rows, experiments), encoding="utf-8")

        manifest = {
            "exp_dirs": [str(repo_path(exp_dir)) for exp_dir in args.exp_dirs],
            "summary_csv": str(output_dir / "summary_metrics.csv"),
            "error_csv": str(output_dir / "error_breakdown.csv"),
            "case_csv": str(output_dir / "case_studies.csv"),
            "dashboard_html": str(dashboard_path),
        }
        (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        emit(f"wrote dashboard artifacts to {output_dir}", log_file=args.log_file)
        append_log(args.log_file, json.dumps({"output_dir": str(output_dir), "num_experiments": len(experiments), "num_cases": len(case_rows)}))
        return 0
    except Exception as exc:  # noqa: BLE001
        emit(f"ERROR: {exc}")
        append_log(args.log_file, f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
