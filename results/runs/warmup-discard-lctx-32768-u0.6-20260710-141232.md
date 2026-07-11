# Tier 2 — Inference (warmup-discard-lctx-32768-u0.6-20260710-141232)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 7528 | 66.3 | 15.3 | 4245 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 8 | 72.3 | 7507 | 7507 | 1/1 |

