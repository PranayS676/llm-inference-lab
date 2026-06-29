# LLM Inference Lab Report

## Overview

- Total result rows: 139
- Successful rows: 139
- Failed rows: 0

## Grouped Summary

| model         | engine   | gpu_name   | category         |   concurrency |   count |   success_rate |   avg_latency_ms |   p50_latency_ms |   avg_ttft_ms |   avg_tokens_per_second |   avg_input_tokens |   avg_output_tokens |   json_valid_rate |   contains_expected_rate |
|:--------------|:---------|:-----------|:-----------------|--------------:|--------:|---------------:|-----------------:|-----------------:|--------------:|------------------------:|-------------------:|--------------------:|------------------:|-------------------------:|
| Qwen/Qwen3-4B | vllm     | A100_80GB  | architecture     |             1 |       1 |              1 |        3958.87   |        3958.87   |       47.8138 |               117.458   |               31   |             465     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | classification   |             1 |       4 |              1 |          52.9249 |          53.962  |       45.1739 |                18.9459  |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | classification   |             3 |       5 |              1 |          76.8079 |          66.0891 |       69.4612 |                14.0552  |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | classification   |             5 |       8 |              1 |          92.0498 |          74.4644 |       78.5282 |                13.3448  |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | classification   |            10 |      17 |              1 |          96.4139 |          82.5616 |       85.4973 |                13.2187  |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | coding           |             1 |       1 |              1 |        3879.02   |        3879.02   |     1894.92   |                64.1915  |               27   |             249     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | debugging        |             1 |       1 |              1 |        3056.96   |        3056.96   |       48.4771 |               124.634   |               29   |             381     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | function_calling |             1 |       2 |              1 |        1387.02   |        1387.02   |      916.642  |                43.3347  |               34   |              38.5   |                 1 |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | json_extraction  |             1 |       5 |              1 |        1047.59   |         354.26   |      739.47   |                53.0512  |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | json_extraction  |             3 |       5 |              1 |         675.111  |         381.19   |      355.199  |                61.9793  |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | json_extraction  |             5 |       9 |              1 |         587.202  |         369.484  |      269.815  |                66.6918  |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | json_extraction  |            10 |      17 |              1 |         535.668  |         412.03   |      201      |                63.6153  |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | multi_agent      |             1 |      10 |              1 |        4908.68   |        5419.95   |      227.45   |               139.848   |              656.5 |             666.6   |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | multi_agent      |             5 |      10 |              1 |        5276.69   |        5696.37   |      347.859  |               122.968   |               42.2 |             624.9   |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | rag              |             1 |       2 |              1 |        1332.17   |        1332.17   |     1160.08   |                62.4395  |               51   |              23.5   |               nan |                        0 |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | single           |             1 |       1 |              1 |        2290.59   |        2290.59   |     2057.49   |                 6.98511 |               20   |              16     |                 1 |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | summarization    |             1 |       4 |              1 |         535.49   |         535.771  |       45.7246 |               125.119   |               46   |              67     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | summarization    |             3 |       5 |              1 |         570.525  |         553.206  |       66.7741 |               117.786   |               46   |              67     |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | summarization    |             5 |       8 |              1 |         578.404  |         561.055  |       71.8652 |               116.084   |               46   |              66.875 |               nan |                      nan |
| Qwen/Qwen3-4B | vllm     | A100_80GB  | summarization    |            10 |      16 |              1 |         612.692  |         596.152  |       90.2314 |               110.616   |               46   |              67     |               nan |                      nan |

## Learning Notes

- Compare rows only when model, engine, GPU, prompt file, and server config match.
- Treat client-side token counts as estimates until engine-native metrics are added.
- If p95 latency rises sharply with concurrency, inspect queueing and KV cache pressure.
- If quality improves with a larger model, compare that gain against latency and cost.

## Recommendation Template

Fill this in after real RunPod runs:

- Best simple/routing model:
- Best balanced agent model:
- Best coding/reasoning model:
- Best long-context GPU/model:
- Configuration to avoid:
