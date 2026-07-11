# Tier 2 — Inference (warmup-discard-sgl0515-27b-nospec-20260711-002515)

- model `sgl27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 883 | 12.3 | 82.8 | 1152 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 12.2 | 238 | 238 | 1/1 |
| 16 | 127 | 9.5 | 1341 | 1346 | 16/16 |

