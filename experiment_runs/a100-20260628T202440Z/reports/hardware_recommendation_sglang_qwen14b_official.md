# LLM Inference Lab Report

## Overview

- Total result rows: 696
- Successful rows: 696
- Failed rows: 0

## Grouped Summary

| model          | engine   | gpu_name   | category         |   concurrency |   count |   success_rate |   avg_latency_ms |   p50_latency_ms |   avg_ttft_ms |   avg_tokens_per_second |   avg_input_tokens |   avg_output_tokens |   json_valid_rate |   contains_expected_rate |
|:---------------|:---------|:-----------|:-----------------|--------------:|--------:|---------------:|-----------------:|-----------------:|--------------:|------------------------:|-------------------:|--------------------:|------------------:|-------------------------:|
| Qwen/Qwen3-14B | sglang   | A100_80GB  | architecture     |             1 |       1 |              1 |        9879.72   |        9879.72   |       38.6227 |                 52.8355 |               31   |             522     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | classification   |             1 |       4 |              1 |          58.0628 |          58.0173 |       39.6047 |                 17.2501 |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | classification   |             3 |       5 |              1 |         108.025  |          76.7521 |       87.4529 |                 10.7784 |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | classification   |             5 |       8 |              1 |          92.9055 |          84.745  |       74.1425 |                 11.2717 |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | classification   |            10 |      17 |              1 |         102.343  |          93.0025 |       79.031  |                 10.329  |               39   |               1     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | coding           |             1 |       1 |              1 |        6104.23   |        6104.23   |      825.983  |                 41.119  |               27   |             251     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | debugging        |             1 |       1 |              1 |        7403.52   |        7403.52   |       41.2797 |                 49.4359 |               29   |             366     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | function_calling |             1 |       2 |              1 |        1770.04   |        1770.04   |      546.485  |                 24.4438 |               34   |              40     |                 1 |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | json_extraction  |             1 |       5 |              1 |        1276.41   |         806.243  |      514.048  |                 26.5601 |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | json_extraction  |             3 |       5 |              1 |        1083      |         817.933  |      293.968  |                 29.8646 |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | json_extraction  |             5 |       9 |              1 |        1011.97   |         894.016  |      200.579  |                 29.7998 |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | json_extraction  |            10 |      17 |              1 |        1019.89   |         962.831  |      146.37   |                 28.5257 |               35   |              28     |                 1 |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | multi_agent      |             1 |      10 |              1 |       13749.8    |       13676      |      221.714  |                 53.5137 |              635.3 |             735.6   |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | multi_agent      |             5 |      10 |              1 |       11597.7    |       13500.3    |      220.267  |                 53.2356 |               42.2 |             600.5   |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | rag              |             1 |       2 |              1 |        1011.94   |        1011.94   |      554.228  |                 31.8915 |               51   |              24.5   |               nan |                        0 |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | single           |             1 |       1 |              1 |        1877.76   |        1877.76   |     1251.93   |                 10.1185 |               20   |              19     |                 1 |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | summarization    |             1 |       4 |              1 |        1779.17   |        1900.09   |       40.0303 |                 52.9835 |               46   |              93.75  |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | summarization    |             3 |       5 |              1 |        2019.76   |        1981.49   |       85.759  |                 48.6283 |               46   |              98     |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | summarization    |             5 |       8 |              1 |        2095.57   |        2117.8    |       69.5233 |                 46.7532 |               46   |              97.875 |               nan |                      nan |
| Qwen/Qwen3-14B | sglang   | A100_80GB  | summarization    |            10 |      16 |              1 |        2247.39   |        2286.18   |       79.3044 |                 43.7198 |               46   |              98     |               nan |                      nan |

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
