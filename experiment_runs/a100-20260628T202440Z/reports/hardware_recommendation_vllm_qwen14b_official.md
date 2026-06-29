# LLM Inference Lab Report

## Overview

- Total result rows: 278
- Successful rows: 278
- Failed rows: 0

## Grouped Summary

| model          | engine   | gpu_name   | category         |   concurrency |   count |   success_rate |   avg_latency_ms |   p50_latency_ms |   avg_ttft_ms |   avg_tokens_per_second |   avg_input_tokens |   avg_output_tokens |   json_valid_rate |   contains_expected_rate |
|:---------------|:---------|:-----------|:-----------------|--------------:|--------:|---------------:|-----------------:|-----------------:|--------------:|------------------------:|-------------------:|--------------------:|------------------:|-------------------------:|
| Qwen/Qwen3-14B | vllm     | A100_80GB  | architecture     |             1 |       1 |              1 |       10087.9    |       10087.9    |       52.8644 |                42.5261  |               31   |            429      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | classification   |             1 |       4 |              1 |          77.4421 |          78.4785 |       57.5958 |                12.9348  |               39   |              1      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | classification   |             3 |       5 |              1 |          96.4678 |          81.6871 |       74.9054 |                11.0923  |               39   |              1      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | classification   |             5 |       8 |              1 |         105.759  |          78.9205 |       82.4532 |                11.0045  |               39   |              1      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | classification   |            10 |      17 |              1 |         131.862  |         107.956  |      111.618  |                 9.0561  |               39   |              1      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | coding           |             1 |       1 |              1 |        7229.34   |        7229.34   |     1837.57   |                34.7196  |               27   |            251      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | debugging        |             1 |       1 |              1 |        7306      |        7306      |       54.2456 |                49.0008  |               29   |            358      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | function_calling |             1 |       2 |              1 |        2232.54   |        2232.54   |      976.279  |                21.0914  |               34   |             40      |                 1 |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | json_extraction  |             1 |       5 |              1 |        1568.52   |         855.713  |      785.392  |                24.0052  |               35   |             28      |                 1 |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | json_extraction  |             3 |       5 |              1 |        1280.89   |         866.487  |      493.287  |                28.0542  |               35   |             28      |                 1 |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | json_extraction  |             5 |       9 |              1 |        1055.09   |         853.856  |      254.094  |                29.9841  |               35   |             28      |                 1 |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | json_extraction  |            10 |      17 |              1 |        1051.38   |         909.426  |      220.977  |                28.7183  |               35   |             28      |                 1 |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | multi_agent      |             1 |      10 |              1 |       14070.5    |       13936.3    |      304.319  |                51.6479  |              650.8 |            726.2    |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | multi_agent      |             5 |      10 |              1 |       11980.7    |       14052.8    |      371.849  |                50.2419  |               42.2 |            588.8    |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | rag              |             1 |       2 |              1 |        1610.43   |        1610.43   |     1143.92   |                27.3107  |               51   |             24.5    |               nan |                        0 |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | single           |             1 |       1 |              1 |        4496.07   |        4496.07   |     3849.48   |                 4.22591 |               20   |             19      |                 1 |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | summarization    |             1 |       4 |              1 |        1966.33   |        1964.09   |       59.2993 |                49.8397  |               46   |             98      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | summarization    |             3 |       5 |              1 |        1981.71   |        1965.27   |       80.6764 |                48.9643  |               46   |             97      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | summarization    |             5 |       8 |              1 |        2015.06   |        1996.93   |       71.6231 |                48.6591  |               46   |             98      |               nan |                      nan |
| Qwen/Qwen3-14B | vllm     | A100_80GB  | summarization    |            10 |      16 |              1 |        2105.22   |        2077.43   |      110.011  |                46.4671  |               46   |             97.6875 |               nan |                      nan |

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
