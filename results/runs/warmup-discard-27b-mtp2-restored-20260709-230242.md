# Tier 2 — Inference (warmup-discard-27b-mtp2-restored-20260709-230242)

- model `qwen36-27b-nvfp4-mtp` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2569 | 20.4 | 49.7 | 396 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 17 | 20.3 | 505 | 505 | 1/1 |
| 16 | 76 | 11.9 | 7850 | 8137 | 16/16 |

