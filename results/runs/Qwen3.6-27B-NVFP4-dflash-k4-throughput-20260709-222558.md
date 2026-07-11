# Tier 2 — Inference (Qwen3.6-27B-NVFP4-dflash-k4-throughput-20260709-222558)

- model `qwen36-27b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-k4`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 672 | 19.9 | 50.3 | 1514 | 512 |
| 8006 | 4163 | 18.4 | 54.5 | 1923 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 18 | 18.0 | 663 | 663 | 1/1 |
| 8 | 89 | 12.3 | 4288 | 4290 | 8/8 |
| 16 | 150 | 11.5 | 8168 | 8410 | 16/16 |

