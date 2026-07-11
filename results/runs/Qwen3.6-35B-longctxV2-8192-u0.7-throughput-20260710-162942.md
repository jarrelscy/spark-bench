# Tier 2 — Inference (Qwen3.6-35B-longctxV2-8192-u0.7-throughput-20260710-162942)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 8006 | 1604 | 62.7 | 16.0 | 4992 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 51 | 61.0 | 1590 | 1590 | 1/1 |
| 4 | 111 | 45.4 | 7156 | 7212 | 4/4 |
| 8 | 152 | 29.9 | 9581 | 12844 | 8/8 |
| 16 | 178 | 18.1 | 16104 | 25916 | 16/16 |

