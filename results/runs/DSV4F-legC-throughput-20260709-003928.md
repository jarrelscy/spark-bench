# Tier 2 — Inference (DSV4F-legC-throughput-20260709-003928)

- model `dsv4f` @ `http://10.0.0.109:8888/v1`  topology `2x DGX Spark` parallelism `1` spec_decode `mtp2`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1008 | 396 | 38.2 | 26.2 | 2545 | 512 |
| 7997 | 6136 | 37.8 | 26.5 | 1303 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 37 | 38.4 | 425 | 425 | 1/1 |
| 8 | 171 | 22.5 | 944 | 946 | 8/8 |
| 16 | 286 | 19.6 | 1939 | 1944 | 16/16 |

