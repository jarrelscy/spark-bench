# Tier 2 — Inference (Qwen3.6-27B-NVFP4-mtp2-restored-throughput-20260709-230305)

- model `qwen36-27b-nvfp4-mtp` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp2`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 513 | 20.1 | 49.9 | 1983 | 512 |
| 8006 | 3716 | 21.2 | 47.2 | 2155 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 20 | 20.9 | 494 | 494 | 1/1 |
| 8 | 124 | 17.5 | 3592 | 3595 | 8/8 |
| 16 | 164 | 12.1 | 7032 | 7229 | 16/16 |

