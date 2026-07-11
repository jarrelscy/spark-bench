# Tier 2 — Inference (Qwen3.6-35B-NVFP4-sgl0515-nospec-throughput-20260710-213715)

- model `sgl35b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `none`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 148 | 68.9 | 14.5 | 6864 | 512 |
| 8006 | 1498 | 66.8 | 15.0 | 5344 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 68 | 68.7 | 85 | 85 | 1/1 |
| 8 | 265 | 34.0 | 431 | 433 | 8/8 |
| 16 | 392 | 24.9 | 366 | 369 | 16/16 |

