# Tier 2 — Inference (Qwythos-9B-vLLM-throughput-20260710-081507)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 259 | 12.8 | 78.4 | 3927 | 512 |
| 8006 | 1703 | 12.4 | 81.1 | 4701 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 13 | 12.7 | 246 | 246 | 1/1 |
| 8 | 101 | 13.1 | 1718 | 1720 | 8/8 |
| 16 | 182 | 12.1 | 1966 | 3379 | 16/16 |

