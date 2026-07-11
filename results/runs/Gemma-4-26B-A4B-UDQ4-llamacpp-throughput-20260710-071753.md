# Tier 2 — Inference (Gemma-4-26B-A4B-UDQ4-llamacpp-throughput-20260710-071753)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1057 | 354 | 46.5 | 21.5 | 2985 | 512 |
| 8287 | 3177 | 43.0 | 23.3 | 2608 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 47 | 50.9 | 766 | 766 | 1/1 |
| 8 | 103 | 28.8 | 22184 | 22319 | 8/8 |
| 16 | 98 | 28.3 | 45215 | 66054 | 16/16 |

