# Tier 2 — Inference (Qwen3.6-27B-NVFP4-mtp3-restored-throughput-20260709-231044)

- model `qwen36-27b-nvfp4-mtp` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 524 | 21.4 | 46.9 | 1939 | 512 |
| 8006 | 3717 | 22.3 | 44.9 | 2154 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 20 | 20.0 | 537 | 537 | 1/1 |
| 8 | 126 | 17.8 | 3688 | 3690 | 8/8 |
| 16 | 191 | 14.6 | 6965 | 7153 | 16/16 |

