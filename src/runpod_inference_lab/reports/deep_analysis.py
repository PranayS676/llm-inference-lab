# ruff: noqa: E501

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
import typer
from rich import print

from runpod_inference_lab.common.paths import repo_root, resolve_repo_path
from runpod_inference_lab.reports.generate_markdown_report import read_all_results
from runpod_inference_lab.reports.summarize_results import flatten_result

app = typer.Typer(help="Generate deep benchmark analysis artifacts and an HTML dashboard.")

OFFICIAL_TAG_SUFFIX = "-official"
CONCURRENCY_SUMMARY_TYPE = "concurrency_summary"
CONCURRENCY_DETAIL_TYPE = "concurrency_detail"
DETAIL_RUN_TYPES = {
    "single_prompt",
    "batch",
    "concurrency_detail",
    "agent_sequential_detail",
    "agent_concurrent_detail",
}
AGENT_SUMMARY_TYPES = {"agent_sequential_summary", "agent_concurrent_summary"}
AGENT_DETAIL_TYPES = {"agent_sequential_detail", "agent_concurrent_detail"}
GPU_SNAPSHOT_RUN_TYPES = {CONCURRENCY_SUMMARY_TYPE, *AGENT_SUMMARY_TYPES}


def is_official_run_tag(run_tag: Any) -> bool:
    return isinstance(run_tag, str) and run_tag.endswith(OFFICIAL_TAG_SUFFIX)


def model_label(model: Any) -> str:
    if not isinstance(model, str):
        return "unknown"
    if model.startswith("Qwen/Qwen3-"):
        return model.replace("Qwen/Qwen3-", "Qwen3 ")
    return model


def model_size_b(model: Any) -> float:
    label = model_label(model)
    if label.startswith("Qwen3 ") and label.endswith("B"):
        try:
            return float(label.removeprefix("Qwen3 ").removesuffix("B"))
        except ValueError:
            return math.nan
    return math.nan


def engine_label(engine: Any) -> str:
    if engine == "vllm":
        return "vLLM"
    if engine == "sglang":
        return "SGLang"
    return str(engine or "unknown")


def series_label(row: dict[str, Any]) -> str:
    return f"{model_label(row.get('model'))} / {engine_label(row.get('engine'))}"


def workflow_mode(run_type: Any) -> str:
    if run_type in {"agent_sequential_summary", "agent_sequential_detail"}:
        return "sequential"
    if run_type in {"agent_concurrent_summary", "agent_concurrent_detail"}:
        return "concurrent"
    return "unknown"


def read_experiment_rows(experiment_dir: str | Path) -> list[dict[str, Any]]:
    resolved = resolve_repo_path(experiment_dir)
    return read_all_results(resolved / "results")


def flatten_analysis_row(row: dict[str, Any]) -> dict[str, Any]:
    flat = flatten_result(row)
    flat.update(
        {
            "agent": row.get("agent"),
            "agent_count": row.get("agent_count"),
            "agent_sequence": row.get("agent_sequence"),
            "gpu_before": row.get("gpu_before"),
            "gpu_after": row.get("gpu_after"),
            "is_official": is_official_run_tag(row.get("run_tag")),
            "max_model_len": row.get("max_model_len"),
            "max_tokens": row.get("max_tokens"),
            "model_label": model_label(row.get("model")),
            "model_size_b": model_size_b(row.get("model")),
            "series_label": series_label(row),
            "suite_latency_ms": row.get("suite_latency_ms"),
            "total_tasks": row.get("total_tasks"),
            "workflow_mode": workflow_mode(row.get("run_type")),
        }
    )
    return flat


def build_results_dataframe(rows: list[dict[str, Any]], official_only: bool = True) -> pd.DataFrame:
    df = pd.DataFrame(flatten_analysis_row(row) for row in rows) if rows else pd.DataFrame()
    if df.empty:
        return df
    if official_only:
        df = df[df["is_official"]].copy()
    numeric_columns = [
        "agent_count",
        "agent_sequence",
        "concurrency",
        "error_count",
        "estimated_input_tokens",
        "estimated_output_tokens",
        "latency_ms",
        "max_model_len",
        "max_tokens",
        "model_size_b",
        "p50_latency_ms",
        "p95_latency_ms",
        "p99_latency_ms",
        "requests_per_second",
        "success_count",
        "suite_latency_ms",
        "tokens_per_second_est",
        "total_tasks",
        "ttft_ms",
        "workflow_latency_ms",
    ]
    for column in numeric_columns:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def _p95(values: pd.Series) -> float:
    return float(values.dropna().quantile(0.95))


def _p50(values: pd.Series) -> float:
    return float(values.dropna().median())


def _failure_count(values: pd.Series) -> int:
    return int((values != True).sum())  # noqa: E712


