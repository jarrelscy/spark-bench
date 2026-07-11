# Tier 2 — Inference (Qwen3.6-35B-longctxV2-32768-u0.7-throughput-20260710-163329)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 7415 | 55.0 | 18.2 | 4310 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 31 | 56.3 | 7397 | 7397 | 1/1 |
| 2 | 42 | 44.7 | 9110 | 15067 | 2/2 |
| 4 | 50 | 29.1 | 24456 | 30157 | 4/4 |

