# Tier 2 — Inference (Qwen3.6-35B-NVFP4-sgl0515-mtp-NEXTN-throughput-20260710-214552)

- model `sgl35b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp-nextn3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 161 | 106.7 | 9.4 | 6311 | 512 |
| 8006 | 1497 | 99.7 | 10.0 | 5348 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 95 | 97.1 | 101 | 101 | 1/1 |
| 8 | 289 | 38.0 | 335 | 341 | 8/8 |
| 16 | 427 | 28.0 | 269 | 271 | 16/16 |

