from __future__ import annotations

import asyncio
import time
from pathlib import Path

import typer
from rich import print

from runpod_inference_lab.agents.basic_agents import build_default_agents
from runpod_inference_lab.common.io import append_jsonl
from runpod_inference_lab.common.metadata import RunMetadata, prompt_file_metadata
from runpod_inference_lab.common.prompts import build_prompt, load_prompt_rows
from runpod_inference_lab.common.result_schema import build_result_row
from runpod_inference_lab.common.settings import Settings
from runpod_inference_lab.runners._shared import build_task_result, make_client, resolve_output_file

app = typer.Typer(help="Run a sequential multi-agent workflow against one endpoint.")


@app.command()
def main(
    prompt_file: Path = typer.Option(Path("prompts/agent_workflow_tasks.jsonl")),
    output_file: Path | None = typer.Option(None),
    max_tasks: int = 2,
    max_tokens: int = 700,
) -> None:
    async def run() -> None:
        settings = Settings.from_env()
        metadata = RunMetadata.create(settings)
        client = make_client(settings)
        agents = build_default_agents()
        tasks = load_prompt_rows(str(prompt_file), max_tasks=max_tasks)
        rows = []

        for task in tasks:
            original_task = build_prompt(task)
            context = original_task
            started = time.perf_counter()
            for sequence, agent in enumerate(agents, start=1):
                result = await agent.run(
                    client=client,
                    task=context,
                    max_tokens=max_tokens,
                    temperature=settings.temperature,
                )
                rows.append(
                    build_task_result(
                        metadata=metadata,
                        settings=settings,
                        run_type="agent_sequential_detail",
                        task_row=task,
                        prompt=context,
                        result=result.to_dict(),
                        prompt_file=prompt_file,
                        concurrency=1,
                        max_tokens=max_tokens,
                        extra={"agent": agent.name, "agent_sequence": sequence},
                    )
                )
                context = (
                    f"Original task:\n{original_task}\n\n"
                    f"Previous agent ({agent.name}) output:\n{result.response}\n\n"
                    "Continue the workflow and improve the answer."
                )

            workflow_latency_ms = (time.perf_counter() - started) * 1000
            rows.append(
                build_result_row(
                    metadata,
                    run_type="agent_sequential_summary",
                    task_id=task.get("id"),
                    category=task.get("category"),
                    concurrency=1,
                    temperature=settings.temperature,
                    max_tokens=max_tokens,
                    success=True,
                    error=None,
                    workflow_latency_ms=workflow_latency_ms,
                    agent_count=len(agents),
                    **prompt_file_metadata(prompt_file),
                )
            )

        written = append_jsonl(
            resolve_output_file(settings, output_file, "agent_workflow_results.jsonl"),
            rows,
        )
        print(f"Wrote {len(rows)} rows to {written}")

    asyncio.run(run())


if __name__ == "__main__":
    app()
