# Tier 2 — Inference (warmup-discard-lctx-32768-u0.7-20260710-163312)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 7627 | 65.6 | 15.5 | 4191 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 8 | 73.8 | 7585 | 7585 | 1/1 |

