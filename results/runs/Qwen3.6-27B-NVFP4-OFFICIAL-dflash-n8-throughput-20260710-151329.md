# Tier 2 — Inference (Qwen3.6-27B-NVFP4-OFFICIAL-dflash-n8-throughput-20260710-151329)

- model `df27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-n8`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1033 | 28.0 | 35.8 | 984 | 512 |
| 8006 | 7080 | 33.0 | 30.4 | 1131 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 27 | 28.9 | 1025 | 1025 | 1/1 |
| 8 | 89 | 13.9 | 7303 | 7305 | 8/8 |
| 16 | 113 | 9.2 | 14558 | 14560 | 16/16 |