def build_concurrency_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    keys = [
        "run_tag",
        "model",
        "model_label",
        "model_size_b",
        "engine",
        "series_label",
        "gpu_name",
        "concurrency",
    ]
    detail = df[df["run_type"] == CONCURRENCY_DETAIL_TYPE].copy()
    summary = df[df["run_type"] == CONCURRENCY_SUMMARY_TYPE].copy()

    detail_metrics = pd.DataFrame()
    if not detail.empty:
        detail_metrics = (
            detail.groupby(keys, dropna=False)
            .agg(
                detail_count=("run_id", "count"),
                detail_success_rate=("success", "mean"),
                detail_error_count=("success", _failure_count),
                avg_latency_ms=("latency_ms", "mean"),
                detail_p50_latency_ms=("latency_ms", _p50),
                detail_p95_latency_ms=("latency_ms", _p95),
                avg_ttft_ms=("ttft_ms", "mean"),
                p50_ttft_ms=("ttft_ms", _p50),
                p95_ttft_ms=("ttft_ms", _p95),
                avg_tokens_per_second=("tokens_per_second_est", "mean"),
                p50_tokens_per_second=("tokens_per_second_est", _p50),
                avg_input_tokens=("estimated_input_tokens", "mean"),
                avg_output_tokens=("estimated_output_tokens", "mean"),
                json_valid_rate=("json_valid", "mean"),
                contains_expected_rate=("contains_expected", "mean"),
            )
            .reset_index()
        )

    summary_columns = keys + [
        "p50_latency_ms",
        "p95_latency_ms",
        "p99_latency_ms",
        "requests_per_second",
        "suite_latency_ms",
        "success_count",
        "error_count",
        "total_tasks",
    ]
    summary_metrics = summary[[column for column in summary_columns if column in summary]].copy()

    if summary_metrics.empty:
        metrics = detail_metrics
    elif detail_metrics.empty:
        metrics = summary_metrics
    else:
        metrics = summary_metrics.merge(detail_metrics, on=keys, how="left")

    if metrics.empty:
        return metrics

    metrics["p50_latency_ms"] = metrics.get("p50_latency_ms", pd.Series(dtype=float)).fillna(
        metrics.get("detail_p50_latency_ms", pd.Series(dtype=float))
    )
    metrics["p95_latency_ms"] = metrics.get("p95_latency_ms", pd.Series(dtype=float)).fillna(
        metrics.get("detail_p95_latency_ms", pd.Series(dtype=float))
    )
    if "total_tasks" not in metrics:
        metrics["total_tasks"] = metrics.get("detail_count", 0)
    metrics["total_tasks"] = metrics["total_tasks"].fillna(metrics.get("detail_count", 0))
    if "error_count" not in metrics:
        metrics["error_count"] = metrics.get("detail_error_count", 0)
    metrics["error_count"] = metrics["error_count"].fillna(metrics.get("detail_error_count", 0))
    if "success_count" not in metrics:
        metrics["success_count"] = metrics["total_tasks"] - metrics["error_count"]
    metrics["success_count"] = metrics["success_count"].fillna(
        metrics["total_tasks"] - metrics["error_count"]
    )
    metrics["success_rate"] = metrics["success_count"] / metrics["total_tasks"].replace(0, pd.NA)
    metrics["error_rate"] = metrics["error_count"] / metrics["total_tasks"].replace(0, pd.NA)
    metrics["latency_per_output_token_ms"] = metrics["avg_latency_ms"] / metrics[
        "avg_output_tokens"
    ].replace(0, pd.NA)

    return metrics.sort_values(
        ["model_size_b", "engine", "concurrency"], na_position="last"
    ).reset_index(drop=True)


def build_scaling_metrics(concurrency_metrics: pd.DataFrame) -> pd.DataFrame:
    if concurrency_metrics.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for _, group in concurrency_metrics.groupby(["run_tag", "model", "engine"], dropna=False):
        base = group[group["concurrency"] == 1]
        if base.empty:
            continue
        base_rps = float(base.iloc[0].get("requests_per_second") or 0)
        if base_rps <= 0:
            continue
        for _, row in group.iterrows():
            concurrency = float(row.get("concurrency") or 0)
            rps = float(row.get("requests_per_second") or 0)
            observed_scaling = rps / base_rps
            ideal_scaling = concurrency if concurrency > 0 else math.nan
            rows.append(
                {
                    "run_tag": row.get("run_tag"),
                    "model": row.get("model"),
                    "model_label": row.get("model_label"),
                    "engine": row.get("engine"),
                    "series_label": row.get("series_label"),
                    "concurrency": concurrency,
                    "requests_per_second": rps,
                    "observed_rps_scaling_vs_c1": observed_scaling,
                    "ideal_rps_scaling_vs_c1": ideal_scaling,
                    "scaling_efficiency_pct": (observed_scaling / ideal_scaling * 100)
                    if ideal_scaling
                    else math.nan,
                }
            )
    return pd.DataFrame(rows)


def build_workload_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    detail = df[df["run_type"].isin(DETAIL_RUN_TYPES) & df["latency_ms"].notna()].copy()
    if detail.empty:
        return pd.DataFrame()
    grouped = (
        detail.groupby(
            [
                "run_tag",
                "model",
                "model_label",
                "model_size_b",
                "engine",
                "series_label",
                "gpu_name",
                "run_type",
                "category",
            ],
            dropna=False,
        )
        .agg(
            request_count=("run_id", "count"),
            success_rate=("success", "mean"),
            error_count=("success", _failure_count),
            avg_latency_ms=("latency_ms", "mean"),
            p50_latency_ms=("latency_ms", _p50),
            p95_latency_ms=("latency_ms", _p95),
            avg_ttft_ms=("ttft_ms", "mean"),
            avg_tokens_per_second=("tokens_per_second_est", "mean"),
            avg_input_tokens=("estimated_input_tokens", "mean"),
            avg_output_tokens=("estimated_output_tokens", "mean"),
            json_valid_rate=("json_valid", "mean"),
            contains_expected_rate=("contains_expected", "mean"),
        )
        .reset_index()
    )
    return grouped.sort_values(
        ["model_size_b", "engine", "run_type", "category"], na_position="last"
    ).reset_index(drop=True)


def build_agent_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    summary = df[df["run_type"].isin(AGENT_SUMMARY_TYPES)].copy()
    if summary.empty:
        return pd.DataFrame()
    grouped = (
        summary.groupby(
            [
                "run_tag",
                "model",
                "model_label",
                "model_size_b",
                "engine",
                "series_label",
                "gpu_name",
                "workflow_mode",
            ],
            dropna=False,
        )
        .agg(
            workflow_count=("run_id", "count"),
            success_rate=("success", "mean"),
            avg_workflow_latency_ms=("workflow_latency_ms", "mean"),
            p50_workflow_latency_ms=("workflow_latency_ms", _p50),
            p95_workflow_latency_ms=("workflow_latency_ms", _p95),
            min_workflow_latency_ms=("workflow_latency_ms", "min"),
            max_workflow_latency_ms=("workflow_latency_ms", "max"),
            avg_agent_count=("agent_count", "mean"),
        )
        .reset_index()
    )
    grouped["avg_workflow_latency_s"] = grouped["avg_workflow_latency_ms"] / 1000
    return grouped.sort_values(
        ["workflow_mode", "model_size_b", "engine"], na_position="last"
    ).reset_index(drop=True)


