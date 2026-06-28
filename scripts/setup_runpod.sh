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
# Torch on the CUDA 12.x wheel line. Newer unpinned vLLM releases can pull
# CUDA 13 wheels and fail on A100 pods with CUDA 12.8 drivers.
VLLM_VERSION="${VLLM_VERSION:-0.11.0}"
uv pip install "vllm==${VLLM_VERSION}"

# Install SGLang only when you are ready to compare engines.
# uv pip install "sglang[all]"

chmod +x servers/*.sh scripts/*.sh

echo "Setup complete. Use: source .venv/bin/activate"
