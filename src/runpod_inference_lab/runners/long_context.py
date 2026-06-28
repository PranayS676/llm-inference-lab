from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich import print

from runpod_inference_lab.common.io import append_jsonl, write_jsonl
from runpod_inference_lab.common.metadata import RunMetadata
from runpod_inference_lab.common.prompts import build_prompt
from runpod_inference_lab.common.settings import Settings
from runpod_inference_lab.common.tokens import estimate_tokens
from runpod_inference_lab.evals.combined import evaluate_task
from runpod_inference_lab.runners._shared import build_task_result, make_client

app = typer.Typer(help="Generate and run synthetic long-context needle tasks.")


def make_long_context_task(target_tokens: int, needle_position: str) -> dict:
    sentence = (
        "This synthetic benchmark paragraph discusses LLM inference, GPU memory, "
        "KV cache pressure, batching, and multi-agent endpoint traffic. "
    )
    expected = f"needle-{target_tokens}-{needle_position}"
    needle = f"Important hidden fact: the retrieval code is {expected}. "
    repeat_count = max(1, int((target_tokens * 4) / len(sentence)))
    paragraphs = [sentence for _ in range(repeat_count)]
    if needle_position == "beginning":
        insert_at = 0
    elif needle_position == "middle":
        insert_at = len(paragraphs) // 2
    else:
        insert_at = len(paragraphs)
    paragraphs.insert(insert_at, needle)
    context = "".join(paragraphs)
    return {
        "id": f"long_{target_tokens}_{needle_position}",
        "category": "long_context",
        "context": context,
        "prompt": "What is the retrieval code from the hidden fact?",
        "expected_answer": expected,
        "target_context_tokens": target_tokens,
        "needle_position": needle_position,
    }


@app.command("generate")
def generate(
    output_file: Annotated[Path, typer.Option()] = Path(
        "prompts/generated_long_context_tasks.jsonl"
    ),
    target_tokens: Annotated[list[int] | None, typer.Option("--target-tokens")] = None,
    needle_position: Annotated[list[str] | None, typer.Option("--needle-position")] = None,
) -> None:
    target_tokens = target_tokens or [8000, 32000]
    needle_position = needle_position or ["beginning", "middle", "end"]
    rows = [
        make_long_context_task(tokens, position)
        for tokens in target_tokens
        for position in needle_position
    ]
    written = write_jsonl(output_file, rows)
    print(f"Wrote {len(rows)} generated prompts to {written}")


@app.command("run")
def run_generated(
    prompt_file: Path = typer.Option(Path("prompts/generated_long_context_tasks.jsonl")),
    output_file: Path = typer.Option(Path("results/long_context_results.jsonl")),
    max_tasks: int = 3,
    max_tokens: int = 1024,
) -> None:
    from runpod_inference_lab.common.prompts import load_prompt_rows

    async def run() -> None:
        settings = Settings.from_env()
        metadata = RunMetadata.create(settings)
        client = make_client(settings)
        tasks = load_prompt_rows(str(prompt_file), max_tasks=max_tasks)
        rows = []
        for task in tasks:
            prompt = build_prompt(task)
            result = await client.chat(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=settings.temperature,
                stream=True,
            )
            payload = result.to_dict()
            payload.update(evaluate_task(task, result.response))
            rows.append(
                build_task_result(
                    metadata=metadata,
                    settings=settings,
                    run_type="long_context",
                    task_row=task,
                    prompt=prompt,
                    result=payload,
                    prompt_file=prompt_file,
                    concurrency=1,
                    max_tokens=max_tokens,
                    extra={
                        "target_context_tokens": task.get("target_context_tokens"),
                        "needle_position": task.get("needle_position"),
                        "estimated_prompt_tokens": estimate_tokens(prompt),
                    },
                )
            )
        written = append_jsonl(output_file, rows)
        print(f"Wrote {len(rows)} rows to {written}")

    asyncio.run(run())


if __name__ == "__main__":
    app()
