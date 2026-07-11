# Tier 2 — Inference (warmup-discard-27b-dflash-k8-20260709-223303)

- model `qwen36-27b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 854 | 24.0 | 42.4 | 1190 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 17 | 20.6 | 690 | 690 | 1/1 |
| 16 | 61 | 13.8 | 6542 | 12386 | 16/16 |

