from __future__ import annotations

import json
from typing import Any


def evaluate_json_validity(response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(response)
    except Exception as exc:
        return {"json_valid": False, "json_error": str(exc), "json_type": None}
    return {"json_valid": True, "json_error": None, "json_type": type(parsed).__name__}


def evaluate_if_needed(expected_type: str | None, response: str) -> dict[str, Any]:
    if expected_type != "json":
        return {}
    return evaluate_json_validity(response)
