#!/usr/bin/env bash
set -euo pipefail

export PROVIDER=${PROVIDER:-runpod}
export GPU_NAME=${GPU_NAME:-H200_141GB}
export GPU_MEMORY_GB=${GPU_MEMORY_GB:-141}
export ENGINE=${ENGINE:-vllm}
export OPENAI_BASE_URL=${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}
export OPENAI_API_KEY=${OPENAI_API_KEY:-dummy}
export RUN_TAG=${RUN_TAG:-h200-long-context}

echo "Running H200 long-context suite against the currently loaded model: ${MODEL_NAME:-unknown}"
echo "Start with concurrency 1. Increase only after results are clean."

uv run lab-long-context generate --target-tokens 8000 --target-tokens 32000 --needle-position beginning --needle-position middle --needle-position end
uv run lab-long-context run --prompt-file prompts/generated_long_context_tasks.jsonl --max-tasks 3 --max-tokens 1024
uv run lab-concurrency --prompt-file prompts/generated_long_context_tasks.jsonl --concurrency 1 --max-tasks 3 --max-tokens 1024
uv run lab-concurrency --prompt-file prompts/generated_long_context_tasks.jsonl --concurrency 3 --max-tasks 6 --max-tokens 1024
uv run lab-report --results-dir results --output-file reports/hardware_recommendation.md
