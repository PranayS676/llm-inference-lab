from __future__ import annotations

import json
from typing import Any


def normalize_json_response(response: str) -> str:
    text = response.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if len(lines) < 3 or lines[-1].strip() != "```":
        return text

    opening_fence = lines[0].strip().lower()
    if opening_fence not in {"```", "```json"}:
        return text

    return "\n".join(lines[1:-1]).strip()


def evaluate_json_validity(response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(normalize_json_response(response))
    except Exception as exc:
        return {"json_valid": False, "json_error": str(exc), "json_type": None}
    return {"json_valid": True, "json_error": None, "json_type": type(parsed).__name__}


def evaluate_if_needed(expected_type: str | None, response: str) -> dict[str, Any]:
    if expected_type != "json":
        return {}
    return evaluate_json_validity(response)
