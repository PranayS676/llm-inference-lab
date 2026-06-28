# H200 Long Context Runbook

Use H200 after A100 tests are clean.

## Start Server

```bash
export MODEL_NAME=Qwen/Qwen3-14B
export OPENAI_API_KEY=dummy
export MAX_MODEL_LEN=131072
export GPU_NAME=H200_141GB
export GPU_MEMORY_GB=141
bash servers/start_vllm_yarn_131k.sh
```

## Validate First

```bash
bash servers/health_check.sh
uv run lab-single
```

## Generate Long Context Tasks

```bash
uv run lab-long-context generate \
  --target-tokens 8000 \
  --target-tokens 32000 \
  --target-tokens 64000 \
  --needle-position beginning \
  --needle-position middle \
  --needle-position end
```

## Run Safely

```bash
uv run lab-long-context run --prompt-file prompts/generated_long_context_tasks.jsonl --max-tasks 3
uv run lab-concurrency --prompt-file prompts/generated_long_context_tasks.jsonl --concurrency 1 --max-tasks 3
uv run lab-concurrency --prompt-file prompts/generated_long_context_tasks.jsonl --concurrency 3 --max-tasks 6
```

Do not start with concurrency 10 on long context. KV cache memory can grow quickly.
