from __future__ import annotations

import platform
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runpod_inference_lab.common.io import file_sha256
from runpod_inference_lab.common.paths import repo_root
from runpod_inference_lab.common.settings import Settings


def _command_output(args: list[str], cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def git_commit() -> str:
    return _command_output(["git", "rev-parse", "HEAD"], cwd=repo_root())


def package_version(package: str) -> str:
    return _command_output([sys.executable, "-m", "pip", "show", package])


def cuda_version() -> str:
    out = _command_output(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"])
    return out.splitlines()[0].strip() if out != "unknown" and out else "unknown"


@dataclass(frozen=True)
class RunMetadata:
    run_id: str
    run_tag: str
    timestamp_utc: str
    git_commit: str
    provider: str
    gpu_name: str
    gpu_memory_gb: float | None
    engine: str
    engine_version: str
    model: str
    model_revision: str
    max_model_len: int
    dtype: str
    gpu_memory_utilization: float
    pod_id: str
    python_version: str
    platform: str
    cuda_version: str

    @classmethod
    def create(cls, settings: Settings, run_id: str | None = None) -> RunMetadata:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        return cls(
            run_id=run_id or f"run-{timestamp}-{uuid.uuid4().hex[:8]}",
            run_tag=settings.run_tag,
            timestamp_utc=datetime.now(UTC).isoformat(),
            git_commit=git_commit(),
            provider=settings.provider,
            gpu_name=settings.gpu_name,
            gpu_memory_gb=settings.gpu_memory_gb,
            engine=settings.engine,
            engine_version=settings.engine_version,
            model=settings.model_name,
            model_revision=settings.model_revision,
            max_model_len=settings.max_model_len,
            dtype=settings.dtype,
            gpu_memory_utilization=settings.gpu_memory_utilization,
            pod_id=settings.pod_id,
            python_version=platform.python_version(),
            platform=platform.platform(),
            cuda_version=cuda_version(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def prompt_file_metadata(prompt_file: str | Path | None) -> dict[str, Any]:
    if prompt_file is None:
        return {"prompt_file": None, "prompt_file_sha256": None}
    return {"prompt_file": str(prompt_file), "prompt_file_sha256": file_sha256(prompt_file)}
