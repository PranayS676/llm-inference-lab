from __future__ import annotations

from runpod_inference_lab.common.llm_client import LLMCallResult


def test_llm_call_result_dict_shape():
    result = LLMCallResult(
        response="hello",
        success=True,
        error=None,
        latency_ms=10,
        ttft_ms=2,
        estimated_input_tokens=3,
        estimated_output_tokens=1,
        tokens_per_second_est=100,
        usage={},
    )

    payload = result.to_dict()

    assert payload["success"] is True
    assert payload["response"] == "hello"
    assert payload["estimated_output_tokens"] == 1
