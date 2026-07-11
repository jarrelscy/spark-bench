# Tier 2 — Inference (warmup-discard-fast35b-20260710-124401)

- model `fast35b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 405 | 112.3 | 9.0 | 2512 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 75 | 101.4 | 218 | 218 | 1/1 |
| 16 | 189 | 35.7 | 3212 | 3401 | 16/16 |

