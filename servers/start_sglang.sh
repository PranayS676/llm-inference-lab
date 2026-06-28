#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME=${MODEL_NAME:-Qwen/Qwen3-14B}
PORT=${PORT:-30000}
MAX_TOTAL_TOKENS=${MAX_TOTAL_TOKENS:-32768}

python -m sglang.launch_server \
  --model-path "$MODEL_NAME" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --context-length "$MAX_TOTAL_TOKENS"
