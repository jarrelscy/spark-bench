# Tier 2 — Inference (Qwen3.6-35B-longctxV2-8192-u0.6-throughput-20260710-140902)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 8006 | 1597 | 61.6 | 16.3 | 5013 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 50 | 58.5 | 1573 | 1573 | 1/1 |
| 4 | 118 | 47.4 | 7258 | 7312 | 4/4 |
| 8 | 152 | 29.8 | 9547 | 12758 | 8/8 |
| 16 | 178 | 18.3 | 16066 | 25759 | 16/16 |

