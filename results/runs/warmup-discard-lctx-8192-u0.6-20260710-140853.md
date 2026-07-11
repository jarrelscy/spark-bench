# Tier 2 — Inference (warmup-discard-lctx-8192-u0.6-20260710-140853)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 8006 | 5852 | 77.2 | 13.2 | 1368 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 25 | 75.9 | 1714 | 1714 | 1/1 |

