# Tier 2 — Inference (Qwen3.6-27B-NVFP4-sgl0515-nospec-throughput-20260711-002535)

- model `sgl27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `none`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 189 | 12.1 | 82.9 | 5393 | 512 |
| 7832 | 7445 | 11.9 | 84.2 | 1052 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 12.0 | 189 | 189 | 1/1 |
| 8 | 84 | 10.6 | 479 | 479 | 8/8 |
| 16 | 145 | 9.3 | 1226 | 1231 | 16/16 |

