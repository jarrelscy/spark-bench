# Tier 2 — Inference (Qwen3.6-27B-NVFP4-OFFICIAL-mtp3-throughput-20260710-093536)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1036 | 25.2 | 39.7 | 982 | 512 |
| 8006 | 7256 | 27.0 | 37.1 | 1103 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 24 | 25.3 | 1025 | 1025 | 1/1 |
| 8 | 116 | 19.4 | 7322 | 7324 | 8/8 |
| 16 | 168 | 15.2 | 14161 | 14337 | 16/16 |

