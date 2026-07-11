# Tier 2 — Inference (Qwen3.6-27B-NVFP4-OFFICIAL-atlasdev-mtp-throughput-20260711-015648)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `mtp1`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1990 | 14.8 | 67.8 | 511 | 938 |
| 7832 | 12848 | 13.9 | 72.0 | 610 | 973 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 14 | 14.7 | 1971 | 1971 | 1/1 |
| 4 | 16 | 4.1 | 7657 | 7658 | 4/4 |

