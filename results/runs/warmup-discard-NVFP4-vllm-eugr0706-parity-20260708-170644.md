# Tier 2 — Inference (warmup-discard-NVFP4-vllm-eugr0706-parity-20260708-170644)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 597 | 78.9 | 12.9 | 1705 | 64 |
| 8006 | 1469 | 75.3 | 13.5 | 5451 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 47 | 79.0 | 550 | 550 | 1/1 |
| 8 | 161 | 30.3 | 906 | 1506 | 8/8 |
| 16 | 192 | 20.2 | 2015 | 3062 | 16/16 |

