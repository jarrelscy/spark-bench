# Tier 2 — Inference (warmup-discard-27b-mtp3-restored-20260709-231022)

- model `qwen36-27b-nvfp4-mtp` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2490 | 21.4 | 47.5 | 408 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 18 | 21.4 | 536 | 536 | 1/1 |
| 16 | 81 | 16.6 | 7920 | 7927 | 16/16 |

