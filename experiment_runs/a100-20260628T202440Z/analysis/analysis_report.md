# A100 Official Benchmark Deep Analysis

## Scope

- Experiment directory: `experiment_runs/a100-20260628T202440Z`
- Official result rows analyzed: 695
- Non-official rows excluded: 1
- Included run tags: tags ending in `-official` only.
- Analysis mode: performance-only; no RunPod cost modeling.

## Headline Findings

- Highest request throughput was Qwen3 4B / SGLang at concurrency 10: 14.91 requests/sec.
- Lowest concurrency p95 latency was Qwen3 4B / vLLM at concurrency 3: 632.6 ms.
- Concurrency runs recorded 0 errors across official benchmark summaries.
- Fastest average agent workflow was Qwen3 4B / SGLang in concurrent mode: 5.78 seconds.
- For common 4B/14B models at concurrency 10, SGLang averaged 1.11x vLLM request throughput and 1.06x vLLM p95 latency.
- Official concurrency summary errors: 0
- Official agent workflow summary errors: 0

## How To Read This Report

- `p50 latency` is the median request latency. It describes the typical request.
- `p95 latency` is the tail-latency pressure point. It matters more for interactive agents.
- `TTFT` is time to first token. Lower TTFT makes the model feel more responsive.
- `requests/sec` measures server throughput for a concurrency level.
- `tokens/sec` is estimated from client-side token counts, so treat it as directional.
- Agent workflow latency is the end-to-end multi-agent task latency, not just one model call.
- GPU memory snapshots are point-in-time `nvidia-smi` values around summary runs, not continuous telemetry.

## Concurrency Summary

| series_label       |   concurrency |   p50_latency_ms |   p95_latency_ms |   requests_per_second |   avg_tokens_per_second |   avg_ttft_ms |   error_rate |
|:-------------------|--------------:|-----------------:|-----------------:|----------------------:|------------------------:|--------------:|-------------:|
| Qwen3 4B / SGLang  |             1 |          313.309 |         1371.83  |                 2.553 |                  78.897 |       133.132 |            0 |
| Qwen3 4B / SGLang  |             3 |          374.433 |         1101.94  |                 4.732 |                  63.344 |       169.644 |            0 |
| Qwen3 4B / SGLang  |             5 |          412.596 |          680.178 |                 8.651 |                  63.007 |        89.036 |            0 |
| Qwen3 4B / SGLang  |            10 |          504.258 |          821.104 |                14.906 |                  52.459 |        86.076 |            0 |
| Qwen3 4B / vLLM    |             1 |          353.449 |         1985.59  |                 2.059 |                  68.318 |       208.392 |            0 |
| Qwen3 4B / vLLM    |             3 |          381.19  |          632.648 |                 4.521 |                  64.607 |       163.812 |            0 |
| Qwen3 4B / vLLM    |             5 |          369.484 |          674.4   |                 6.737 |                  65.426 |       145.259 |            0 |
| Qwen3 4B / vLLM    |            10 |          407.468 |          751.333 |                12.846 |                  61.521 |       126.283 |            0 |
| Qwen3 14B / SGLang |             1 |          806.212 |         1901.41  |                 0.984 |                  32.567 |       142.3   |            0 |
| Qwen3 14B / SGLang |             3 |          817.933 |         2123.85  |                 2.142 |                  29.757 |       155.727 |            0 |
| Qwen3 14B / SGLang |             5 |          894.016 |         2127.15  |                 3.486 |                  29.296 |       118.181 |            0 |
| Qwen3 14B / SGLang |            10 |          961.822 |         2329.91  |                 6.604 |                  27.201 |       102.014 |            0 |
| Qwen3 14B / vLLM   |             1 |          852.071 |         2667.15  |                 0.876 |                  29.664 |       244.616 |            0 |
| Qwen3 14B / vLLM   |             3 |          866.487 |         2067.32  |                 1.889 |                  29.37  |       216.29  |            0 |
| Qwen3 14B / vLLM   |             5 |          853.856 |         2113.72  |                 3.319 |                  29.887 |       140.778 |            0 |
| Qwen3 14B / vLLM   |            10 |          909.075 |         2271.28  |                 6.235 |                  27.713 |       148.286 |            0 |
| Qwen3 32B / vLLM   |             1 |         1787.29  |         4014.45  |                 0.49  |                  16.689 |       307.351 |            0 |
| Qwen3 32B / vLLM   |             3 |         1836.95  |         3550.34  |                 1.116 |                  16.458 |       260.727 |            0 |
| Qwen3 32B / vLLM   |             5 |         1897.32  |         3653.63  |                 1.854 |                  15.905 |       219.825 |            0 |
| Qwen3 32B / vLLM   |            10 |         1939.89  |         3792.28  |                 3.639 |                  15.473 |       203.692 |            0 |