def build_agent_step_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    detail = df[df["run_type"].isin(AGENT_DETAIL_TYPES) & df["latency_ms"].notna()].copy()
    if detail.empty:
        return pd.DataFrame()
    grouped = (
        detail.groupby(
            [
                "run_tag",
                "model",
                "model_label",
                "model_size_b",
                "engine",
                "series_label",
                "gpu_name",
                "workflow_mode",
                "agent",
            ],
            dropna=False,
        )
        .agg(
            step_count=("run_id", "count"),
            success_rate=("success", "mean"),
            avg_step_latency_ms=("latency_ms", "mean"),
            p50_step_latency_ms=("latency_ms", _p50),
            p95_step_latency_ms=("latency_ms", _p95),
            avg_tokens_per_second=("tokens_per_second_est", "mean"),
        )
        .reset_index()
    )
    return grouped.sort_values(
        ["workflow_mode", "model_size_b", "engine", "agent"], na_position="last"
    ).reset_index(drop=True)


def build_gpu_snapshots(rows: list[dict[str, Any]], official_only: bool = True) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in rows:
        if official_only and not is_official_run_tag(row.get("run_tag")):
            continue
        if row.get("run_type") not in GPU_SNAPSHOT_RUN_TYPES:
            continue
        for phase in ("gpu_before", "gpu_after"):
            snapshot = row.get(phase)
            if not isinstance(snapshot, dict):
                continue
            for gpu in snapshot.get("gpus", []):
                total_mb = gpu.get("memory_total_mb")
                used_mb = gpu.get("memory_used_mb")
                records.append(
                    {
                        "run_tag": row.get("run_tag"),
                        "run_type": row.get("run_type"),
                        "model": row.get("model"),
                        "model_label": model_label(row.get("model")),
                        "model_size_b": model_size_b(row.get("model")),
                        "engine": row.get("engine"),
                        "series_label": series_label(row),
                        "gpu_name": row.get("gpu_name"),
                        "detected_gpu_name": snapshot.get("detected_gpu_name"),
                        "concurrency": row.get("concurrency"),
                        "snapshot_phase": phase.removeprefix("gpu_"),
                        "gpu_index": gpu.get("index"),
                        "gpu_memory_used_mb": used_mb,
                        "gpu_memory_total_mb": total_mb,
                        "gpu_memory_used_pct": (used_mb / total_mb * 100)
                        if used_mb and total_mb
                        else math.nan,
                        "gpu_util_percent": gpu.get("gpu_util_percent"),
                        "gpu_power_watts": gpu.get("power_watts"),
                    }
                )
    df = pd.DataFrame(records)
    if df.empty:
        return df
    numeric_columns = [
        "concurrency",
        "gpu_index",
        "gpu_memory_used_mb",
        "gpu_memory_total_mb",
        "gpu_memory_used_pct",
        "gpu_util_percent",
        "gpu_power_watts",
        "model_size_b",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.sort_values(
        ["model_size_b", "engine", "run_type", "concurrency", "snapshot_phase"], na_position="last"
    )


def build_engine_comparison(concurrency_metrics: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "model",
        "model_label",
        "concurrency",
        "vllm_requests_per_second",
        "sglang_requests_per_second",
        "sglang_vs_vllm_rps_ratio",
        "vllm_p95_latency_ms",
        "sglang_p95_latency_ms",
        "sglang_vs_vllm_p95_ratio",
        "vllm_avg_ttft_ms",
        "sglang_avg_ttft_ms",
        "sglang_vs_vllm_ttft_ratio",
    ]
    if concurrency_metrics.empty:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, Any]] = []
    for (model, concurrency), group in concurrency_metrics.groupby(
        ["model", "concurrency"], dropna=False
    ):
        by_engine = {row["engine"]: row for _, row in group.iterrows()}
        if "vllm" not in by_engine or "sglang" not in by_engine:
            continue
        vllm = by_engine["vllm"]
        sglang = by_engine["sglang"]
        vllm_rps = float(vllm.get("requests_per_second") or 0)
        sglang_rps = float(sglang.get("requests_per_second") or 0)
        vllm_p95 = float(vllm.get("p95_latency_ms") or 0)
        sglang_p95 = float(sglang.get("p95_latency_ms") or 0)
        vllm_ttft = float(vllm.get("avg_ttft_ms") or 0)
        sglang_ttft = float(sglang.get("avg_ttft_ms") or 0)
        rows.append(
            {
                "model": model,
                "model_label": model_label(model),
                "concurrency": concurrency,
                "vllm_requests_per_second": vllm_rps,
                "sglang_requests_per_second": sglang_rps,
                "sglang_vs_vllm_rps_ratio": sglang_rps / vllm_rps if vllm_rps else math.nan,
                "vllm_p95_latency_ms": vllm_p95,
                "sglang_p95_latency_ms": sglang_p95,
                "sglang_vs_vllm_p95_ratio": sglang_p95 / vllm_p95 if vllm_p95 else math.nan,
                "vllm_avg_ttft_ms": vllm_ttft,
                "sglang_avg_ttft_ms": sglang_ttft,
                "sglang_vs_vllm_ttft_ratio": sglang_ttft / vllm_ttft if vllm_ttft else math.nan,
            }
        )
    if not rows:
        return pd.DataFrame(columns=columns)
    return (
        pd.DataFrame(rows, columns=columns)
        .sort_values(["model_label", "concurrency"])
        .reset_index(drop=True)
    )


