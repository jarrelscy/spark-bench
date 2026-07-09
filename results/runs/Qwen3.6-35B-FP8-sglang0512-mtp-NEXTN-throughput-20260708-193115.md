# Tier 2 — Inference (Qwen3.6-35B-FP8-sglang0512-mtp-NEXTN-throughput-20260708-193115)

- model `qwen` @ `http://10.0.0.183:8899/v1`  topology `single` parallelism `1` spec_decode `mtp`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 307 | 60.3 | 16.6 | 3307 | 512 |
| 8006 | 1348 | 59.3 | 16.9 | 5939 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 59 | 61.5 | 297 | 297 | 1/1 |
| 8 | 279 | 38.8 | 1384 | 1387 | 8/8 |
| 16 | 252 | 26.2 | 2383 | 23371 | 16/16 |

