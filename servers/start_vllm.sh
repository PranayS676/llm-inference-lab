#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME=${MODEL_NAME:-Qwen/Qwen3-14B}
PORT=${PORT:-8000}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-32768}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}
DTYPE=${DTYPE:-auto}
API_KEY=${OPENAI_API_KEY:-dummy}

echo "Starting vLLM"
echo "MODEL_NAME=$MODEL_NAME"
echo "PORT=$PORT"
echo "MAX_MODEL_LEN=$MAX_MODEL_LEN"

python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_NAME" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_MODEL_LEN" \
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
  --api-key "$API_KEY"
