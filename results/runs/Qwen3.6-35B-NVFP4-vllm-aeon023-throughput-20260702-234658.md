# Tier 2 — Inference (Qwen3.6-35B-NVFP4-vllm-aeon023-throughput-20260702-234658)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 200 | 77.5 | 12.9 | 5085 | 512 |
| 8006 | 1220 | 74.0 | 13.5 | 6562 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 75 | 77.6 | 185 | 185 | 1/1 |
| 8 | 264 | 35.1 | 913 | 1270 | 8/8 |
| 16 | 377 | 25.4 | 1659 | 2473 | 16/16 |

