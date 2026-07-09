# Tier 2 — Inference (warmup-discard-NVFP4-vllm-eugr0706-recipe-mtp3-20260708-171212)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 985 | 88.8 | 11.4 | 1033 | 64 |
| 8006 | 1403 | 126.2 | 8.0 | 5708 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 60 | 137.1 | 600 | 600 | 1/1 |
| 8 | 150 | 63.9 | 2256 | 2258 | 8/8 |
| 16 | 223 | 43.2 | 2612 | 2765 | 16/16 |

