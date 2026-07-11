# Tier 2 — Inference (AEON-Ultimate-MM-NVFP4-MTP-vLLM-throughput-20260710-075123)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 693 | 16.9 | 59.3 | 1468 | 512 |
| 8006 | 4518 | 15.6 | 64.3 | 1772 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 15 | 15.8 | 677 | 677 | 1/1 |
| 8 | 94 | 13.4 | 4575 | 4577 | 8/8 |
| 16 | 156 | 11.8 | 8819 | 9044 | 16/16 |

