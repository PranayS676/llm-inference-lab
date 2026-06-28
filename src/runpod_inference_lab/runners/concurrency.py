from __future__ import annotations

import asyncio
import statistics
import time
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path
from typing import Any, TypeVar

import typer
from rich import print

from runpod_inference_lab.common.gpu import read_nvidia_smi
from runpod_inference_lab.common.io import append_jsonl
from runpod_inference_lab.common.metadata import RunMetadata, prompt_file_metadata
from runpod_inference_lab.common.prompts import build_prompt, load_prompt_rows
from runpod_inference_lab.common.result_schema import build_result_row
from runpod_inference_lab.common.settings import Settings
from runpod_inference_lab.evals.combined import evaluate_task
from runpod_inference_lab.runners._shared import build_task_result, make_client, resolve_output_file

app = typer.Typer(help="Run concurrent requests against one loaded model endpoint.")

T = TypeVar("T")
R = TypeVar("R")


async def run_with_concurrency_limit(
    items: Sequence[T],
    concurrency: int,
    worker: Callable[[int, T], Awaitable[R]],
) -> list[R]:
    semaphore = asyncio.Semaphore(concurrency)

    async def wrapped(index: int, item: T) -> R:
        async with semaphore:
            return await worker(index, item)

    return await asyncio.gather(*[wrapped(index, item) for index, item in enumerate(items)])


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((percent / 100) * (len(ordered) - 1)))))
    return ordered[index]


@app.command()
def main(
    prompt_file: Path = typer.Option(Path("prompts/simple_tasks.jsonl")),
    output_file: Path | None = typer.Option(None),
    concurrency: int = 5,
    max_tasks: int = 50,
    max_tokens: int = 512,
) -> None:
    async def run() -> None:
        settings = Settings.from_env()
        metadata = RunMetadata.create(settings)
        client = make_client(settings)
        tasks = load_prompt_rows(str(prompt_file), max_tasks=max_tasks, repeat=True)
        gpu_before = read_nvidia_smi()

        async def one(index: int, task: dict[str, Any]) -> dict[str, Any]:
            prompt = build_prompt(task)
            result = await client.chat(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=settings.temperature,
                stream=True,
            )
            payload = result.to_dict()
            payload.update(evaluate_task(task, result.response))
            return build_task_result(
                metadata=metadata,
                settings=settings,
                run_type="concurrency_detail",
                task_row=task,
                prompt=prompt,
                result=payload,
                prompt_file=prompt_file,
                concurrency=concurrency,
                max_tokens=max_tokens,
                extra={"request_index": index},
            )

        started = time.perf_counter()
        rows = await run_with_concurrency_limit(tasks, concurrency, one)
        suite_latency_seconds = time.perf_counter() - started
        gpu_after = read_nvidia_smi()

        latencies = [row["latency_ms"] for row in rows]
        error_count = sum(1 for row in rows if not row["success"])
        summary = build_result_row(
            metadata,
            run_type="concurrency_summary",
            task_id="summary",
            category="summary",
            concurrency=concurrency,
            temperature=settings.temperature,
            max_tokens=max_tokens,
            success=error_count == 0,
            error=None if error_count == 0 else f"{error_count} request(s) failed",
            total_tasks=len(rows),
            success_count=len(rows) - error_count,
            error_count=error_count,
            suite_latency_ms=suite_latency_seconds * 1000,
            requests_per_second=len(rows) / max(suite_latency_seconds, 1e-9),
            p50_latency_ms=statistics.median(latencies) if latencies else None,
            p95_latency_ms=percentile(latencies, 95),
            p99_latency_ms=percentile(latencies, 99),
            gpu_before=gpu_before,
            gpu_after=gpu_after,
            **prompt_file_metadata(prompt_file),
        )

        written = append_jsonl(
            resolve_output_file(settings, output_file, "concurrency_results.jsonl"),
            rows + [summary],
        )
        print(summary)
        print(f"Wrote {len(rows)} detail rows + 1 summary row to {written}")

    asyncio.run(run())


if __name__ == "__main__":
    app()
