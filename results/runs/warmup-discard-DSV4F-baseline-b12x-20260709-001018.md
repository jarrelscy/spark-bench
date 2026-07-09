# Tier 2 — Inference (warmup-discard-DSV4F-baseline-b12x-20260709-001018)

- model `deepseek-v4-flash-dspark` @ `http://10.0.0.109:8888/v1`  topology `2x DGX Spark` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1008 | 927 | 42.4 | 24.0 | 1088 | 64 |
| 7997 | 4197 | 2.4 | 429.4 | 1906 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 22 | 29.4 | 691 | 691 | 1/1 |
| 8 | 99 | 17.9 | 1201 | 1203 | 8/8 |
| 16 | 101 | 13.8 | 1993 | 8321 | 16/16 |

