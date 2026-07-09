# Tier 2 — Inference (Qwen3.6-35B-FP8-sglang0512-nospec-throughput-20260708-192419)

- model `qwen` @ `http://10.0.0.183:8899/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 256 | 50.9 | 19.7 | 3971 | 512 |
| 8006 | 1257 | 49.3 | 20.3 | 6369 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 50 | 50.8 | 255 | 255 | 1/1 |
| 8 | 244 | 33.0 | 1400 | 1403 | 8/8 |
| 16 | 260 | 28.1 | 2087 | 21452 | 16/16 |

