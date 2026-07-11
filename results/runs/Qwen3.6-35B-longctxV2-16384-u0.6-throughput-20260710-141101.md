# Tier 2 — Inference (Qwen3.6-35B-longctxV2-16384-u0.6-throughput-20260710-141101)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 15981 | 3338 | 55.7 | 18.0 | 4788 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 40 | 54.3 | 3323 | 3323 | 1/1 |
| 4 | 83 | 36.8 | 11785 | 13465 | 4/4 |
| 8 | 102 | 24.9 | 18663 | 26966 | 8/8 |

