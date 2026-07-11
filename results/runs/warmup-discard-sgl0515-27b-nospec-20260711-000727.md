# Tier 2 — Inference (warmup-discard-sgl0515-27b-nospec-20260711-000727)

- model `sgl27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 899 | 12.3 | 82.6 | 1132 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 12.3 | 245 | 245 | 1/1 |
| 16 | 127 | 9.5 | 1348 | 1353 | 16/16 |

