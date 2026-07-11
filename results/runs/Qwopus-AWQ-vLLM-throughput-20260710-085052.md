# Tier 2 — Inference (Qwopus-AWQ-vLLM-throughput-20260710-085052)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1031 | 9.4 | 106.4 | 986 | 512 |
| 8006 | 7752 | 9.2 | 108.4 | 1033 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 9 | 9.4 | 1020 | 1020 | 1/1 |
| 8 | 61 | 8.6 | 7824 | 7826 | 8/8 |
| 16 | 99 | 7.5 | 13264 | 15617 | 16/16 |

