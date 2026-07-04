# Tier 2 — Inference (Qwen3.6-35B-FP8-vllm-aeon023-throughput-20260702-222509)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 264 | 53.5 | 18.7 | 3853 | 512 |
| 8006 | 1418 | 51.7 | 19.4 | 5644 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 52 | 53.4 | 247 | 247 | 1/1 |
| 8 | 169 | 22.1 | 1201 | 1401 | 8/8 |
| 16 | 255 | 16.9 | 1919 | 2825 | 16/16 |

