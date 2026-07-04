# Tier 2 — Inference (Qwen3.6-35B-FP8-atlas-throughput-20260702-232024)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 683 | 52.7 | 19.0 | 1490 | 900 |
| 8006 | 3339 | 42.2 | 23.7 | 2397 | 898 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 51 | 52.4 | 688 | 688 | 1/1 |
| 8 | 54 | 7.0 | 5411 | 5412 | 8/8 |
| 16 | 55 | 3.6 | 10806 | 10811 | 16/16 |

