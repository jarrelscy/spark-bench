# Tier 2 — Inference (warmup-discard-Qwen3.6-35B-UDQ8-llamacpp-20260709-084854)

- model `udq8` @ `http://10.0.0.120:8000/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 679 | 57.2 | 17.7 | 1498 | 64 |
| 8006 | 3995 | 54.6 | 18.6 | 2004 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 42 | 57.1 | 413 | 413 | 1/1 |
| 8 | 66 | 28.1 | 4247 | 5787 | 8/8 |
| 16 | 72 | 30.9 | 8937 | 12490 | 16/16 |

