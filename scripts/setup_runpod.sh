#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update || true
sudo apt-get install -y git curl tmux htop nvtop jq || true

python -m pip install --upgrade pip uv
uv sync

# Install one engine first. Keep SGLang for the comparison phase.
uv pip install vllm

# Install SGLang only when you are ready to compare engines.
# uv pip install "sglang[all]"

chmod +x servers/*.sh scripts/*.sh

echo "Setup complete. Use: source .venv/bin/activate"