def _clean_for_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean_for_json(item) for item in value]
    if value is pd.NA:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if hasattr(value, "item"):
        try:
            return _clean_for_json(value.item())
        except ValueError:
            return None
    return value


def dataframe_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return [_clean_for_json(record) for record in df.to_dict(orient="records")]


def dataframe_to_markdown(
    df: pd.DataFrame, columns: list[str] | None = None, max_rows: int = 20
) -> str:
    if df.empty:
        return "_No rows available._"
    table = df[columns].copy() if columns else df.copy()
    for column in table.select_dtypes(include="number").columns:
        table[column] = table[column].map(
            lambda value: round(float(value), 3) if pd.notna(value) else value
        )
    return table.head(max_rows).to_markdown(index=False)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root()).as_posix()
    except ValueError:
        return path.as_posix()


def build_headline_findings(
    concurrency_metrics: pd.DataFrame,
    agent_metrics: pd.DataFrame,
    engine_comparison: pd.DataFrame,
) -> list[str]:
    findings: list[str] = []
    if not concurrency_metrics.empty:
        peak = concurrency_metrics.sort_values("requests_per_second", ascending=False).iloc[0]
        findings.append(
            "Highest request throughput was "
            f"{peak['series_label']} at concurrency {int(peak['concurrency'])}: "
            f"{peak['requests_per_second']:.2f} requests/sec."
        )
        lowest_p95 = concurrency_metrics.sort_values("p95_latency_ms", ascending=True).iloc[0]
        findings.append(
            "Lowest concurrency p95 latency was "
            f"{lowest_p95['series_label']} at concurrency {int(lowest_p95['concurrency'])}: "
            f"{lowest_p95['p95_latency_ms']:.1f} ms."
        )
        no_errors = int(concurrency_metrics["error_count"].fillna(0).sum())
        findings.append(
            f"Concurrency runs recorded {no_errors} errors across official benchmark summaries."
        )
    if not agent_metrics.empty:
        fastest_agent = agent_metrics.sort_values("avg_workflow_latency_ms", ascending=True).iloc[0]
        findings.append(
            "Fastest average agent workflow was "
            f"{fastest_agent['series_label']} in {fastest_agent['workflow_mode']} mode: "
            f"{fastest_agent['avg_workflow_latency_s']:.2f} seconds."
        )
    if not engine_comparison.empty:
        common = engine_comparison[engine_comparison["concurrency"] == 10]
        if not common.empty:
            avg_rps_ratio = common["sglang_vs_vllm_rps_ratio"].mean()
            avg_p95_ratio = common["sglang_vs_vllm_p95_ratio"].mean()
            findings.append(
                "For common 4B/14B models at concurrency 10, SGLang averaged "
                f"{avg_rps_ratio:.2f}x vLLM request throughput and "
                f"{avg_p95_ratio:.2f}x vLLM p95 latency."
            )
    return findings


