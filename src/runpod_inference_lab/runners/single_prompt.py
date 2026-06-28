from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich import print

from runpod_inference_lab.common.gpu import read_nvidia_smi
from runpod_inference_lab.common.io import append_jsonl
from runpod_inference_lab.common.metadata import RunMetadata
from runpod_inference_lab.common.settings import Settings
from runpod_inference_lab.evals.combined import evaluate_task
from runpod_inference_lab.runners._shared import build_task_result, make_client, resolve_output_file

app = typer.Typer(help="Run one prompt against the configured OpenAI-compatible endpoint.")


@app.command()
def main(
    prompt: str = (
        "Extract name, company, and date as valid JSON: Pranay spoke with NVIDIA on June 28."
    ),
    output_file: Path | None = typer.Option(None),
    max_tokens: int = 256,
    expected_type: str = "json",
) -> None:
    async def run() -> None:
        settings = Settings.from_env()
        metadata = RunMetadata.create(settings)
        client = make_client(settings)
        task = {"id": "single_prompt", "category": "single", "expected_type": expected_type}

        gpu_before = read_nvidia_smi()
        result = await client.chat(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=settings.temperature,
            stream=True,
        )
        gpu_after = read_nvidia_smi()

        result_payload = result.to_dict()
        result_payload.update(evaluate_task(task, result.response))
        row = build_task_result(
            metadata=metadata,
            settings=settings,
            run_type="single_prompt",
            task_row=task,
            prompt=prompt,
            result=result_payload,
            prompt_file=None,
            concurrency=1,
            max_tokens=max_tokens,
            gpu_before=gpu_before,
            gpu_after=gpu_after,
        )
        written = append_jsonl(
            resolve_output_file(settings, output_file, "single_prompt_results.jsonl"), [row]
        )
        print(f"Wrote 1 row to {written}")
        print({"success": row["success"], "latency_ms": row["latency_ms"], "error": row["error"]})

    asyncio.run(run())


if __name__ == "__main__":
    app()
