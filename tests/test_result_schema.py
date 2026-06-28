from __future__ import annotations

import pytest

from runpod_inference_lab.common.metadata import RunMetadata
from runpod_inference_lab.common.result_schema import build_result_row, validate_result_row


def metadata() -> RunMetadata:
    return RunMetadata(
        run_id="run-test",
        run_tag="test",
        timestamp_utc="2026-06-28T00:00:00Z",
        git_commit="abc123",
        provider="runpod",
        gpu_name="A100_80GB",
        gpu_memory_gb=80,
        engine="vllm",
        engine_version="test",
        model="Qwen/Qwen3-4B",
        model_revision="unknown",
        max_model_len=32768,
        dtype="auto",
        gpu_memory_utilization=0.9,
        pod_id="pod-test",
        python_version="3.11",
        platform="test",
        cuda_version="unknown",
    )


def test_valid_result_row_has_required_keys():
    row = build_result_row(
        metadata(),
        task_id="task-1",
        category="simple",
        concurrency=1,
        temperature=0,
        max_tokens=128,
        success=True,
        error=None,
    )

    validate_result_row(row)


def test_missing_result_key_fails_validation():
    row = metadata().to_dict()

    with pytest.raises(ValueError):
        validate_result_row(row)
