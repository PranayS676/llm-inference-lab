# LLM Inference Lab

A RunPod-first lab for learning and benchmarking OpenAI-compatible LLM inference.

The project is designed to answer one practical question:

> Which GPU, model, inference engine, and server configuration is best for a 5-10 agent workload?

It is not a chatbot app. It is an inference experimentation harness for vLLM first, SGLang second, Qwen models first, and A100 before H200.

## What This Lab Teaches

- TTFT and streaming latency
- Output tokens/sec and request throughput
- Concurrency effects at 1, 3, 5, 10, and higher
- KV-cache pressure from long context
- Model size tradeoffs: 4B vs 14B vs 32B
- Engine behavior: vLLM vs SGLang
- Sequential agent latency vs concurrent agent fanout
- Cost per successful/acceptable task once GPU prices are added

## Repository Layout

```text
src/runpod_inference_lab/   Python package
configs/                    Model, GPU, benchmark, and engine configs
prompts/                    JSONL task suites
servers/                    vLLM/SGLang start, health, and stop scripts
scripts/                    A100/H200 benchmark scripts
tests/                      Local tests that do not need a GPU
docs/                       RunPod runbooks and experiment guidance
results/                    Raw JSONL output, ignored except .gitkeep
reports/                    Generated reports, ignored except .gitkeep
```

## Local Setup

Install `uv`, then:

```powershell
uv sync --group dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The local tests use fake data and do not require a GPU or model server.

## Environment

Copy `.env.example` to `.env` if you want local defaults:

```bash
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
OPENAI_API_KEY=dummy
MODEL_NAME=Qwen/Qwen3-4B
PROVIDER=runpod
GPU_NAME=A100_80GB
ENGINE=vllm
RUN_TAG=dev
CHAT_TEMPLATE_ENABLE_THINKING=false
```

Do not commit real API keys.

## RunPod A100 Quick Start

On the pod:

```bash
cd /workspace
git clone https://github.com/PranayS676/llm-inference-lab.git
cd llm-inference-lab
bash scripts/setup_runpod.sh
source .venv/bin/activate
```

`setup_runpod.sh` pins vLLM to a Torch 2.8-compatible release for the RunPod
PyTorch 2.8 / CUDA 12.8 image and caps Transformers below 5 for vLLM tokenizer
compatibility. Override `VLLM_VERSION` or `TRANSFORMERS_CONSTRAINT` only when
you are intentionally testing a newer RunPod image or driver.

Start vLLM:

```bash
export MODEL_NAME=Qwen/Qwen3-4B
export OPENAI_API_KEY=dummy
export MAX_MODEL_LEN=32768
bash servers/start_vllm.sh
```

In a second terminal:

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

bash servers/health_check.sh
uv run lab-single
bash scripts/run_a100_baseline.sh
```

## Model Switching Rule

One loaded model equals one server run.

Do not compare Qwen 4B, 14B, and 32B by changing only `MODEL_NAME` in the client shell. To benchmark a different model:

```bash
bash servers/stop_servers.sh
export MODEL_NAME=Qwen/Qwen3-14B
bash servers/start_vllm.sh
bash servers/health_check.sh
uv run lab-single
bash scripts/run_a100_baseline.sh
```

## Main Commands

```bash
uv run lab-single
uv run lab-batch --prompt-file prompts/simple_tasks.jsonl --max-tasks 10
uv run lab-concurrency --prompt-file prompts/simple_tasks.jsonl --concurrency 5 --max-tasks 25
uv run lab-agent-workflow --max-tasks 2
uv run lab-agent-concurrent --max-tasks 2
uv run lab-long-context generate --target-tokens 8000 --target-tokens 32000
uv run lab-long-context run --prompt-file prompts/generated_long_context_tasks.jsonl
uv run lab-summarize --input-file results/concurrency_results.jsonl --output-csv results/summary.csv
uv run lab-report --results-dir results --output-file reports/hardware_recommendation.md
```

## Result Policy

Raw result files are append-only JSONL. They are ignored by git by default:

```text
results/*.jsonl
reports/*.md
reports/*.csv
```

Commit small prompt files and configs. Do not commit real benchmark outputs unless they are intentionally sanitized examples.

## Documentation

- [Experiment Design](docs/EXPERIMENT_DESIGN.md)
- [RunPod A100 Runbook](docs/RUNPOD_A100_RUNBOOK.md)
- [H200 Long Context Runbook](docs/H200_LONG_CONTEXT_RUNBOOK.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
