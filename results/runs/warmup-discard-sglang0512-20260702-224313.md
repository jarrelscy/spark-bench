# Tier 2 — Inference (warmup-discard-sglang0512-20260702-224313)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8892/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 919 | 51.9 | 19.6 | 1106 | 64 |
| 8006 | 1719 | 50.2 | 20.2 | 4658 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 42 | 52.1 | 309 | 309 | 1/1 |
| 8 | 165 | 35.1 | 1384 | 1385 | 8/8 |
| 16 | 156 | 26.1 | 2550 | 5314 | 16/16 |

