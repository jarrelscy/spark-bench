# Tier 2 — Inference (Qwen3.6-27B-NVFP4-sgl0515-nospec-throughput-20260711-000746)

- model `sgl27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `none`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 194 | 12.1 | 82.8 | 5229 | 512 |
| 7832 | 7442 | 11.9 | 83.9 | 1052 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 12.1 | 189 | 189 | 1/1 |
| 8 | 84 | 10.6 | 480 | 482 | 8/8 |
| 16 | 146 | 9.3 | 1224 | 1230 | 16/16 |

