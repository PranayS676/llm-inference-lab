# A100 Benchmark Manifest

Experiment ID: a100-20260628T202440Z

Official tags:
- a100-vllm-qwen3-4b-official
- a100-vllm-qwen3-14b-official
- a100-vllm-qwen3-32b-official
- a100-sglang-qwen3-4b-official
- a100-sglang-qwen3-14b-official

Artifacts:
- results/*.jsonl raw result rows
- reports/hardware_recommendation_all.md final combined report
- reports/concurrency_summary.csv concurrency grouped summary
- reports/result_counts.csv row counts by run tag and run type
- logs/*.log server and benchmark logs
- package_versions*.txt dependency snapshots
- nvidia_smi_*.txt GPU snapshots
