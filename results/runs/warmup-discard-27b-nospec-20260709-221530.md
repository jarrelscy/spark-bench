# Tier 2 — Inference (warmup-discard-27b-nospec-20260709-221530)

- model `qwen36-27b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 605 | 8.2 | 123.2 | 1680 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 8 | 8.2 | 489 | 489 | 1/1 |
| 16 | 61 | 6.3 | 5909 | 7692 | 16/16 |

