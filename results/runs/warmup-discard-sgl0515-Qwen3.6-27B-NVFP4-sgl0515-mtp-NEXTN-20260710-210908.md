# Tier 2 — Inference (warmup-discard-sgl0515-Qwen3.6-27B-NVFP4-sgl0515-mtp-NEXTN-20260710-210908)

- model `sgl27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 935 | 26.3 | 38.6 | 1087 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 26 | 28.9 | 280 | 280 | 1/1 |
| 16 | 122 | 16.7 | 1275 | 5936 | 16/16 |

