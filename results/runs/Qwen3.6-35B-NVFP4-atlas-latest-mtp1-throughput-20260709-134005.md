# Tier 2 — Inference (Qwen3.6-35B-NVFP4-atlas-latest-mtp1-throughput-20260709-134005)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `mtp1`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 465 | 95.0 | 10.5 | 2187 | 902 |
| 8006 | 2977 | 71.5 | 14.0 | 2689 | 925 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 90 | 94.8 | 462 | 462 | 1/1 |
| 4 | 94 | 24.6 | 1807 | 1807 | 4/4 |

