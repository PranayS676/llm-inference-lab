# Troubleshooting

## Debug Order

```bash
nvidia-smi
python --version
uv --version
uv pip show vllm
bash servers/health_check.sh
uv run lab-single
uv run lab-batch --prompt-file prompts/simple_tasks.jsonl --max-tasks 3
uv run lab-concurrency --prompt-file prompts/simple_tasks.jsonl --concurrency 1 --max-tasks 5
```

## Common Failures

### Health Check Fails

- Confirm the server is still running.
- Confirm `OPENAI_BASE_URL` ends with `/v1`.
- Confirm `OPENAI_API_KEY` matches the server key.
- Confirm the RunPod port is exposed if calling from outside the pod.

### Model Does Not Load

- Check model name and Hugging Face access.
- Check disk space on the volume.
- Try Qwen 4B before 14B or 32B.

### Concurrency Fails

- Lower concurrency.
- Lower `MAX_MODEL_LEN`.
- Lower `GPU_MEMORY_UTILIZATION`.
- Use a smaller model.

### Results Look Wrong

- Confirm you restarted the server when changing models.
- Compare prompt file hashes.
- Check `run_tag`, `model`, `engine`, `gpu_name`, and `max_model_len` in result rows.
