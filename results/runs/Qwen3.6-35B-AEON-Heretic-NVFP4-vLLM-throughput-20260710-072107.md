# Tier 2 — Inference (Qwen3.6-35B-AEON-Heretic-NVFP4-vLLM-throughput-20260710-072107)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 204 | 42.2 | 23.7 | 4979 | 512 |
| 8006 | 1132 | 41.5 | 24.1 | 7074 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 42 | 42.2 | 183 | 183 | 1/1 |
| 8 | 212 | 28.0 | 1113 | 1114 | 8/8 |
| 16 | 312 | 21.0 | 1717 | 2181 | 16/16 |

