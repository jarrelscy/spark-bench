# Tier 2 — Inference (Qwen3.6-35B-longctxV2-32768-u0.6-throughput-20260710-141248)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 7394 | 56.3 | 17.8 | 4322 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 30 | 52.1 | 7374 | 7374 | 1/1 |
| 2 | 41 | 42.5 | 9087 | 14953 | 2/2 |
| 4 | 50 | 29.4 | 24369 | 29959 | 4/4 |

