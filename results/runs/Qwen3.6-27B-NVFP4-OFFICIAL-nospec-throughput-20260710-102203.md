# Tier 2 — Inference (Qwen3.6-27B-NVFP4-OFFICIAL-nospec-throughput-20260710-102203)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 894 | 12.4 | 80.8 | 1137 | 512 |
| 8006 | 6863 | 12.3 | 81.7 | 1167 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 12.4 | 875 | 875 | 1/1 |
| 8 | 76 | 10.8 | 6846 | 6849 | 8/8 |
| 16 | 121 | 9.2 | 11468 | 13667 | 16/16 |

