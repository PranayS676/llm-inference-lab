from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import typer
from rich import print

from runpod_inference_lab.common.paths import resolve_repo_path
from runpod_inference_lab.reports.summarize_results import flatten_result, summarize_dataframe

app = typer.Typer(help="Generate a markdown recommendation report from result JSONL files.")


def read_all_results(results_dir: str | Path) -> list[dict[str, Any]]:
    resolved = resolve_repo_path(results_dir)
    rows: list[dict[str, Any]] = []
    if not resolved.exists():
        return rows
    for path in sorted(resolved.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    row["_source_file"] = str(path)
                    rows.append(row)
    return rows


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows available yet._"
    return df.head(max_rows).to_markdown(index=False)


def build_report(rows: list[dict[str, Any]]) -> str:
    flat = pd.DataFrame(flatten_result(row) for row in rows) if rows else pd.DataFrame()
    summary = summarize_dataframe(rows)
    total_rows = len(rows)
    successful = int(flat["success"].sum()) if not flat.empty and "success" in flat else 0
    failed = total_rows - successful if total_rows else 0

    lines = [
        "# LLM Inference Lab Report",
        "",
        "## Overview",
        "",
        f"- Total result rows: {total_rows}",
        f"- Successful rows: {successful}",
        f"- Failed rows: {failed}",
        "",
        "## Grouped Summary",
        "",
        dataframe_to_markdown(summary),
        "",
        "## Learning Notes",
        "",
        "- Compare rows only when model, engine, GPU, prompt file, and server config match.",
        "- Treat client-side token counts as estimates until engine-native metrics are added.",
        "- If p95 latency rises sharply with concurrency, inspect queueing and KV cache pressure.",
        "- If quality improves with a larger model, compare that gain against latency and cost.",
        "",
        "## Recommendation Template",
        "",
        "Fill this in after real RunPod runs:",
        "",
        "- Best simple/routing model:",
        "- Best balanced agent model:",
        "- Best coding/reasoning model:",
        "- Best long-context GPU/model:",
        "- Configuration to avoid:",
    ]
    return "\n".join(lines) + "\n"


@app.command()
def main(
    results_dir: Path = typer.Option(Path("results")),
    output_file: Path = typer.Option(Path("reports/hardware_recommendation.md")),
) -> None:
    rows = read_all_results(results_dir)
    report = build_report(rows)
    resolved = resolve_repo_path(output_file)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(report, encoding="utf-8")
    print(f"Wrote {resolved}")


if __name__ == "__main__":
    app()
