from __future__ import annotations

from typing import Any

from runpod_inference_lab.common.io import read_jsonl


def build_prompt(row: dict[str, Any]) -> str:
    prompt = row.get("prompt") or row.get("task") or ""
    context = row.get("context")
    if context:
        return f"Context:\n{context}\n\nQuestion:\n{prompt}"
    return prompt


def load_prompt_rows(
    path: str,
    max_tasks: int | None = None,
    repeat: bool = False,
) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"No prompts found in {path}")
    if max_tasks is None:
        return rows
    if not repeat:
        return rows[:max_tasks]
    return [rows[index % len(rows)] for index in range(max_tasks)]
