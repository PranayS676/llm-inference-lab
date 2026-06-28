from __future__ import annotations

from runpod_inference_lab.evals.combined import evaluate_task
from runpod_inference_lab.evals.exact_answer import evaluate_exact_or_contains
from runpod_inference_lab.evals.json_validity import evaluate_json_validity


def test_json_validity_evaluator():
    assert evaluate_json_validity('{"ok": true}')["json_valid"] is True
    assert evaluate_json_validity("not-json")["json_valid"] is False


def test_json_validity_accepts_markdown_fenced_json():
    response = """```json
{"ok": true}
```"""

    assert evaluate_json_validity(response)["json_valid"] is True


def test_json_validity_rejects_json_inside_extra_prose():
    response = """Here is the JSON:
```json
{"ok": true}
```"""

    assert evaluate_json_validity(response)["json_valid"] is False


def test_exact_answer_contains():
    result = evaluate_exact_or_contains("A100 80GB", "The best GPU is A100 80GB for this test.")

    assert result["exact_match"] is False
    assert result["contains_expected"] is True


def test_combined_evaluator():
    result = evaluate_task(
        {"expected_type": "json", "expected_answer": None},
        '{"model": "Qwen"}',
    )

    assert result["json_valid"] is True
