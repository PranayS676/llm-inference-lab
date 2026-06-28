from __future__ import annotations

from typing import Any


def normalize_text(value: str) -> str:
    return " ".join(value.lower().strip().split())


def evaluate_exact_or_contains(expected_answer: str | None, response: str) -> dict[str, Any]:
    if not expected_answer:
        return {}
    expected = normalize_text(expected_answer)
    actual = normalize_text(response)
    return {
        "expected_answer": expected_answer,
        "exact_match": actual == expected,
        "contains_expected": expected in actual,
    }