## Scaling Efficiency

Scaling efficiency compares observed requests/sec against the ideal linear increase from concurrency 1.

| series_label       |   concurrency |   requests_per_second |   observed_rps_scaling_vs_c1 |   scaling_efficiency_pct |
|:-------------------|--------------:|----------------------:|-----------------------------:|-------------------------:|
| Qwen3 14B / SGLang |             1 |                 0.984 |                        1     |                  100     |
| Qwen3 14B / SGLang |             3 |                 2.142 |                        2.176 |                   72.529 |
| Qwen3 14B / SGLang |             5 |                 3.486 |                        3.541 |                   70.829 |
| Qwen3 14B / SGLang |            10 |                 6.604 |                        6.709 |                   67.085 |
| Qwen3 4B / SGLang  |             1 |                 2.553 |                        1     |                  100     |
| Qwen3 4B / SGLang  |             3 |                 4.732 |                        1.853 |                   61.779 |
| Qwen3 4B / SGLang  |             5 |                 8.651 |                        3.388 |                   67.766 |
| Qwen3 4B / SGLang  |            10 |                14.906 |                        5.838 |                   58.379 |
| Qwen3 14B / vLLM   |             1 |                 0.876 |                        1     |                  100     |
| Qwen3 14B / vLLM   |             3 |                 1.889 |                        2.158 |                   71.926 |
| Qwen3 14B / vLLM   |             5 |                 3.319 |                        3.791 |                   75.821 |
| Qwen3 14B / vLLM   |            10 |                 6.235 |                        7.121 |                   71.21  |
| Qwen3 32B / vLLM   |             1 |                 0.49  |                        1     |                  100     |
| Qwen3 32B / vLLM   |             3 |                 1.116 |                        2.279 |                   75.963 |
| Qwen3 32B / vLLM   |             5 |                 1.854 |                        3.786 |                   75.714 |
| Qwen3 32B / vLLM   |            10 |                 3.639 |                        7.43  |                   74.298 |
| Qwen3 4B / vLLM    |             1 |                 2.059 |                        1     |                  100     |
| Qwen3 4B / vLLM    |             3 |                 4.521 |                        2.196 |                   73.212 |
| Qwen3 4B / vLLM    |             5 |                 6.737 |                        3.273 |                   65.456 |
| Qwen3 4B / vLLM    |            10 |                12.846 |                        6.24  |                   62.402 |

## Engine Comparison

This section compares vLLM and SGLang only where both engines were run for the same model size.
Ratios above `1.0` mean SGLang is higher than vLLM for that metric.

| model_label   |   concurrency |   sglang_vs_vllm_rps_ratio |   sglang_vs_vllm_p95_ratio |   sglang_vs_vllm_ttft_ratio |
|:--------------|--------------:|---------------------------:|---------------------------:|----------------------------:|
| Qwen3 14B     |             1 |                      1.124 |                      0.713 |                       0.582 |
| Qwen3 14B     |             3 |                      1.134 |                      1.027 |                       0.72  |
| Qwen3 14B     |             5 |                      1.05  |                      1.006 |                       0.839 |
| Qwen3 14B     |            10 |                      1.059 |                      1.026 |                       0.688 |
| Qwen3 4B      |             1 |                      1.24  |                      0.691 |                       0.639 |
| Qwen3 4B      |             3 |                      1.047 |                      1.742 |                       1.036 |
| Qwen3 4B      |             5 |                      1.284 |                      1.009 |                       0.613 |
| Qwen3 4B      |            10 |                      1.16  |                      1.093 |                       0.682 |

## Agent Workflow Summary

