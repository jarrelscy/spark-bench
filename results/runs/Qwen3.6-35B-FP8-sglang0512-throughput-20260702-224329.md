# Tier 2 — Inference (Qwen3.6-35B-FP8-sglang0512-throughput-20260702-224329)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8892/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 256 | 51.3 | 19.5 | 3973 | 512 |
| 8006 | 1252 | 49.5 | 20.2 | 6394 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 50 | 51.1 | 252 | 252 | 1/1 |
| 8 | 308 | 41.9 | 1280 | 1282 | 8/8 |
| 16 | 261 | 28.3 | 2222 | 21306 | 16/16 |

