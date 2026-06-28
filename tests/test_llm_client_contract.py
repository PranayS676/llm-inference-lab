from __future__ import annotations

from runpod_inference_lab.common.llm_client import LLMCallResult, OpenAICompatibleClient


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


def test_openai_client_merges_default_extra_body():
    client = OpenAICompatibleClient(
        base_url="http://127.0.0.1:8000/v1",
        api_key="dummy",
        model="Qwen/Qwen3-4B",
        default_extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False,
            }
        },
    )

    payload = client._extra_body_for_request(
        {
            "chat_template_kwargs": {
                "other_option": "value",
            },
            "top_k": 20,
        }
    )

    assert payload == {
        "chat_template_kwargs": {
            "enable_thinking": False,
            "other_option": "value",
        },
        "top_k": 20,
    }
