# Tier 2 — Inference (Qwen3.6-35B-UDQ8-llamacpp-throughput-20260709-084925)

- model `udq8` @ `http://10.0.0.120:8000/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 428 | 56.0 | 17.9 | 2378 | 512 |
| 8006 | 4052 | 53.9 | 18.6 | 1976 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 54 | 56.4 | 447 | 447 | 1/1 |
| 8 | 102 | 27.7 | 20464 | 21937 | 8/8 |
| 16 | 105 | 29.2 | 40640 | 60270 | 16/16 |

