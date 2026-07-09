# Tier 2 — Inference (warmup-discard-Qwen3.6-35B-FP8-sglang0512-mtp-NEXTN-20260708-193100)

- model `qwen` @ `http://10.0.0.183:8899/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1045 | 65.5 | 15.5 | 973 | 64 |
| 8006 | 1765 | 74.0 | 13.7 | 4536 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 53 | 76.0 | 363 | 363 | 1/1 |
| 8 | 170 | 48.4 | 1663 | 1665 | 8/8 |
| 16 | 163 | 33.2 | 2937 | 5414 | 16/16 |