| series_label       | workflow_mode   |   workflow_count |   avg_workflow_latency_s |   p95_workflow_latency_ms |   success_rate |
|:-------------------|:----------------|-----------------:|-------------------------:|--------------------------:|---------------:|
| Qwen3 4B / SGLang  | concurrent      |                2 |                    5.784 |                   6270.6  |              1 |
| Qwen3 4B / vLLM    | concurrent      |                2 |                    6.795 |                   7773.85 |              1 |
| Qwen3 14B / SGLang | concurrent      |                2 |                   14.137 |                  14703.1  |              1 |
| Qwen3 14B / vLLM   | concurrent      |                2 |                   15.101 |                  16022.7  |              1 |
| Qwen3 32B / vLLM   | concurrent      |                2 |                   32.368 |                  33459.7  |              1 |
| Qwen3 4B / SGLang  | sequential      |                2 |                   22.57  |                  23008.5  |              1 |
| Qwen3 4B / vLLM    | sequential      |                2 |                   24.573 |                  25722.4  |              1 |
| Qwen3 14B / SGLang | sequential      |                2 |                   68.792 |                  69399.4  |              1 |
| Qwen3 14B / vLLM   | sequential      |                2 |                   70.387 |                  71239.6  |              1 |
| Qwen3 32B / vLLM   | sequential      |                2 |                  132.766 |                 136305    |              1 |

## Agent Step Summary

| series_label       | workflow_mode   | agent     |   avg_step_latency_ms |   p95_step_latency_ms |   avg_tokens_per_second |
|:-------------------|:----------------|:----------|----------------------:|----------------------:|------------------------:|
| Qwen3 4B / SGLang  | concurrent      | architect |               5255.21 |               5273.96 |                 129.888 |
| Qwen3 4B / SGLang  | concurrent      | coder     |               5248.67 |               5268.44 |                 126.666 |
| Qwen3 4B / SGLang  | concurrent      | evaluator |               2186.27 |               2372.51 |                 164.823 |
| Qwen3 4B / SGLang  | concurrent      | planner   |               5764.29 |               6251.83 |                 117.749 |
| Qwen3 4B / SGLang  | concurrent      | reviewer  |               5247.21 |               5263.4  |                 134.854 |
| Qwen3 4B / vLLM    | concurrent      | architect |               5710.8  |               5735.06 |                 119.951 |
| Qwen3 4B / vLLM    | concurrent      | coder     |               5719.81 |               5746.58 |                 116.585 |
| Qwen3 4B / vLLM    | concurrent      | evaluator |               2445.19 |               2586.16 |                 149.422 |
| Qwen3 4B / vLLM    | concurrent      | planner   |               6786.15 |               7762.21 |                 104.334 |
| Qwen3 4B / vLLM    | concurrent      | reviewer  |               5721.51 |               5748.87 |                 124.548 |
| Qwen3 14B / SGLang | concurrent      | architect |              13528.5  |              13560.1  |                  50.709 |
| Qwen3 14B / SGLang | concurrent      | coder     |              13535.3  |              13571.7  |                  52.807 |
| Qwen3 14B / SGLang | concurrent      | evaluator |               3266.97 |               3806.38 |                  61.441 |
| Qwen3 14B / SGLang | concurrent      | planner   |              14132.7  |              14697.1  |                  47.405 |
| Qwen3 14B / SGLang | concurrent      | reviewer  |              13524.9  |              13561.9  |                  53.816 |
| Qwen3 14B / vLLM   | concurrent      | architect |              14044.6  |              14056.3  |                  47.6   |
| Qwen3 14B / vLLM   | concurrent      | coder     |              14053.9  |              14059.4  |                  49.027 |
| Qwen3 14B / vLLM   | concurrent      | evaluator |               2655.55 |               2773.07 |                  55.577 |
| Qwen3 14B / vLLM   | concurrent      | planner   |              15094.1  |              16019.1  |                  45.469 |
| Qwen3 14B / vLLM   | concurrent      | reviewer  |              14055.2  |              14062.3  |                  53.537 |
| Qwen3 32B / vLLM   | concurrent      | architect |              31154.2  |              31205.4  |                  21.617 |
| Qwen3 32B / vLLM   | concurrent      | coder     |              31170.9  |              31196.9  |                  22.151 |
| Qwen3 32B / vLLM   | concurrent      | evaluator |              10480    |              11212.1  |                  27.888 |
| Qwen3 32B / vLLM   | concurrent      | planner   |              32352.5  |              33442.5  |                  20.885 |
| Qwen3 32B / vLLM   | concurrent      | reviewer  |              31198.8  |              31248.2  |                  25.657 |
| Qwen3 4B / SGLang  | sequential      | architect |               5174.72 |               5175.61 |                 142.52  |
| Qwen3 4B / SGLang  | sequential      | coder     |               5175.01 |               5177.62 |                 149.563 |
| Qwen3 4B / SGLang  | sequential      | evaluator |               1409.84 |               1432.55 |                 165.15  |
| Qwen3 4B / SGLang  | sequential      | planner   |               5601.33 |               6056.35 |                 121.698 |
| Qwen3 4B / SGLang  | sequential      | reviewer  |               5176.74 |               5177.6  |                 143.43  |
| Qwen3 4B / vLLM    | sequential      | architect |               5400.99 |               5412.08 |                 138.684 |
| Qwen3 4B / vLLM    | sequential      | coder     |               5441.14 |               5454.23 |                 141.612 |
| Qwen3 4B / vLLM    | sequential      | evaluator |               2039.63 |               2466.08 |                 160.602 |
| Qwen3 4B / vLLM    | sequential      | planner   |               6218.66 |               6969.18 |                 111.727 |
| Qwen3 4B / vLLM    | sequential      | reviewer  |               5442.99 |               5446.3  |                 146.618 |
| Qwen3 14B / SGLang | sequential      | architect |              13676.8  |              13682.7  |                  53.959 |
| Qwen3 14B / SGLang | sequential      | coder     |              13676.4  |              13682.1  |                  51.875 |
| Qwen3 14B / SGLang | sequential      | evaluator |              13675.5  |              13683.1  |                  56.852 |
| Qwen3 14B / SGLang | sequential      | planner   |              14044.1  |              14620.4  |                  47.373 |
| Qwen3 14B / SGLang | sequential      | reviewer  |              13676    |              13680.4  |                  57.509 |

