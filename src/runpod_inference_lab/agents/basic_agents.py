from __future__ import annotations

from dataclasses import dataclass

from runpod_inference_lab.common.llm_client import LLMCallResult, LLMClient


@dataclass(frozen=True)
class Agent:
    name: str
    system_prompt: str

    async def run(
        self,
        client: LLMClient,
        task: str,
        max_tokens: int,
        temperature: float,
    ) -> LLMCallResult:
        return await client.chat(
            system=self.system_prompt,
            prompt=task,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )


def build_default_agents() -> list[Agent]:
    return [
        Agent(
            "planner",
            "You are a practical planning agent. Produce concise implementation plans.",
        ),
        Agent(
            "architect",
            "You are an inference systems architect. Focus on components and tradeoffs.",
        ),
        Agent(
            "coder",
            "You are a careful Python engineer. Suggest simple, testable implementation details.",
        ),
        Agent(
            "reviewer",
            "You are a critical reviewer. Find missing pieces, risks, and weak assumptions.",
        ),
        Agent(
            "evaluator",
            "You are an evaluator. Score the solution from 1 to 5 and explain briefly.",
        ),
    ]
