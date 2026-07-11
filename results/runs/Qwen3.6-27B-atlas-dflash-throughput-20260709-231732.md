# Tier 2 — Inference (Qwen3.6-27B-atlas-dflash-throughput-20260709-231732)

- model `qwen36-27b` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `dflash`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2106 | 13.5 | 74.0 | 483 | 998 |
| 8006 | 13660 | 12.3 | 81.6 | 586 | 913 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 13 | 13.5 | 2092 | 2092 | 1/1 |
| 4 | 14 | 3.5 | 8400 | 8400 | 4/4 |

