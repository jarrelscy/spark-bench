# Tier 2 — Inference (warmup-discard-DSV4F-legC-20260709-003855)

- model `dsv4f` @ `http://10.0.0.109:8888/v1`  topology `2x DGX Spark` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1008 | 6438 | 39.9 | 25.4 | 157 | 64 |
| 7997 | 4189 | 38.7 | 26.2 | 1909 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 8 | 35.1 | 6119 | 6119 | 1/1 |
| 8 | 98 | 19.2 | 1899 | 1900 | 8/8 |
| 16 | 203 | 21.9 | 2018 | 2021 | 16/16 |

