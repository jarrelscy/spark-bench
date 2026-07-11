# Tier 2 — Inference (Qwen3.6-27B-NVFP4-dflash-k8-throughput-20260709-223327)

- model `qwen36-27b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-k8`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 674 | 20.6 | 48.7 | 1509 | 512 |
| 8006 | 4186 | 21.3 | 47.1 | 1913 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 17 | 17.5 | 670 | 670 | 1/1 |
| 8 | 99 | 13.7 | 4285 | 4287 | 8/8 |
| 16 | 92 | 12.0 | 6385 | 53502 | 16/16 |

