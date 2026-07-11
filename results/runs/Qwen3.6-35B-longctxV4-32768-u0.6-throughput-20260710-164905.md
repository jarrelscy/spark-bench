# Tier 2 — Inference (Qwen3.6-35B-longctxV4-32768-u0.6-throughput-20260710-164905)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 5845 | 99.1 | 10.1 | 5468 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 46 | 98.0 | 5826 | 5826 | 1/1 |
| 2 | 55 | 61.1 | 7149 | 11786 | 2/2 |
| 4 | 62 | 35.2 | 19313 | 23752 | 4/4 |

