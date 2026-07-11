# Tier 2 — Inference (Qwen3.6-35B-longctxV2-16384-u0.7-throughput-20260710-163143)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 15981 | 3340 | 61.2 | 16.4 | 4785 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 42 | 57.1 | 3335 | 3335 | 1/1 |
| 4 | 84 | 37.4 | 11821 | 13586 | 4/4 |
| 8 | 101 | 24.6 | 18718 | 27143 | 8/8 |

