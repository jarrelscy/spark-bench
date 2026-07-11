# Tier 2 — Inference (Qwen3.6-27B-NVFP4-OFFICIAL-dflash-n4-throughput-20260710-152036)

- model `df27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-n4`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1034 | 27.8 | 36.0 | 983 | 512 |
| 8006 | 7200 | 28.4 | 35.2 | 1112 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 23 | 23.8 | 1019 | 1019 | 1/1 |
| 8 | 110 | 18.4 | 7355 | 7356 | 8/8 |
| 16 | 138 | 11.7 | 14173 | 14415 | 16/16 |

