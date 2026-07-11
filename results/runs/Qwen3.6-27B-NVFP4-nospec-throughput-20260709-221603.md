# Tier 2 — Inference (Qwen3.6-27B-NVFP4-nospec-throughput-20260709-221603)

- model `qwen36-27b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 505 | 8.1 | 123.6 | 2012 | 512 |
| 8006 | 3885 | 8.0 | 124.6 | 2061 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 8 | 8.1 | 489 | 489 | 1/1 |
| 8 | 57 | 7.5 | 3840 | 3842 | 8/8 |
| 16 | 100 | 6.8 | 5910 | 7691 | 16/16 |

