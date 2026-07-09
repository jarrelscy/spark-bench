# Tier 2 — Inference (warmup-discard-NVFP4-vllm-eugr0706-dflash-k10-20260708-183218)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 666 | 70.2 | 14.5 | 1527 | 64 |
| 8006 | 1261 | 110.0 | 9.2 | 6349 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 43 | 73.6 | 607 | 607 | 1/1 |
| 8 | 175 | 52.0 | 1451 | 1453 | 8/8 |
| 16 | 221 | 34.5 | 2529 | 2535 | 16/16 |

