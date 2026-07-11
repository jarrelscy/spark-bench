# Tier 2 — Inference (warmup-discard-27b-atlas-dflash-20260709-231654)

- model `qwen36-27b` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2118 | 5.6 | 180.3 | 480 | 136 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 14.1 | 2089 | 2089 | 1/1 |

