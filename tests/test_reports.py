from __future__ import annotations

from runpod_inference_lab.reports.generate_markdown_report import build_report
from runpod_inference_lab.reports.summarize_results import summarize_dataframe


def sample_row() -> dict:
    return {
        "run_id": "run-1",
        "run_tag": "test",
        "timestamp_utc": "2026-06-28T00:00:00Z",
        "run_type": "batch",
        "provider": "runpod",
        "gpu_name": "A100_80GB",
        "engine": "vllm",
        "engine_version": "test",
        "model": "Qwen/Qwen3-4B",
        "prompt_file": "prompts/simple_tasks.jsonl",
        "task_id": "simple_001",
        "category": "json_extraction",
        "concurrency": 1,
        "success": True,
        "error": None,
        "latency_ms": 100.0,
        "ttft_ms": 20.0,
        "tokens_per_second_est": 50.0,
        "estimated_input_tokens": 10,
        "estimated_output_tokens": 5,
        "json_valid": True,
    }


def test_summarize_dataframe_groups_results():
    summary = summarize_dataframe([sample_row()])

    assert len(summary) == 1
    assert summary.iloc[0]["success_rate"] == 1.0


def test_build_report_contains_overview():
    report = build_report([sample_row()])

    assert "# LLM Inference Lab Report" in report
    assert "Grouped Summary" in report