## Workload Category Summary

| series_label       | run_type                | category         |   request_count |   p50_latency_ms |   p95_latency_ms |   avg_ttft_ms |   avg_tokens_per_second |   success_rate |
|:-------------------|:------------------------|:-----------------|----------------:|-----------------:|-----------------:|--------------:|------------------------:|---------------:|
| Qwen3 4B / SGLang  | agent_concurrent_detail | multi_agent      |              10 |         5231.8   |         5842.52  |       187.048 |                 134.796 |              1 |
| Qwen3 4B / SGLang  | agent_sequential_detail | multi_agent      |              10 |         5174.72  |         5688.86  |       144.395 |                 144.472 |              1 |
| Qwen3 4B / SGLang  | batch                   | architecture     |               1 |         3726.3   |         3726.3   |        32.263 |                 124.789 |              1 |
| Qwen3 4B / SGLang  | batch                   | classification   |               1 |           37.656 |           37.656 |        30.035 |                  26.556 |              1 |
| Qwen3 4B / SGLang  | batch                   | coding           |               1 |         2889.81  |         2889.81  |      1000.89  |                  86.857 |              1 |
| Qwen3 4B / SGLang  | batch                   | debugging        |               1 |         3720.45  |         3720.45  |        28.683 |                 133.049 |              1 |
| Qwen3 4B / SGLang  | batch                   | function_calling |               2 |          896.697 |         1379.82  |       458.457 |                  53.911 |              1 |
| Qwen3 4B / SGLang  | batch                   | json_extraction  |               1 |         1588.94  |         1588.94  |      1296.58  |                  17.622 |              1 |
| Qwen3 4B / SGLang  | batch                   | rag              |               2 |          789.925 |         1312.51  |       629.643 |                  71.805 |              1 |
| Qwen3 4B / SGLang  | batch                   | summarization    |               1 |          485.925 |          485.925 |        29.885 |                 137.881 |              1 |
| Qwen3 4B / SGLang  | concurrency_detail      | classification   |              33 |           59.584 |          115.702 |        71.809 |                  16.379 |              1 |
| Qwen3 4B / SGLang  | concurrency_detail      | json_extraction  |              35 |          437.965 |         1394.92  |       164.734 |                  60.563 |              1 |
| Qwen3 4B / SGLang  | concurrency_detail      | summarization    |              32 |          657.89  |          821.192 |        70.946 |                 102.407 |              1 |
| Qwen3 4B / SGLang  | single_prompt           | single           |               1 |        11612.4   |        11612.4   |     11396.5   |                   1.378 |              1 |
| Qwen3 4B / vLLM    | agent_concurrent_detail | multi_agent      |              10 |         5696.37  |         6917.23  |       347.859 |                 122.968 |              1 |
| Qwen3 4B / vLLM    | agent_sequential_detail | multi_agent      |              10 |         5419.95  |         6333.98  |       227.45  |                 139.848 |              1 |
| Qwen3 4B / vLLM    | batch                   | architecture     |               1 |         3958.87  |         3958.87  |        47.814 |                 117.458 |              1 |
| Qwen3 4B / vLLM    | batch                   | classification   |               1 |           48.406 |           48.406 |        40.662 |                  20.659 |              1 |
| Qwen3 4B / vLLM    | batch                   | coding           |               1 |         3879.02  |         3879.02  |      1894.92  |                  64.191 |              1 |
| Qwen3 4B / vLLM    | batch                   | debugging        |               1 |         3056.96  |         3056.96  |        48.477 |                 124.634 |              1 |
| Qwen3 4B / vLLM    | batch                   | function_calling |               2 |         1387.02  |         2276.42  |       916.642 |                  43.335 |              1 |
| Qwen3 4B / vLLM    | batch                   | json_extraction  |               1 |         2195.27  |         2195.27  |      1891.05  |                  12.755 |              1 |
| Qwen3 4B / vLLM    | batch                   | rag              |               2 |         1332.17  |         2322.83  |      1160.08  |                  62.44  |              1 |
| Qwen3 4B / vLLM    | batch                   | summarization    |               1 |          536.332 |          536.332 |        45.314 |                 124.923 |              1 |
| Qwen3 4B / vLLM    | concurrency_detail      | classification   |              33 |           66.089 |          211.851 |        77.849 |                  13.845 |              1 |
| Qwen3 4B / vLLM    | concurrency_detail      | json_extraction  |              35 |          394.155 |         2053.41  |       269.361 |                  64.117 |              1 |
| Qwen3 4B / vLLM    | concurrency_detail      | summarization    |              32 |          565.806 |          749.143 |        77.815 |                 114.469 |              1 |
| Qwen3 4B / vLLM    | single_prompt           | single           |               1 |         2290.59  |         2290.59  |      2057.49  |                   6.985 |              1 |
| Qwen3 14B / SGLang | agent_concurrent_detail | multi_agent      |              10 |        13500.3   |        14226.9   |       220.267 |                  53.236 |              1 |
| Qwen3 14B / SGLang | agent_sequential_detail | multi_agent      |              10 |        13676     |        14234.2   |       221.714 |                  53.514 |              1 |
| Qwen3 14B / SGLang | batch                   | architecture     |               1 |         9879.72  |         9879.72  |        38.623 |                  52.836 |              1 |
| Qwen3 14B / SGLang | batch                   | classification   |               1 |           56.203 |           56.203 |        38.194 |                  17.793 |              1 |
| Qwen3 14B / SGLang | batch                   | coding           |               1 |         6104.23  |         6104.23  |       825.983 |                  41.119 |              1 |
| Qwen3 14B / SGLang | batch                   | debugging        |               1 |         7403.52  |         7403.52  |        41.28  |                  49.436 |              1 |
| Qwen3 14B / SGLang | batch                   | function_calling |               2 |         1770.04  |         2454.83  |       546.485 |                  24.444 |              1 |
| Qwen3 14B / SGLang | batch                   | json_extraction  |               1 |         2148.14  |         2148.14  |      1391.56  |                  13.035 |              1 |
| Qwen3 14B / SGLang | batch                   | rag              |               2 |         1011.94  |         1376.47  |       554.228 |                  31.891 |              1 |
| Qwen3 14B / SGLang | batch                   | summarization    |               1 |         1415.09  |         1415.09  |        36.032 |                  57.24  |              1 |
| Qwen3 14B / SGLang | concurrency_detail      | classification   |              33 |           83.745 |          149.125 |        75.58  |                  11.238 |              1 |
| Qwen3 14B / SGLang | concurrency_detail      | json_extraction  |              35 |          919.716 |         2080.56  |       198.343 |                  29.206 |              1 |
| Qwen3 14B / SGLang | concurrency_detail      | summarization    |              32 |         2132.64  |         2343.13  |        74.311 |                  45.981 |              1 |
| Qwen3 14B / SGLang | single_prompt           | single           |               1 |         1877.76  |         1877.76  |      1251.93  |                  10.118 |              1 |
| Qwen3 14B / vLLM   | agent_concurrent_detail | multi_agent      |              10 |        14052.8   |        15196.8   |       371.849 |                  50.242 |              1 |
| Qwen3 14B / vLLM   | agent_sequential_detail | multi_agent      |              10 |        13936.3   |        14823.7   |       304.319 |                  51.648 |              1 |
| Qwen3 14B / vLLM   | batch                   | architecture     |               1 |        10087.9   |        10087.9   |        52.864 |                  42.526 |              1 |
| Qwen3 14B / vLLM   | batch                   | classification   |               1 |           72.339 |           72.339 |        52.552 |                  13.824 |              1 |
| Qwen3 14B / vLLM   | batch                   | coding           |               1 |         7229.34  |         7229.34  |      1837.57  |                  34.72  |              1 |
| Qwen3 14B / vLLM   | batch                   | debugging        |               1 |         7306.01  |         7306.01  |        54.246 |                  49.001 |              1 |
| Qwen3 14B / vLLM   | batch                   | function_calling |               2 |         2232.55  |         3281.34  |       976.279 |                  21.091 |              1 |
| Qwen3 14B / vLLM   | batch                   | json_extraction  |               1 |         2626.52  |         2626.52  |      1844.19  |                  10.661 |              1 |

