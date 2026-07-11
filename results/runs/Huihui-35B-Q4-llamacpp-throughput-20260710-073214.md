# Tier 2 — Inference (Huihui-35B-Q4-llamacpp-throughput-20260710-073214)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 402 | 77.8 | 12.9 | 2530 | 512 |
| 8006 | 3315 | 73.4 | 13.7 | 2415 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 74 | 78.0 | 390 | 390 | 1/1 |
| 8 | 141 | 38.2 | 15181 | 16023 | 8/8 |
| 16 | 140 | 39.9 | 31460 | 45984 | 16/16 |

