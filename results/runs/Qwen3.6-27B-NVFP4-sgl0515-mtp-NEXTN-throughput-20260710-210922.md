# Tier 2 — Inference (Qwen3.6-27B-NVFP4-sgl0515-mtp-NEXTN-throughput-20260710-210922)

- model `sgl27b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp-nextn3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 205 | 26.3 | 38.1 | 4954 | 512 |
| 8006 | 7173 | 26.2 | 38.2 | 1116 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 25 | 25.7 | 225 | 225 | 1/1 |
| 8 | 137 | 17.9 | 578 | 580 | 8/8 |
| 16 | 140 | 15.5 | 1105 | 36889 | 16/16 |

