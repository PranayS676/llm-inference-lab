#!/usr/bin/env bash
set -euo pipefail

echo "Stopping common vLLM/SGLang server processes for this pod user."
pkill -f "vllm.entrypoints.openai.api_server" || true
pkill -f "vllm serve" || true
pkill -f "sglang.launch_server" || true
echo "Stop signal sent."
