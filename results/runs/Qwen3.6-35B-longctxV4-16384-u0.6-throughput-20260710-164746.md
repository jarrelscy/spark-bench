# Tier 2 — Inference (Qwen3.6-35B-longctxV4-16384-u0.6-throughput-20260710-164746)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 15981 | 2547 | 107.5 | 9.3 | 6276 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 67 | 99.6 | 2534 | 2534 | 1/1 |
| 4 | 110 | 49.0 | 9031 | 10258 | 4/4 |
| 8 | 125 | 28.7 | 14365 | 20713 | 8/8 |

