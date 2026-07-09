# Tier 2 — Inference (Qwen3.6-35B-NVFP4-vllm-eugr0706-dflash-k10-throughput-20260708-183230)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-k10`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 255 | 76.3 | 13.1 | 3986 | 512 |
| 8006 | 1213 | 69.1 | 14.5 | 6602 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 65 | 66.8 | 239 | 239 | 1/1 |
| 8 | 232 | 33.9 | 1314 | 1315 | 8/8 |
| 16 | 301 | 22.1 | 2532 | 2538 | 16/16 |

