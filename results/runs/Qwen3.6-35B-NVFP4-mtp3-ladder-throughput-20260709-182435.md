# Tier 2 — Inference (Qwen3.6-35B-NVFP4-mtp3-ladder-throughput-20260709-182435)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 240 | 95.8 | 10.5 | 4245 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 95 | 99.4 | 223 | 223 | 1/1 |
| 8 | 314 | 45.2 | 1243 | 1244 | 8/8 |
| 16 | 452 | 33.4 | 2356 | 2421 | 16/16 |
| 24 | 517 | 25.8 | 3519 | 3605 | 24/24 |
| 32 | 567 | 21.2 | 3688 | 4825 | 32/32 |
| 48 | 635 | 15.8 | 4887 | 7312 | 48/48 |
| 64 | 687 | 12.9 | 6096 | 9862 | 64/64 |

