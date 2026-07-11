# Tier 2 — Inference (Qwen3.6-27B-atlas-nospec-throughput-20260709-230648)

- model `qwen36-27b` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2024 | 13.6 | 73.9 | 502 | 998 |
| 8006 | 13389 | 12.3 | 81.7 | 598 | 913 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 13 | 13.5 | 2014 | 2014 | 1/1 |
| 4 | 14 | 3.5 | 8071 | 8071 | 4/4 |

