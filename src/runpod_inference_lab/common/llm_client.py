from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from openai import AsyncOpenAI

from runpod_inference_lab.common.tokens import estimate_tokens


@dataclass(frozen=True)
class LLMCallResult:
    response: str
    success: bool
    error: str | None
    latency_ms: float
    ttft_ms: float | None
    estimated_input_tokens: int
    estimated_output_tokens: int
    tokens_per_second_est: float
    usage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LLMClient(Protocol):
    async def chat(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stream: bool = True,
        extra_body: dict[str, Any] | None = None,
    ) -> LLMCallResult: ...


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 180,
        default_extra_body: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout_seconds)
        self.default_extra_body = deepcopy(default_extra_body)

    def _extra_body_for_request(self, extra_body: dict[str, Any] | None) -> dict[str, Any] | None:
        if self.default_extra_body is None:
            return extra_body
        if extra_body is None:
            return deepcopy(self.default_extra_body)

        merged = deepcopy(self.default_extra_body)
        for key, value in extra_body.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                nested = dict(merged[key])
                nested.update(value)
                merged[key] = nested
            else:
                merged[key] = value
        return merged

    async def chat(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.0,
        stream: bool = True,
        extra_body: dict[str, Any] | None = None,
    ) -> LLMCallResult:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        start = time.perf_counter()
        first_token_time: float | None = None
        chunks: list[str] = []
        usage: dict[str, Any] = {}
        request_extra_body = self._extra_body_for_request(extra_body)

        try:
            if stream:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    extra_body=request_extra_body,
                )
                async for event in response:
                    delta = event.choices[0].delta.content or ""
                    if delta and first_token_time is None:
                        first_token_time = time.perf_counter()
                    chunks.append(delta)
                text = "".join(chunks)
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                    extra_body=request_extra_body,
                )
                text = response.choices[0].message.content or ""
                usage = response.usage.model_dump() if response.usage else {}

            end = time.perf_counter()
            latency_seconds = max(end - start, 1e-9)
            output_tokens = estimate_tokens(text)
            return LLMCallResult(
                response=text,
                success=True,
                error=None,
                latency_ms=latency_seconds * 1000,
                ttft_ms=(first_token_time - start) * 1000 if first_token_time else None,
                estimated_input_tokens=estimate_tokens(prompt),
                estimated_output_tokens=output_tokens,
                tokens_per_second_est=output_tokens / latency_seconds,
                usage=usage,
            )
        except Exception as exc:
            end = time.perf_counter()
            return LLMCallResult(
                response="",
                success=False,
                error=repr(exc),
                latency_ms=(end - start) * 1000,
                ttft_ms=None,
                estimated_input_tokens=estimate_tokens(prompt),
                estimated_output_tokens=0,
                tokens_per_second_est=0,
                usage={},
            )
