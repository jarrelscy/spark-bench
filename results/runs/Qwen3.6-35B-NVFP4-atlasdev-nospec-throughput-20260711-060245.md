# Tier 2 — Inference (Qwen3.6-35B-NVFP4-atlasdev-nospec-throughput-20260711-060245)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `none`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 435 | 86.3 | 11.6 | 2338 | 868 |
| 7832 | 2724 | 62.0 | 16.1 | 2875 | 924 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 83 | 85.8 | 432 | 432 | 1/1 |
| 4 | 105 | 27.7 | 1694 | 1696 | 4/4 |

