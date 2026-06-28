from __future__ import annotations

import asyncio
import statistics
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

app = typer.Typer(help="Run concurrent agent fanout against one shared endpoint.")


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

            async def one_agent(sequence_and_agent, task_row=task, base_task=original_task):
                sequence, agent = sequence_and_agent
                prompt = f"Agent role: {agent.name}\n\nTask:\n{base_task}"
                result = await agent.run(
                    client=client,
                    task=prompt,
                    max_tokens=max_tokens,
                    temperature=settings.temperature,
                )
                return build_task_result(
                    metadata=metadata,
                    settings=settings,
                    run_type="agent_concurrent_detail",
                    task_row=task_row,
                    prompt=prompt,
                    result=result.to_dict(),
                    prompt_file=prompt_file,
                    concurrency=len(agents),
                    max_tokens=max_tokens,
                    extra={"agent": agent.name, "agent_sequence": sequence},
                )

            started = time.perf_counter()
            task_rows = await asyncio.gather(
                *[one_agent(item) for item in enumerate(agents, start=1)]
            )
            workflow_latency_ms = (time.perf_counter() - started) * 1000
            rows.extend(task_rows)
            latencies = [row["latency_ms"] for row in task_rows]
            errors = sum(1 for row in task_rows if not row["success"])
            rows.append(
                build_result_row(
                    metadata,
                    run_type="agent_concurrent_summary",
                    task_id=task.get("id"),
                    category=task.get("category"),
                    concurrency=len(agents),
                    temperature=settings.temperature,
                    max_tokens=max_tokens,
                    success=errors == 0,
                    error=None if errors == 0 else f"{errors} agent request(s) failed",
                    workflow_latency_ms=workflow_latency_ms,
                    agent_count=len(agents),
                    success_count=len(agents) - errors,
                    error_count=errors,
                    p50_latency_ms=statistics.median(latencies) if latencies else None,
                    **prompt_file_metadata(prompt_file),
                )
            )

        written = append_jsonl(
            resolve_output_file(settings, output_file, "agent_concurrent_results.jsonl"),
            rows,
        )
        print(f"Wrote {len(rows)} rows to {written}")

    asyncio.run(run())


if __name__ == "__main__":
    app()
