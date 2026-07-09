# Tier 2 — Inference (Qwen3.6-35B-NVFP4-atlas-latest-nospec-throughput-20260709-133155)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 462 | 85.9 | 11.7 | 2201 | 868 |
| 8006 | 2970 | 61.1 | 16.4 | 2696 | 852 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 81 | 84.7 | 464 | 464 | 1/1 |
| 8 | 99 | 12.9 | 3634 | 3636 | 8/8 |
| 16 | 101 | 6.7 | 7093 | 7100 | 16/16 |

