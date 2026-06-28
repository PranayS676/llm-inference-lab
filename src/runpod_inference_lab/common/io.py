from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from runpod_inference_lab.common.paths import resolve_repo_path


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    resolved = resolve_repo_path(path)
    rows: list[dict[str, Any]] = []
    with resolved.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {resolved}:{line_number}: {exc}") from exc
    return rows


def append_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> Path:
    resolved = resolve_repo_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return resolved


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> Path:
    resolved = resolve_repo_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return resolved


def file_sha256(path: str | Path) -> str:
    resolved = resolve_repo_path(path)
    digest = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: str | Path) -> str:
    return resolve_repo_path(path).read_text(encoding="utf-8")
