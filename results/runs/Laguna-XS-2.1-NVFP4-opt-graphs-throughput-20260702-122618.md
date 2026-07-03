# Tier 2 — Inference (Laguna-XS-2.1-NVFP4-opt-graphs-throughput-20260702-122618)

- model `laguna` @ `http://10.0.0.229:8003/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 986 | 234 | 43.6 | 23.0 | 4223 | 512 |
| 7734 | 889 | 42.3 | 23.7 | 8696 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 43 | 43.4 | 76 | 76 | 1/1 |
| 8 | 263 | 33.2 | 170 | 173 | 8/8 |
| 32 | 723 | 22.8 | 210 | 214 | 32/32 |

