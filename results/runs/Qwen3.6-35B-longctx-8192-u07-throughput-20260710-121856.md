# Tier 2 — Inference (Qwen3.6-35B-longctx-8192-u07-throughput-20260710-121856)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 8006 | 5077 | 44.3 | 22.6 | 1577 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 11 | 12.0 | 3744 | 3744 | 1/1 |
| 4 | 73 | 27.4 | 6975 | 7033 | 4/4 |
| 8 | 89 | 19.7 | 18877 | 25419 | 8/8 |
| 16 | 66 | 8.3 | 44622 | 86010 | 16/16 |
| 24 | 78 | 5.9 | 44428 | 124499 | 24/24 |
| 32 | 86 | 5.4 | 56181 | 152373 | 32/32 |

