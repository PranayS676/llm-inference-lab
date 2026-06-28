from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import typer
from rich import print

from runpod_inference_lab.common.paths import resolve_repo_path

app = typer.Typer(help="Summarize JSONL result files into CSV.")


def read_result_rows(input_file: str | Path) -> list[dict[str, Any]]:
    resolved = resolve_repo_path(input_file)
    rows: list[dict[str, Any]] = []
    if not resolved.exists():
        return rows
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def flatten_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": row.get("run_id"),
        "run_tag": row.get("run_tag"),
        "timestamp_utc": row.get("timestamp_utc"),
        "run_type": row.get("run_type"),
        "provider": row.get("provider"),
        "gpu_name": row.get("gpu_name"),
        "engine": row.get("engine"),
        "engine_version": row.get("engine_version"),
        "model": row.get("model"),
        "prompt_file": row.get("prompt_file"),
        "task_id": row.get("task_id"),
        "category": row.get("category"),
        "concurrency": row.get("concurrency"),
        "success": row.get("success"),
        "error": row.get("error"),
        "latency_ms": row.get("latency_ms"),
        "ttft_ms": row.get("ttft_ms"),
        "tokens_per_second_est": row.get("tokens_per_second_est"),
        "estimated_input_tokens": row.get("estimated_input_tokens"),
        "estimated_output_tokens": row.get("estimated_output_tokens"),
        "requests_per_second": row.get("requests_per_second"),
        "p50_latency_ms": row.get("p50_latency_ms"),
        "p95_latency_ms": row.get("p95_latency_ms"),
        "p99_latency_ms": row.get("p99_latency_ms"),
        "workflow_latency_ms": row.get("workflow_latency_ms"),
        "json_valid": row.get("json_valid"),
        "contains_expected": row.get("contains_expected"),
        "exact_match": row.get("exact_match"),
        "error_count": row.get("error_count"),
        "success_count": row.get("success_count"),
    }


def summarize_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(flatten_result(row) for row in rows)
    detail = df[df["latency_ms"].notna()].copy()
    if detail.empty:
        return df
    grouped = (
        detail.groupby(["model", "engine", "gpu_name", "category", "concurrency"], dropna=False)
        .agg(
            count=("run_id", "count"),
            success_rate=("success", "mean"),
            avg_latency_ms=("latency_ms", "mean"),
            p50_latency_ms=("latency_ms", "median"),
            avg_ttft_ms=("ttft_ms", "mean"),
            avg_tokens_per_second=("tokens_per_second_est", "mean"),
            avg_input_tokens=("estimated_input_tokens", "mean"),
            avg_output_tokens=("estimated_output_tokens", "mean"),
            json_valid_rate=("json_valid", "mean"),
            contains_expected_rate=("contains_expected", "mean"),
        )
        .reset_index()
    )
    return grouped


@app.command()
def main(
    input_file: Path = typer.Option(Path("results/concurrency_results.jsonl")),
    output_csv: Path = typer.Option(Path("results/summary.csv")),
) -> None:
    rows = read_result_rows(input_file)
    summary = summarize_dataframe(rows)
    resolved_output = resolve_repo_path(output_csv)
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(resolved_output, index=False)
    print(summary)
    print(f"Wrote {resolved_output}")


if __name__ == "__main__":
    app()
