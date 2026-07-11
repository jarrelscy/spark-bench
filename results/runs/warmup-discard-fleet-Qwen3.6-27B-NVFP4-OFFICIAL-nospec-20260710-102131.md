# Tier 2 — Inference (warmup-discard-fleet-Qwen3.6-27B-NVFP4-OFFICIAL-nospec-20260710-102131)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1164 | 12.6 | 80.5 | 874 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 10 | 12.6 | 1123 | 1123 | 1/1 |
| 16 | 50 | 8.2 | 11537 | 13736 | 16/16 |

