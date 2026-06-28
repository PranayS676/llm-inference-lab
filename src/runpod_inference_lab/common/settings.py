from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from runpod_inference_lab.common.paths import repo_root, resolve_repo_path


def load_project_env() -> None:
    load_dotenv(repo_root() / ".env", override=False)


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    return int(_env(name, str(default)))


def _env_float(name: str, default: float) -> float:
    return float(_env(name, str(default)))


def _env_bool_optional(name: str) -> bool | None:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return None
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be one of: true, false, 1, 0, yes, no, on, off")


@dataclass(frozen=True)
class Settings:
    openai_base_url: str
    openai_api_key: str
    model_name: str
    model_revision: str
    provider: str
    gpu_name: str
    gpu_memory_gb: float | None
    engine: str
    engine_version: str
    run_tag: str
    pod_id: str
    results_dir: Path
    request_timeout_seconds: float
    max_model_len: int
    gpu_memory_utilization: float
    dtype: str
    temperature: float
    chat_template_enable_thinking: bool | None

    @property
    def default_extra_body(self) -> dict[str, Any] | None:
        if self.chat_template_enable_thinking is None:
            return None
        return {
            "chat_template_kwargs": {
                "enable_thinking": self.chat_template_enable_thinking,
            }
        }

    @classmethod
    def from_env(cls) -> Settings:
        load_project_env()
        gpu_memory_raw = _env("GPU_MEMORY_GB", "")
        return cls(
            openai_base_url=_env("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"),
            openai_api_key=_env("OPENAI_API_KEY", "dummy"),
            model_name=_env("MODEL_NAME", "Qwen/Qwen3-4B"),
            model_revision=_env("MODEL_REVISION", "unknown"),
            provider=_env("PROVIDER", "runpod"),
            gpu_name=_env("GPU_NAME", "unknown_gpu"),
            gpu_memory_gb=float(gpu_memory_raw) if gpu_memory_raw else None,
            engine=_env("ENGINE", "vllm"),
            engine_version=_env("ENGINE_VERSION", "unknown"),
            run_tag=_env("RUN_TAG", "dev"),
            pod_id=_env("POD_ID", "unknown"),
            results_dir=resolve_repo_path(_env("RESULTS_DIR", "results")),
            request_timeout_seconds=_env_float("REQUEST_TIMEOUT_SECONDS", 180),
            max_model_len=_env_int("MAX_MODEL_LEN", 32768),
            gpu_memory_utilization=_env_float("GPU_MEMORY_UTILIZATION", 0.90),
            dtype=_env("DTYPE", "auto"),
            temperature=_env_float("TEMPERATURE", 0.0),
            chat_template_enable_thinking=_env_bool_optional("CHAT_TEMPLATE_ENABLE_THINKING"),
        )