## GPU Memory Snapshots

| series_label       | run_type            |   concurrency | snapshot_phase   |   gpu_memory_used_mb |   gpu_memory_used_pct |   gpu_util_percent |   gpu_power_watts |
|:-------------------|:--------------------|--------------:|:-----------------|---------------------:|----------------------:|-------------------:|------------------:|
| Qwen3 4B / SGLang  | concurrency_summary |             1 | after            |                70244 |                85.747 |                 91 |            265.39 |
| Qwen3 4B / SGLang  | concurrency_summary |             1 | before           |                70244 |                85.747 |                  0 |             71.49 |
| Qwen3 4B / SGLang  | concurrency_summary |             3 | after            |                70264 |                85.771 |                 85 |            266.86 |
| Qwen3 4B / SGLang  | concurrency_summary |             3 | before           |                70244 |                85.747 |                  0 |             71.69 |
| Qwen3 4B / SGLang  | concurrency_summary |             5 | after            |                70264 |                85.771 |                100 |            262.34 |
| Qwen3 4B / SGLang  | concurrency_summary |             5 | before           |                70264 |                85.771 |                  0 |             71.69 |
| Qwen3 4B / SGLang  | concurrency_summary |            10 | after            |                70264 |                85.771 |                100 |            264.46 |
| Qwen3 4B / SGLang  | concurrency_summary |            10 | before           |                70264 |                85.771 |                  0 |             71.76 |
| Qwen3 4B / vLLM    | concurrency_summary |             1 | after            |                74461 |                90.895 |                 92 |            250.48 |
| Qwen3 4B / vLLM    | concurrency_summary |             1 | before           |                74461 |                90.895 |                  0 |             69.96 |
| Qwen3 4B / vLLM    | concurrency_summary |             3 | after            |                74461 |                90.895 |                 92 |            247.5  |
| Qwen3 4B / vLLM    | concurrency_summary |             3 | before           |                74461 |                90.895 |                  0 |             70.24 |
| Qwen3 4B / vLLM    | concurrency_summary |             5 | after            |                74461 |                90.895 |                 92 |            248.1  |
| Qwen3 4B / vLLM    | concurrency_summary |             5 | before           |                74461 |                90.895 |                  0 |             70.17 |
| Qwen3 4B / vLLM    | concurrency_summary |            10 | after            |                74461 |                90.895 |                 92 |            245.98 |
| Qwen3 4B / vLLM    | concurrency_summary |            10 | before           |                74461 |                90.895 |                  0 |             69.96 |
| Qwen3 14B / SGLang | concurrency_summary |             1 | after            |                70416 |                85.957 |                100 |            301.7  |
| Qwen3 14B / SGLang | concurrency_summary |             1 | before           |                70416 |                85.957 |                  0 |             70.83 |
| Qwen3 14B / SGLang | concurrency_summary |             3 | after            |                70416 |                85.957 |                100 |            301.08 |
| Qwen3 14B / SGLang | concurrency_summary |             3 | before           |                70416 |                85.957 |                  0 |             71.16 |
| Qwen3 14B / SGLang | concurrency_summary |             5 | after            |                70416 |                85.957 |                100 |            301.38 |
| Qwen3 14B / SGLang | concurrency_summary |             5 | before           |                70416 |                85.957 |                  0 |             71.16 |
| Qwen3 14B / SGLang | concurrency_summary |            10 | after            |                70416 |                85.957 |                100 |            302.62 |
| Qwen3 14B / SGLang | concurrency_summary |            10 | before           |                70416 |                85.957 |                  0 |             71.23 |
| Qwen3 14B / vLLM   | concurrency_summary |             1 | after            |                74583 |                91.044 |                 97 |            294.41 |
| Qwen3 14B / vLLM   | concurrency_summary |             1 | before           |                74583 |                91.044 |                  0 |             70.76 |
| Qwen3 14B / vLLM   | concurrency_summary |             3 | after            |                74583 |                91.044 |                 97 |            296.55 |
| Qwen3 14B / vLLM   | concurrency_summary |             3 | before           |                74583 |                91.044 |                  0 |             71.16 |
| Qwen3 14B / vLLM   | concurrency_summary |             5 | after            |                74583 |                91.044 |                 97 |            292.64 |
| Qwen3 14B / vLLM   | concurrency_summary |             5 | before           |                74583 |                91.044 |                  0 |             71.16 |
| Qwen3 14B / vLLM   | concurrency_summary |            10 | after            |                74583 |                91.044 |                 97 |            297.14 |
| Qwen3 14B / vLLM   | concurrency_summary |            10 | before           |                74583 |                91.044 |                  0 |             71.42 |
| Qwen3 32B / vLLM   | concurrency_summary |             1 | after            |                75053 |                91.617 |                 98 |            311.04 |
| Qwen3 32B / vLLM   | concurrency_summary |             1 | before           |                75053 |                91.617 |                  0 |             70.56 |
| Qwen3 32B / vLLM   | concurrency_summary |             3 | after            |                75053 |                91.617 |                 98 |            312.89 |
| Qwen3 32B / vLLM   | concurrency_summary |             3 | before           |                75053 |                91.617 |                  0 |             72.09 |
| Qwen3 32B / vLLM   | concurrency_summary |             5 | after            |                75053 |                91.617 |                 98 |            310.5  |
| Qwen3 32B / vLLM   | concurrency_summary |             5 | before           |                75053 |                91.617 |                  0 |             71.76 |
| Qwen3 32B / vLLM   | concurrency_summary |            10 | after            |                75053 |                91.617 |                 99 |            307.41 |
| Qwen3 32B / vLLM   | concurrency_summary |            10 | before           |                75053 |                91.617 |                  0 |             71.76 |

