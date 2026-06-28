#!/usr/bin/env bash
set -euo pipefail

export OPENAI_BASE_URL=${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}
export OPENAI_API_KEY=${OPENAI_API_KEY:-dummy}
export RUN_TAG=${RUN_TAG:-a100-loaded-model-baseline}

echo "Running A100 baseline against the currently loaded model: ${MODEL_NAME:-unknown}"
echo "To benchmark another model, stop the server and restart it with a new MODEL_NAME."

uv run lab-single --max-tokens 256
uv run lab-batch --prompt-file prompts/simple_tasks.jsonl --max-tasks 10 --max-tokens 256
uv run lab-batch --prompt-file prompts/coding_tasks.jsonl --max-tasks 10 --max-tokens 512
uv run lab-batch --prompt-file prompts/rag_tasks.jsonl --max-tasks 10 --max-tokens 512
uv run lab-batch --prompt-file prompts/function_calling_tasks.jsonl --max-tasks 10 --max-tokens 512

uv run lab-concurrency --prompt-file prompts/simple_tasks.jsonl --concurrency 1 --max-tasks 10 --max-tokens 256
uv run lab-concurrency --prompt-file prompts/simple_tasks.jsonl --concurrency 5 --max-tasks 25 --max-tokens 256
uv run lab-concurrency --prompt-file prompts/simple_tasks.jsonl --concurrency 10 --max-tasks 50 --max-tokens 256

uv run lab-agent-workflow --prompt-file prompts/agent_workflow_tasks.jsonl --max-tasks 2 --max-tokens 700
uv run lab-agent-concurrent --prompt-file prompts/agent_workflow_tasks.jsonl --max-tasks 2 --max-tokens 700
uv run lab-report --results-dir results --output-file reports/hardware_recommendation.md
