# Tier 2 — Inference (Qwen3.6-35B-FP8-vllm-MTP2-throughput-20260703-001142)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 32287 | 61.2 | 16.4 | 31 | 512 |
| 8006 | 1753 | 59.5 | 16.8 | 4566 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 61 | 63.2 | 297 | 297 | 1/1 |
| 8 | 208 | 30.1 | 2351 | 2378 | 8/8 |
| 16 | 313 | 21.7 | 2163 | 3231 | 16/16 |

