from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.progress import track

from runpod_inference_lab.common.gpu import read_nvidia_smi
from runpod_inference_lab.common.io import append_jsonl
from runpod_inference_lab.common.metadata import RunMetadata
from runpod_inference_lab.common.prompts import build_prompt, load_prompt_rows
from runpod_inference_lab.common.settings import Settings
from runpod_inference_lab.evals.combined import evaluate_task
from runpod_inference_lab.runners._shared import build_task_result, make_client

app = typer.Typer(help="Run a prompt file sequentially against the configured endpoint.")


@app.command()
def main(
    prompt_file: Path = typer.Option(Path("prompts/simple_tasks.jsonl")),
    output_file: Path = typer.Option(Path("results/batch_results.jsonl")),
    max_tasks: int = 50,
    max_tokens: int = 512,
) -> None:
    async def run() -> None:
        settings = Settings.from_env()
        metadata = RunMetadata.create(settings)
        client = make_client(settings)
        tasks = load_prompt_rows(str(prompt_file), max_tasks=max_tasks)
        rows = []

        for task in track(tasks, description="Running batch prompts"):
            prompt = build_prompt(task)
            gpu_before = read_nvidia_smi()
            result = await client.chat(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=settings.temperature,
                stream=True,
            )
            gpu_after = read_nvidia_smi()
            payload = result.to_dict()
            payload.update(evaluate_task(task, result.response))
            rows.append(
                build_task_result(
                    metadata=metadata,
                    settings=settings,
                    run_type="batch",
                    task_row=task,
                    prompt=prompt,
                    result=payload,
                    prompt_file=prompt_file,
                    concurrency=1,
                    max_tokens=max_tokens,
                    gpu_before=gpu_before,
                    gpu_after=gpu_after,
                )
            )

        written = append_jsonl(output_file, rows)
        print(f"Wrote {len(rows)} rows to {written}")

    asyncio.run(run())


if __name__ == "__main__":
    app()
