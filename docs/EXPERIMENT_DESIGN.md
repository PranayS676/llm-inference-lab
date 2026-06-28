# Experiment Design

Run controlled experiments. Change one major variable at a time.

## Core Matrix

| Experiment | Change | Keep Fixed | Teaches |
|---|---|---|---|
| Smoke | none | Qwen 4B, vLLM, A100 | Server/client wiring |
| Concurrency | 1, 3, 5, 10 | model, engine, prompts, GPU | Latency vs throughput |
| Model size | 4B, 14B, 32B | engine, prompts, GPU | Quality vs speed |
| Prompt category | simple, coding, RAG, function calling | model, engine, GPU | Workload difficulty |
| Context size | 8K, 32K, 64K, 128K | model, engine, GPU | KV-cache pressure |
| Engine | vLLM vs SGLang | model, prompts, GPU | Engine behavior |
| Agent shape | sequential vs concurrent | model, engine, GPU | Workflow latency vs fanout |
| Hardware | A100 vs H200 | model, engine, prompts | When H200 is worth it |

## Run Notes

For every experiment, record:

- hypothesis
- what changed
- what stayed fixed
- result summary
- surprising behavior
- next test

## Comparison Rule

Do not compare runs unless these match or are the specific variable under test:

- prompt file hash
- model and model revision
- engine and engine version
- GPU
- max model length
- dtype
- GPU memory utilization
- temperature
- max tokens
