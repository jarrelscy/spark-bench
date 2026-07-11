# Tier 2 — Inference (Qwen3.6-27B-base-MTP-llamacpp-throughput-20260710-073504)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1106 | 21.6 | 46.3 | 919 | 512 |
| 8006 | 9748 | 23.6 | 42.4 | 821 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 21 | 22.1 | 1061 | 1061 | 1/1 |
| 8 | 53 | 14.7 | 39374 | 43196 | 8/8 |
| 16 | 55 | 14.6 | 73418 | 117285 | 16/16 |