## Interpretation

- Use p95 latency, not average latency, when deciding what feels safe for interactive agent loops.
- Use requests/sec at concurrency 5 and 10 when estimating whether one GPU can serve multiple agents.
- Treat 4B models as routing and fast utility candidates, 14B as balanced candidates, and 32B as a quality candidate that needs tighter latency review.
- Treat SGLang-vs-vLLM conclusions as model-size-specific. The comparison is strongest for 4B and 14B because both engines were run there.
- The current GPU memory data is enough to confirm model residency and rough pressure, but future experiments should add periodic memory/utilization sampling.

## Generated Artifacts

- `dashboard.html`: interactive Plotly dashboard.
- `summary_metrics.csv`: per-run official row counts.
- `concurrency_metrics.csv`: latency, throughput, TTFT, tokens/sec, and error-rate summary.
- `scaling_metrics.csv`: throughput scaling efficiency by concurrency.
- `engine_comparison.csv`: SGLang vs vLLM ratios for common models.
- `agent_metrics.csv`: sequential and concurrent workflow latency.
- `agent_step_metrics.csv`: per-agent step latency.
- `workload_metrics.csv`: workload/category breakdown.
- `gpu_snapshots.csv`: structured GPU memory/utilization snapshots extracted from result rows.

## Future Benchmark Improvements

- Add continuous GPU telemetry sampling during each benchmark run.
- Add engine-native token and scheduler metrics instead of client-estimated token counts only.
- Add quality-scored prompts for model-size tradeoff analysis.
- Repeat each official run multiple times to estimate variance.
