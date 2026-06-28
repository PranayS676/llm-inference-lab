from __future__ import annotations

from pathlib import Path
from typing import Any

from runpod_inference_lab.common.gpu import read_nvidia_smi
from runpod_inference_lab.common.llm_client import OpenAICompatibleClient
from runpod_inference_lab.common.metadata import RunMetadata, prompt_file_metadata
from runpod_inference_lab.common.result_schema import build_result_row, validate_result_row
from runpod_inference_lab.common.settings import Settings


def make_client(settings: Settings) -> OpenAICompatibleClient:
    return OpenAICompatibleClient(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.model_name,
        timeout_seconds=settings.request_timeout_seconds,
        default_extra_body=settings.default_extra_body,
    )


def resolve_output_file(settings: Settings, output_file: Path | None, filename: str) -> Path:
    return output_file if output_file is not None else settings.results_dir / filename


def build_task_result(
    metadata: RunMetadata,
    settings: Settings,
    run_type: str,
    task_row: dict[str, Any],
    prompt: str,
    result: dict[str, Any],
    prompt_file: str | Path | None,
    concurrency: int,
    max_tokens: int,
    gpu_before: dict[str, Any] | None = None,
    gpu_after: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = build_result_row(
        metadata,
        run_type=run_type,
        task_id=task_row.get("id"),
        category=task_row.get("category"),
        prompt=prompt,
        expected_type=task_row.get("expected_type"),
        concurrency=concurrency,
        temperature=settings.temperature,
        max_tokens=max_tokens,
        gpu_before=gpu_before,
        gpu_after=gpu_after,
        **prompt_file_metadata(prompt_file),
        **result,
        **(extra or {}),
    )
    validate_result_row(row)
    return row


def gpu_pair() -> tuple[dict[str, Any], dict[str, Any]]:
    before = read_nvidia_smi()
    after = read_nvidia_smi()
    return before, after
