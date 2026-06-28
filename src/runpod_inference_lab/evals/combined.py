from __future__ import annotations

from typing import Any

from runpod_inference_lab.evals.exact_answer import evaluate_exact_or_contains
from runpod_inference_lab.evals.json_validity import evaluate_if_needed


def evaluate_task(row: dict[str, Any], response: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    output.update(evaluate_if_needed(row.get("expected_type"), response))
    output.update(evaluate_exact_or_contains(row.get("expected_answer"), response))
    return output
