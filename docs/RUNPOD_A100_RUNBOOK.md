# RunPod A100 Runbook

## Pod Setup

Use:

- A100 80GB
- PyTorch/CUDA template
- 200GB-500GB persistent volume
- HTTP port 8000 for vLLM
- HTTP port 30000 for SGLang later
- SSH enabled

## Install

```bash
cd /workspace
git clone https://github.com/PranayS676/llm-inference-lab.git
cd llm-inference-lab
bash scripts/setup_runpod.sh
source .venv/bin/activate
```

The setup script defaults to `VLLM_VERSION=0.11.0` because that release keeps
Torch on the 2.8 / CUDA 12.x wheel line used by the RunPod PyTorch 2.8 image.
It also defaults to `TRANSFORMERS_CONSTRAINT=transformers>=4.55.2,<5` because
vLLM 0.11.0 expects the Transformers 4 tokenizer API. Do not run an unpinned
`uv pip install vllm` on this pod image unless you are also upgrading the image,
driver, and compatibility pins together.

## Start Qwen 4B

```bash
export MODEL_NAME=Qwen/Qwen3-4B
export OPENAI_API_KEY=dummy
export MAX_MODEL_LEN=32768
export GPU_MEMORY_UTILIZATION=0.90
bash servers/start_vllm.sh
```

## Validate

Second terminal:

```bash
cd /workspace/llm-inference-lab
source .venv/bin/activate
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=dummy
export MODEL_NAME=Qwen/Qwen3-4B
export GPU_NAME=A100_80GB
export GPU_MEMORY_GB=80
export ENGINE=vllm
export CHAT_TEMPLATE_ENABLE_THINKING=false

nvidia-smi
bash servers/health_check.sh
uv run lab-single
uv run lab-batch --prompt-file prompts/simple_tasks.jsonl --max-tasks 3
uv run lab-concurrency --prompt-file prompts/simple_tasks.jsonl --concurrency 1 --max-tasks 5
```

## Baseline

```bash
bash scripts/run_a100_baseline.sh
```

## Switch Models

```bash
bash servers/stop_servers.sh
export MODEL_NAME=Qwen/Qwen3-14B
bash servers/start_vllm.sh
```

Run health check and smoke test again before the full baseline.
