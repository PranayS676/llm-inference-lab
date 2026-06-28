from __future__ import annotations

from typing import Any

from runpod_inference_lab.common.metadata import RunMetadata

REQUIRED_RESULT_KEYS = {
    "run_id",
    "run_tag",
    "timestamp_utc",
    "git_commit",
    "provider",
    "gpu_name",
    "engine",
    "engine_version",
    "model",
    "model_revision",
    "max_model_len",
    "dtype",
    "gpu_memory_utilization",
    "task_id",
    "category",
    "concurrency",
    "temperature",
    "max_tokens",
    "success",
    "error",
}


def build_result_row(metadata: RunMetadata, **values: Any) -> dict[str, Any]:
    row = metadata.to_dict()
    row.update(values)
    return row


def missing_required_keys(row: dict[str, Any]) -> set[str]:
    return REQUIRED_RESULT_KEYS - set(row)


def validate_result_row(row: dict[str, Any]) -> None:
    missing = missing_required_keys(row)
    if missing:
        raise ValueError(f"Result row is missing required keys: {sorted(missing)}")
