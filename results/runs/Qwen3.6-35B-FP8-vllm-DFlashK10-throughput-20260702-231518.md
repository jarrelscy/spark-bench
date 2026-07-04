# Tier 2 — Inference (Qwen3.6-35B-FP8-vllm-DFlashK10-throughput-20260702-231518)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 51521 | 64.9 | 15.4 | 20 | 512 |
| 8006 | 1741 | 61.3 | 16.4 | 4599 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 63 | 64.7 | 265 | 265 | 1/1 |
| 8 | 171 | 25.4 | 2233 | 2555 | 8/8 |
| 16 | 234 | 17.2 | 2111 | 3759 | 16/16 |