def build_analysis_report(
    *,
    experiment_dir: Path,
    official_row_count: int,
    excluded_row_count: int,
    concurrency_metrics: pd.DataFrame,
    scaling_metrics: pd.DataFrame,
    workload_metrics: pd.DataFrame,
    agent_metrics: pd.DataFrame,
    agent_step_metrics: pd.DataFrame,
    gpu_snapshots: pd.DataFrame,
    engine_comparison: pd.DataFrame,
) -> str:
    findings = build_headline_findings(concurrency_metrics, agent_metrics, engine_comparison)
    error_total = (
        int(concurrency_metrics["error_count"].fillna(0).sum())
        if not concurrency_metrics.empty
        else 0
    )
    workflow_error_total = 0
    if not agent_metrics.empty:
        workflow_error_total = int(
            (agent_metrics["workflow_count"] * (1 - agent_metrics["success_rate"])).fillna(0).sum()
        )

    concurrency_columns = [
        "series_label",
        "concurrency",
        "p50_latency_ms",
        "p95_latency_ms",
        "requests_per_second",
        "avg_tokens_per_second",
        "avg_ttft_ms",
        "error_rate",
    ]
    agent_columns = [
        "series_label",
        "workflow_mode",
        "workflow_count",
        "avg_workflow_latency_s",
        "p95_workflow_latency_ms",
        "success_rate",
    ]
    engine_columns = [
        "model_label",
        "concurrency",
        "sglang_vs_vllm_rps_ratio",
        "sglang_vs_vllm_p95_ratio",
        "sglang_vs_vllm_ttft_ratio",
    ]
    gpu_columns = [
        "series_label",
        "run_type",
        "concurrency",
        "snapshot_phase",
        "gpu_memory_used_mb",
        "gpu_memory_used_pct",
        "gpu_util_percent",
        "gpu_power_watts",
    ]
    scaling_columns = [
        "series_label",
        "concurrency",
        "requests_per_second",
        "observed_rps_scaling_vs_c1",
        "scaling_efficiency_pct",
    ]

    lines = [
        "# A100 Official Benchmark Deep Analysis",
        "",
        "## Scope",
        "",
        f"- Experiment directory: `{display_path(experiment_dir)}`",
        f"- Official result rows analyzed: {official_row_count}",
        f"- Non-official rows excluded: {excluded_row_count}",
        "- Included run tags: tags ending in `-official` only.",
        "- Analysis mode: performance-only; no RunPod cost modeling.",
        "",
        "## Headline Findings",
        "",
    ]
    lines.extend(f"- {finding}" for finding in findings)
    lines.extend(
        [
            f"- Official concurrency summary errors: {error_total}",
            f"- Official agent workflow summary errors: {workflow_error_total}",
            "",
            "## How To Read This Report",
            "",
            "- `p50 latency` is the median request latency. It describes the typical request.",
            "- `p95 latency` is the tail-latency pressure point. It matters more for interactive agents.",
            "- `TTFT` is time to first token. Lower TTFT makes the model feel more responsive.",
            "- `requests/sec` measures server throughput for a concurrency level.",
            "- `tokens/sec` is estimated from client-side token counts, so treat it as directional.",
            "- Agent workflow latency is the end-to-end multi-agent task latency, not just one model call.",
            "- GPU memory snapshots are point-in-time `nvidia-smi` values around summary runs, not continuous telemetry.",
            "",
            "## Concurrency Summary",
            "",
            dataframe_to_markdown(concurrency_metrics, concurrency_columns, max_rows=40),
            "",
            "## Scaling Efficiency",
            "",
            "Scaling efficiency compares observed requests/sec against the ideal linear increase from concurrency 1.",
            "",
            dataframe_to_markdown(scaling_metrics, scaling_columns, max_rows=40),
            "",
            "## Engine Comparison",
            "",
            "This section compares vLLM and SGLang only where both engines were run for the same model size.",
            "Ratios above `1.0` mean SGLang is higher than vLLM for that metric.",
            "",
            dataframe_to_markdown(engine_comparison, engine_columns, max_rows=20),
            "",
            "## Agent Workflow Summary",
            "",
            dataframe_to_markdown(agent_metrics, agent_columns, max_rows=30),
            "",
            "## Agent Step Summary",
            "",
            dataframe_to_markdown(
                agent_step_metrics,
                [
                    "series_label",
                    "workflow_mode",
                    "agent",
                    "avg_step_latency_ms",
                    "p95_step_latency_ms",
                    "avg_tokens_per_second",
                ],
                max_rows=40,
            ),
            "",
            "## Workload Category Summary",
            "",
            dataframe_to_markdown(
                workload_metrics,
                [
                    "series_label",
                    "run_type",
                    "category",
                    "request_count",
                    "p50_latency_ms",
                    "p95_latency_ms",
                    "avg_ttft_ms",
                    "avg_tokens_per_second",
                    "success_rate",
                ],
                max_rows=50,
            ),
            "",
            "## GPU Memory Snapshots",
            "",
            dataframe_to_markdown(gpu_snapshots, gpu_columns, max_rows=40),
            "",
            "## Interpretation",
            "",
            "- Use p95 latency, not average latency, when deciding what feels safe for interactive agent loops.",
            "- Use requests/sec at concurrency 5 and 10 when estimating whether one GPU can serve multiple agents.",
            "- Treat 4B models as routing and fast utility candidates, 14B as balanced candidates, and 32B as a quality candidate that needs tighter latency review.",
            "- Treat SGLang-vs-vLLM conclusions as model-size-specific. The comparison is strongest for 4B and 14B because both engines were run there.",
            "- The current GPU memory data is enough to confirm model residency and rough pressure, but future experiments should add periodic memory/utilization sampling.",
            "",
            "## Generated Artifacts",
            "",
            "- `dashboard.html`: interactive Plotly dashboard.",
            "- `summary_metrics.csv`: per-run official row counts.",
            "- `concurrency_metrics.csv`: latency, throughput, TTFT, tokens/sec, and error-rate summary.",
            "- `scaling_metrics.csv`: throughput scaling efficiency by concurrency.",
            "- `engine_comparison.csv`: SGLang vs vLLM ratios for common models.",
            "- `agent_metrics.csv`: sequential and concurrent workflow latency.",
            "- `agent_step_metrics.csv`: per-agent step latency.",
            "- `workload_metrics.csv`: workload/category breakdown.",
            "- `gpu_snapshots.csv`: structured GPU memory/utilization snapshots extracted from result rows.",
            "",
            "## Future Benchmark Improvements",
            "",
            "- Add continuous GPU telemetry sampling during each benchmark run.",
            "- Add engine-native token and scheduler metrics instead of client-estimated token counts only.",
            "- Add quality-scored prompts for model-size tradeoff analysis.",
            "- Repeat each official run multiple times to estimate variance.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_dashboard_html(
    *,
    experiment_name: str,
    official_row_count: int,
    excluded_row_count: int,
    concurrency_metrics: pd.DataFrame,
    scaling_metrics: pd.DataFrame,
    workload_metrics: pd.DataFrame,
    agent_metrics: pd.DataFrame,
    agent_step_metrics: pd.DataFrame,
    gpu_snapshots: pd.DataFrame,
    engine_comparison: pd.DataFrame,
) -> str:
    payload = {
        "experimentName": experiment_name,
        "officialRowCount": official_row_count,
        "excludedRowCount": excluded_row_count,
        "concurrency": dataframe_records(concurrency_metrics),
        "scaling": dataframe_records(scaling_metrics),
        "workloads": dataframe_records(workload_metrics),
        "agents": dataframe_records(agent_metrics),
        "agentSteps": dataframe_records(agent_step_metrics),
        "gpu": dataframe_records(gpu_snapshots),
        "engineComparison": dataframe_records(engine_comparison),
    }
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>A100 Official Benchmark Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #1f2937;
      --muted: #64748b;
      --border: #d7dce5;
      --accent: #1f7a8c;
      --accent-2: #8a5a44;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      padding: 28px 36px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); margin: 0; }}
    main {{ padding: 24px 36px 40px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 12px;
      margin-bottom: 22px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
    }}
    .card .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .card .value {{
      margin-top: 6px;
      font-size: 24px;
      font-weight: 700;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
      padding: 12px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    label {{ font-size: 13px; color: var(--muted); }}
    select {{
      min-width: 220px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .panel {{
      min-width: 0;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
    }}
    .panel.full {{ grid-column: 1 / -1; }}
    .chart {{ width: 100%; height: 420px; }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--panel);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 9px 10px;
      border-bottom: 1px solid var(--border);
      text-align: right;
      white-space: nowrap;
    }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{
      position: sticky;
      top: 0;
      background: #eef2f7;
      color: #334155;
      z-index: 1;
    }}
    @media (max-width: 980px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .chart {{ height: 360px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>A100 Official Benchmark Dashboard</h1>
    <p id="subtitle"></p>
  </header>
  <main>
    <section class="cards" id="cards"></section>
    <section class="toolbar">
      <label for="metricSelect">Primary line metric</label>
      <select id="metricSelect">
        <option value="p95_latency_ms">p95 latency (ms)</option>
        <option value="p50_latency_ms">p50 latency (ms)</option>
        <option value="requests_per_second">requests/sec</option>
        <option value="avg_tokens_per_second">tokens/sec</option>
        <option value="avg_ttft_ms">avg TTFT (ms)</option>
        <option value="error_rate">error rate</option>
      </select>
    </section>
    <section class="grid">
      <div class="panel full">
        <h2>Concurrency Metric Trend</h2>
        <div id="metricTrend" class="chart"></div>
      </div>
      <div class="panel">
        <h2>Latency vs Throughput</h2>
        <div id="pareto" class="chart"></div>
      </div>
      <div class="panel">
        <h2>Scaling Efficiency</h2>
        <div id="scaling" class="chart"></div>
      </div>
      <div class="panel">
        <h2>Agent Workflow Latency</h2>
        <div id="agentLatency" class="chart"></div>
      </div>
      <div class="panel">
        <h2>GPU Memory Snapshot</h2>
        <div id="gpuMemory" class="chart"></div>
      </div>
      <div class="panel">
        <h2>SGLang vs vLLM Ratios</h2>
        <div id="engineRatios" class="chart"></div>
      </div>
      <div class="panel">
        <h2>Agent Step Latency</h2>
        <div id="agentSteps" class="chart"></div>
      </div>
      <div class="panel full">
        <h2>Official Concurrency Metrics</h2>
        <div class="table-wrap" id="metricsTable"></div>
      </div>
      <div class="panel full">
        <h2>Workload Category Metrics</h2>
        <div class="table-wrap" id="workloadTable"></div>
      </div>
    </section>
  </main>
  <script>
    const DATA = {payload_json};
    const plotConfig = {{ responsive: true, displaylogo: false }};
    const baseLayout = {{
      margin: {{ l: 60, r: 26, t: 20, b: 70 }},
      paper_bgcolor: "#ffffff",
      plot_bgcolor: "#ffffff",
      hovermode: "closest",
      legend: {{ orientation: "h", y: -0.25 }},
      font: {{ family: "Inter, Segoe UI, sans-serif", color: "#1f2937" }}
    }};

    function fmt(value, digits = 2) {{
      if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
      return Number(value).toFixed(digits);
    }}
    function groupBy(rows, keyFn) {{
      const map = new Map();
      rows.forEach(row => {{
        const key = keyFn(row);
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(row);
      }});
      return map;
    }}
    function sortedRows(rows) {{
      return [...rows].sort((a, b) =>
        Number(a.model_size_b ?? 999) - Number(b.model_size_b ?? 999) ||
        String(a.engine).localeCompare(String(b.engine)) ||
        Number(a.concurrency ?? 0) - Number(b.concurrency ?? 0)
      );
    }}
    function lineTraces(rows, metric) {{
      const groups = groupBy(sortedRows(rows), row => row.series_label);
      return [...groups.entries()].map(([name, values]) => ({{
        type: "scatter",
        mode: "lines+markers",
        name,
        x: values.map(row => row.concurrency),
        y: values.map(row => row[metric]),
        customdata: values.map(row => [row.p50_latency_ms, row.p95_latency_ms, row.requests_per_second, row.avg_ttft_ms, row.avg_tokens_per_second]),
        hovertemplate:
          "<b>%{{fullData.name}}</b><br>Concurrency: %{{x}}<br>Metric: %{{y:.3f}}" +
          "<br>p50: %{{customdata[0]:.1f}} ms<br>p95: %{{customdata[1]:.1f}} ms" +
          "<br>RPS: %{{customdata[2]:.3f}}<br>TTFT: %{{customdata[3]:.1f}} ms" +
          "<br>Tok/s: %{{customdata[4]:.2f}}<extra></extra>"
      }}));
    }}
    function renderMetricTrend() {{
      const metric = document.getElementById("metricSelect").value;
      const label = document.getElementById("metricSelect").selectedOptions[0].text;
      Plotly.react("metricTrend", lineTraces(DATA.concurrency, metric), {{
        ...baseLayout,
        yaxis: {{ title: label }},
        xaxis: {{ title: "Concurrency", dtick: 1 }}
      }}, plotConfig);
    }}
    function renderPareto() {{
      const traces = sortedRows(DATA.concurrency).map(row => ({{
        type: "scatter",
        mode: "markers+text",
        name: `${{row.series_label}} c${{row.concurrency}}`,
        x: [row.p95_latency_ms],
        y: [row.requests_per_second],
        text: [`c${{row.concurrency}}`],
        textposition: "top center",
        marker: {{
          size: Math.max(9, Math.min(28, Number(row.avg_tokens_per_second || 0) / 2)),
          line: {{ width: 1, color: "#334155" }}
        }},
        hovertemplate:
          `<b>${{row.series_label}}</b><br>Concurrency: ${{row.concurrency}}` +
          "<br>p95 latency: %{{x:.1f}} ms<br>Requests/sec: %{{y:.3f}}" +
          `<br>Tokens/sec: ${{fmt(row.avg_tokens_per_second)}}<extra></extra>`
      }}));
      Plotly.newPlot("pareto", traces, {{
        ...baseLayout,
        xaxis: {{ title: "p95 latency (ms)" }},
        yaxis: {{ title: "requests/sec" }},
        showlegend: false
      }}, plotConfig);
    }}
    function renderScaling() {{
      Plotly.newPlot("scaling", lineTraces(DATA.scaling, "scaling_efficiency_pct"), {{
        ...baseLayout,
        yaxis: {{ title: "Scaling efficiency (%)" }},
        xaxis: {{ title: "Concurrency", dtick: 1 }}
      }}, plotConfig);
    }}
    function renderAgentLatency() {{
      const rows = sortedRows(DATA.agents);
      Plotly.newPlot("agentLatency", [{{
        type: "bar",
        x: rows.map(row => `${{row.series_label}}<br>${{row.workflow_mode}}`),
        y: rows.map(row => row.avg_workflow_latency_s),
        marker: {{ color: rows.map(row => row.workflow_mode === "concurrent" ? "#1f7a8c" : "#8a5a44") }},
        hovertemplate: "%{{x}}<br>Avg workflow latency: %{{y:.2f}}s<extra></extra>"
      }}], {{
        ...baseLayout,
        yaxis: {{ title: "Average workflow latency (seconds)" }},
        xaxis: {{ tickangle: -35 }}
      }}, plotConfig);
    }}
    function renderGpuMemory() {{
      const rows = sortedRows(DATA.gpu.filter(row => row.snapshot_phase === "after" && row.run_type === "concurrency_summary"));
      Plotly.newPlot("gpuMemory", [{{
        type: "scatter",
        mode: "markers",
        x: rows.map(row => row.concurrency),
        y: rows.map(row => row.gpu_memory_used_pct),
        text: rows.map(row => row.series_label),
        marker: {{
          size: rows.map(row => Math.max(8, Number(row.gpu_util_percent || 0) / 4)),
          color: rows.map(row => Number(row.gpu_power_watts || 0)),
          colorscale: "Viridis",
          colorbar: {{ title: "Watts" }}
        }},
        hovertemplate: "<b>%{{text}}</b><br>Concurrency: %{{x}}<br>Memory used: %{{y:.1f}}%<extra></extra>"
      }}], {{
        ...baseLayout,
        xaxis: {{ title: "Concurrency", dtick: 1 }},
        yaxis: {{ title: "GPU memory used (%)" }}
      }}, plotConfig);
    }}
    function renderEngineRatios() {{
      const rows = DATA.engineComparison;
      Plotly.newPlot("engineRatios", [
        {{
          type: "bar",
          name: "RPS ratio",
          x: rows.map(row => `${{row.model_label}} c${{row.concurrency}}`),
          y: rows.map(row => row.sglang_vs_vllm_rps_ratio)
        }},
        {{
          type: "bar",
          name: "p95 ratio",
          x: rows.map(row => `${{row.model_label}} c${{row.concurrency}}`),
          y: rows.map(row => row.sglang_vs_vllm_p95_ratio)
        }}
      ], {{
        ...baseLayout,
        barmode: "group",
        yaxis: {{ title: "SGLang / vLLM ratio" }},
        xaxis: {{ tickangle: -35 }}
      }}, plotConfig);
    }}
    function renderAgentSteps() {{
      const rows = sortedRows(DATA.agentSteps);
      Plotly.newPlot("agentSteps", [{{
        type: "bar",
        x: rows.map(row => `${{row.series_label}}<br>${{row.workflow_mode}}<br>${{row.agent || "agent"}}`),
        y: rows.map(row => row.p95_step_latency_ms),
        hovertemplate: "%{{x}}<br>p95 step latency: %{{y:.1f}} ms<extra></extra>"
      }}], {{
        ...baseLayout,
        yaxis: {{ title: "p95 agent step latency (ms)" }},
        xaxis: {{ tickangle: -35 }}
      }}, plotConfig);
    }}
    function renderCards() {{
      const errors = DATA.concurrency.reduce((sum, row) => sum + Number(row.error_count || 0), 0);
      const peak = [...DATA.concurrency].sort((a, b) => Number(b.requests_per_second || 0) - Number(a.requests_per_second || 0))[0] || {{}};
      const fastestAgent = [...DATA.agents].sort((a, b) => Number(a.avg_workflow_latency_s || 1e9) - Number(b.avg_workflow_latency_s || 1e9))[0] || {{}};
      const cards = [
        ["Official rows", DATA.officialRowCount],
        ["Excluded rows", DATA.excludedRowCount],
        ["Concurrency errors", errors],
        ["Peak requests/sec", `${{fmt(peak.requests_per_second)}}`],
        ["Peak throughput config", `${{peak.series_label || ""}} c${{peak.concurrency || ""}}`],
        ["Fastest agent workflow", `${{fastestAgent.series_label || ""}} ${{fastestAgent.workflow_mode || ""}}`]
      ];
      document.getElementById("cards").innerHTML = cards.map(([label, value]) =>
        `<article class="card"><div class="label">${{label}}</div><div class="value">${{value}}</div></article>`
      ).join("");
      document.getElementById("subtitle").textContent =
        `${{DATA.experimentName}} · official benchmark tags only · performance analysis`;
    }}
    function renderTable(target, rows, columns) {{
      const header = `<tr>${{columns.map(col => `<th>${{col.label}}</th>`).join("")}}</tr>`;
      const body = rows.map(row => `<tr>${{columns.map(col => {{
        const value = row[col.key];
        const rendered = typeof value === "number" ? fmt(value, col.digits ?? 2) : (value ?? "");
        return `<td>${{rendered}}</td>`;
      }}).join("")}}</tr>`).join("");
      document.getElementById(target).innerHTML = `<table>${{header}}${{body}}</table>`;
    }}
    renderCards();
    renderMetricTrend();
    renderPareto();
    renderScaling();
    renderAgentLatency();
    renderGpuMemory();
    renderEngineRatios();
    renderAgentSteps();
    renderTable("metricsTable", sortedRows(DATA.concurrency), [
      {{ key: "series_label", label: "model / engine" }},
      {{ key: "concurrency", label: "concurrency", digits: 0 }},
      {{ key: "p50_latency_ms", label: "p50 ms", digits: 1 }},
      {{ key: "p95_latency_ms", label: "p95 ms", digits: 1 }},
      {{ key: "requests_per_second", label: "req/s", digits: 3 }},
      {{ key: "avg_tokens_per_second", label: "tok/s", digits: 2 }},
      {{ key: "avg_ttft_ms", label: "TTFT ms", digits: 1 }},
      {{ key: "error_rate", label: "error rate", digits: 4 }}
    ]);
    renderTable("workloadTable", DATA.workloads, [
      {{ key: "series_label", label: "model / engine" }},
      {{ key: "run_type", label: "run type" }},
      {{ key: "category", label: "category" }},
      {{ key: "request_count", label: "requests", digits: 0 }},
      {{ key: "p50_latency_ms", label: "p50 ms", digits: 1 }},
      {{ key: "p95_latency_ms", label: "p95 ms", digits: 1 }},
      {{ key: "avg_ttft_ms", label: "TTFT ms", digits: 1 }},
      {{ key: "avg_tokens_per_second", label: "tok/s", digits: 2 }},
      {{ key: "success_rate", label: "success", digits: 3 }}
    ]);
    document.getElementById("metricSelect").addEventListener("change", renderMetricTrend);
  </script>
</body>
</html>
"""


def build_summary_metrics(rows: list[dict[str, Any]], official_only: bool = True) -> pd.DataFrame:
    filtered = (
        [row for row in rows if is_official_run_tag(row.get("run_tag"))] if official_only else rows
    )
    if not filtered:
        return pd.DataFrame()
    df = pd.DataFrame(flatten_analysis_row(row) for row in filtered)
    return (
        df.groupby(
            ["run_tag", "model", "model_label", "engine", "gpu_name", "run_type"], dropna=False
        )
        .agg(
            row_count=("run_id", "count"),
            success_rate=("success", "mean"),
            error_count=("success", _failure_count),
        )
        .reset_index()
        .sort_values(["model_label", "engine", "run_type"], na_position="last")
    )


def write_analysis_outputs(
    experiment_dir: str | Path,
    output_dir: str | Path | None = None,
    official_only: bool = True,
) -> dict[str, Path]:
    resolved_experiment = resolve_repo_path(experiment_dir)
    resolved_output = (
        resolve_repo_path(output_dir) if output_dir else resolved_experiment / "analysis"
    )
    resolved_output.mkdir(parents=True, exist_ok=True)

    rows = read_experiment_rows(resolved_experiment)
    official_rows = [row for row in rows if is_official_run_tag(row.get("run_tag"))]
    excluded_row_count = len(rows) - len(official_rows) if official_only else 0
    df = build_results_dataframe(rows, official_only=official_only)

    summary_metrics = build_summary_metrics(rows, official_only=official_only)
    concurrency_metrics = build_concurrency_metrics(df)
    scaling_metrics = build_scaling_metrics(concurrency_metrics)
    workload_metrics = build_workload_metrics(df)
    agent_metrics = build_agent_metrics(df)
    agent_step_metrics = build_agent_step_metrics(df)
    gpu_snapshots = build_gpu_snapshots(rows, official_only=official_only)
    engine_comparison = build_engine_comparison(concurrency_metrics)

    outputs = {
        "summary_metrics": resolved_output / "summary_metrics.csv",
        "concurrency_metrics": resolved_output / "concurrency_metrics.csv",
        "scaling_metrics": resolved_output / "scaling_metrics.csv",
        "workload_metrics": resolved_output / "workload_metrics.csv",
        "agent_metrics": resolved_output / "agent_metrics.csv",
        "agent_step_metrics": resolved_output / "agent_step_metrics.csv",
        "gpu_snapshots": resolved_output / "gpu_snapshots.csv",
        "engine_comparison": resolved_output / "engine_comparison.csv",
        "report": resolved_output / "analysis_report.md",
        "dashboard": resolved_output / "dashboard.html",
    }
    summary_metrics.to_csv(outputs["summary_metrics"], index=False)
    concurrency_metrics.to_csv(outputs["concurrency_metrics"], index=False)
    scaling_metrics.to_csv(outputs["scaling_metrics"], index=False)
    workload_metrics.to_csv(outputs["workload_metrics"], index=False)
    agent_metrics.to_csv(outputs["agent_metrics"], index=False)
    agent_step_metrics.to_csv(outputs["agent_step_metrics"], index=False)
    gpu_snapshots.to_csv(outputs["gpu_snapshots"], index=False)
    engine_comparison.to_csv(outputs["engine_comparison"], index=False)

    report = build_analysis_report(
        experiment_dir=resolved_experiment,
        official_row_count=len(official_rows) if official_only else len(rows),
        excluded_row_count=excluded_row_count,
        concurrency_metrics=concurrency_metrics,
        scaling_metrics=scaling_metrics,
        workload_metrics=workload_metrics,
        agent_metrics=agent_metrics,
        agent_step_metrics=agent_step_metrics,
        gpu_snapshots=gpu_snapshots,
        engine_comparison=engine_comparison,
    )
    outputs["report"].write_text(report, encoding="utf-8")

    dashboard = build_dashboard_html(
        experiment_name=resolved_experiment.name,
        official_row_count=len(official_rows) if official_only else len(rows),
        excluded_row_count=excluded_row_count,
        concurrency_metrics=concurrency_metrics,
        scaling_metrics=scaling_metrics,
        workload_metrics=workload_metrics,
        agent_metrics=agent_metrics,
        agent_step_metrics=agent_step_metrics,
        gpu_snapshots=gpu_snapshots,
        engine_comparison=engine_comparison,
    )
    outputs["dashboard"].write_text(dashboard, encoding="utf-8")
    return outputs


@app.command()
def main(
    experiment_dir: Path = typer.Argument(
        ..., help="Experiment run directory containing a results/ folder."
    ),
    output_dir: Path | None = typer.Option(
        None, help="Output directory. Defaults to <experiment_dir>/analysis."
    ),
    include_non_official: bool = typer.Option(
        False, help="Include non-official run tags such as smoke rows."
    ),
) -> None:
    outputs = write_analysis_outputs(
        experiment_dir=experiment_dir,
        output_dir=output_dir,
        official_only=not include_non_official,
    )
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    app()
