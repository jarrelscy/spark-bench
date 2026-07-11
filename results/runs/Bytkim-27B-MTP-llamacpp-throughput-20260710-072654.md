# Tier 2 — Inference (Bytkim-27B-MTP-llamacpp-throughput-20260710-072654)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1228 | 23.6 | 42.5 | 828 | 512 |
| 8006 | 9566 | 24.2 | 41.4 | 837 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 21 | 22.4 | 1034 | 1034 | 1/1 |
| 8 | 57 | 15.7 | 34102 | 39773 | 8/8 |
| 16 | 57 | 15.2 | 70921 | 113547 | 16/16 |

