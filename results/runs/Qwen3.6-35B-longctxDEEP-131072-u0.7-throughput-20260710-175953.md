# Tier 2 — Inference (Qwen3.6-35B-longctxDEEP-131072-u0.7-throughput-20260710-175953)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 123803 | 40832 | 79.8 | 12.6 | 3032 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 11 | 84.6 | 40705 | 40705 | 1/1 |
| 2 | 11 | 34.3 | 43546 | 82889 | 2/2 |
| 4 | 12 | 15.3 | 125346 | 164998 | 4/4 |
| 8 | 12 | 7.0 | 208473 | 333384 | 8/8 |
| 16 | 12 | 3.9 | 378432 | 674790 | 16/16 |

