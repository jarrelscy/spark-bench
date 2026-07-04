# Tier 2 — Inference (warmup-discard-NVFP4-vllm-aeon023-20260702-234646)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 259 | 79.1 | 12.8 | 3933 | 64 |
| 8006 | 1500 | 75.0 | 13.5 | 5338 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 63 | 78.7 | 201 | 201 | 1/1 |
| 8 | 161 | 32.9 | 1196 | 1557 | 8/8 |
| 16 | 213 | 20.9 | 1528 | 2517 | 16/16 |

