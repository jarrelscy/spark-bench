# Tier 2 — Inference (Qwen3.6-35B-NVFP4-atlasdev-mtp-throughput-20260710-221329)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `mtp1`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 436 | 97.0 | 10.3 | 2333 | 928 |
| 8006 | 2774 | 71.7 | 14.0 | 2886 | 889 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 91 | 95.4 | 430 | 430 | 1/1 |
| 4 | 105 | 28.1 | 1683 | 1683 | 4/4 |

