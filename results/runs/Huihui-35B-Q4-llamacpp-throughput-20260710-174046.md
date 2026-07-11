# Tier 2 — Inference (Huihui-35B-Q4-llamacpp-throughput-20260710-174046)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 424 | 77.6 | 12.9 | 2396 | 512 |
| 8006 | 3347 | 73.2 | 13.7 | 2392 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 74 | 78.1 | 383 | 383 | 1/1 |
| 8 | 141 | 38.3 | 15151 | 15981 | 8/8 |
| 16 | 139 | 39.5 | 31658 | 46225 | 16/16 |

