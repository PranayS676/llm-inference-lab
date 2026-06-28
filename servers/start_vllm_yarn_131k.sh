#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME=${MODEL_NAME:-Qwen/Qwen3-14B}
PORT=${PORT:-8000}
API_KEY=${OPENAI_API_KEY:-dummy}

python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_NAME" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --dtype auto \
  --max-model-len 131072 \
  --rope-scaling '{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768}' \
  --gpu-memory-utilization 0.90 \
  --api-key "$API_KEY"
