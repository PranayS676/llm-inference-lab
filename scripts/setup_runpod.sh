#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update || true
sudo apt-get install -y git curl tmux htop nvtop jq || true

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

uv sync --locked

# Install one engine first. Keep SGLang for the comparison phase.
# The RunPod PyTorch 2.8 / CUDA 12.8 image needs a vLLM release that keeps
# Torch on the CUDA 12.x wheel line. Transformers is capped below 5 because
# vLLM 0.11.0 expects the Transformers 4 tokenizer API.
VLLM_VERSION="${VLLM_VERSION:-0.11.0}"
TRANSFORMERS_CONSTRAINT="${TRANSFORMERS_CONSTRAINT:-transformers>=4.55.2,<5}"
uv pip install "vllm==${VLLM_VERSION}" "${TRANSFORMERS_CONSTRAINT}"

# Install SGLang only when you are ready to compare engines.
# SGLang latest releases can pull newer CUDA/Torch stacks. For this RunPod
# PyTorch 2.8 / CUDA 12.8 image, keep SGLang on the Torch 2.8-compatible line.
# SGLANG_VERSION="${SGLANG_VERSION:-0.5.5.post3}"
# uv pip install "sglang==${SGLANG_VERSION}"

chmod +x servers/*.sh scripts/*.sh

echo "Setup complete. Use: source .venv/bin/activate"
