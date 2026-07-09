# Tier 2 — Inference (DSV4F-baseline-b12x-dspark5-throughput-20260709-001110)

- model `deepseek-v4-flash-dspark` @ `http://10.0.0.109:8888/v1`  topology `2x DGX Spark` parallelism `1` spec_decode `dspark-n5`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1008 | 351 | 39.9 | 25.1 | 2872 | 512 |
| 7997 | 324 | 38.0 | 26.4 | 24720 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 40 | 40.5 | 330 | 330 | 1/1 |
| 8 | 131 | 18.2 | 1083 | 1085 | 8/8 |
| 16 | 200 | 13.7 | 2260 | 2264 | 16/16 |

