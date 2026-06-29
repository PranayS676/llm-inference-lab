from __future__ import annotations

import json
from pathlib import Path

from runpod_inference_lab.reports.deep_analysis import (
    build_concurrency_metrics,
    build_gpu_snapshots,
    build_results_dataframe,
    write_analysis_outputs,
)


def detail_row(
    *,
    run_tag: str = "a100-vllm-qwen3-4b-official",
    run_type: str = "concurrency_detail",
    latency_ms: float = 100.0,
    ttft_ms: float = 10.0,
    tokens_per_second: float = 50.0,
    success: bool = True,
) -> dict:
    return {
        "run_id": f"run-{run_tag}-{run_type}-{latency_ms}",
        "run_tag": run_tag,
        "timestamp_utc": "2026-06-28T00:00:00Z",
        "run_type": run_type,
        "provider": "runpod",
        "gpu_name": "A100_80GB",
        "engine": "vllm",
        "engine_version": "0.11.0",
        "model": "Qwen/Qwen3-4B",
        "prompt_file": "prompts/simple_tasks.jsonl",
        "task_id": "simple_001",
        "category": "json_extraction",
        "concurrency": 1,
        "success": success,
        "error": None if success else "failed",
        "latency_ms": latency_ms,
        "ttft_ms": ttft_ms,
        "tokens_per_second_est": tokens_per_second,
        "estimated_input_tokens": 10,
        "estimated_output_tokens": 5,
        "json_valid": True,
    }


def concurrency_summary_row(run_tag: str = "a100-vllm-qwen3-4b-official") -> dict:
    row = detail_row(run_tag=run_tag, run_type="concurrency_summary", latency_ms=0)
    row.update(
        {
            "category": "summary",
            "p50_latency_ms": 200.0,
            "p95_latency_ms": 290.0,
            "p99_latency_ms": 300.0,
            "requests_per_second": 2.0,
            "suite_latency_ms": 1000.0,
            "success_count": 2,
            "error_count": 0,
            "total_tasks": 2,
            "gpu_before": {
                "detected_gpu_name": "NVIDIA A100-SXM4-80GB",
                "gpus": [
                    {
                        "index": 0,
                        "memory_used_mb": 1000.0,
                        "memory_total_mb": 81920.0,
                        "gpu_util_percent": 0.0,
                        "power_watts": 70.0,
                    }
                ],
            },
            "gpu_after": {
                "detected_gpu_name": "NVIDIA A100-SXM4-80GB",
                "gpus": [
                    {
                        "index": 0,
                        "memory_used_mb": 2000.0,
                        "memory_total_mb": 81920.0,
                        "gpu_util_percent": 80.0,
                        "power_watts": 250.0,
                    }
                ],
            },
        }
    )
    return row


def agent_rows() -> list[dict]:
    detail = detail_row(run_type="agent_sequential_detail", latency_ms=500.0, ttft_ms=25.0)
    detail.update({"agent": "planner", "category": "multi_agent"})
    summary = detail_row(run_type="agent_sequential_summary", latency_ms=0)
    summary.update(
        {
            "agent_count": 1,
            "category": "multi_agent",
            "workflow_latency_ms": 500.0,
            "latency_ms": None,
        }
    )
    return [detail, summary]


def test_build_results_dataframe_excludes_non_official_rows():
    rows = [
        detail_row(run_tag="a100-vllm-qwen3-4b-official"),
        detail_row(run_tag="a100-sglang-qwen3-4b-smoke"),
    ]

    df = build_results_dataframe(rows, official_only=True)

    assert len(df) == 1
    assert df.iloc[0]["run_tag"] == "a100-vllm-qwen3-4b-official"


def test_build_concurrency_metrics_merges_summary_and_detail_metrics():
    rows = [
        detail_row(latency_ms=100.0, ttft_ms=10.0, tokens_per_second=40.0),
        detail_row(latency_ms=300.0, ttft_ms=30.0, tokens_per_second=60.0),
        concurrency_summary_row(),
    ]
    df = build_results_dataframe(rows)

    metrics = build_concurrency_metrics(df)

    assert len(metrics) == 1
    metric = metrics.iloc[0]
    assert metric["p50_latency_ms"] == 200.0
    assert metric["p95_latency_ms"] == 290.0
    assert metric["avg_latency_ms"] == 200.0
    assert metric["avg_ttft_ms"] == 20.0
    assert metric["avg_tokens_per_second"] == 50.0
    assert metric["error_rate"] == 0.0


def test_build_gpu_snapshots_flattens_before_and_after_snapshots():
    snapshots = build_gpu_snapshots([concurrency_summary_row()])

    assert len(snapshots) == 2
    assert set(snapshots["snapshot_phase"]) == {"before", "after"}
    after = snapshots[snapshots["snapshot_phase"] == "after"].iloc[0]
    assert after["gpu_memory_used_mb"] == 2000.0
    assert round(after["gpu_memory_used_pct"], 3) == round(2000.0 / 81920.0 * 100, 3)


def test_write_analysis_outputs_creates_official_only_report_and_dashboard(tmp_path: Path):
    experiment_dir = tmp_path / "experiment"
    results_dir = experiment_dir / "results"
    results_dir.mkdir(parents=True)
    rows = [
        detail_row(latency_ms=100.0),
        detail_row(latency_ms=300.0),
        concurrency_summary_row(),
        *agent_rows(),
        detail_row(run_tag="a100-sglang-qwen3-4b-smoke"),
    ]
    with (results_dir / "results.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    outputs = write_analysis_outputs(experiment_dir)

    assert outputs["dashboard"].exists()
    assert outputs["report"].exists()
    dashboard = outputs["dashboard"].read_text(encoding="utf-8")
    report = outputs["report"].read_text(encoding="utf-8")
    assert "a100-vllm-qwen3-4b-official" in dashboard
    assert "a100-sglang-qwen3-4b-smoke" not in dashboard
    assert "Official result rows analyzed: 5" in report
    assert "Non-official rows excluded: 1" in report
