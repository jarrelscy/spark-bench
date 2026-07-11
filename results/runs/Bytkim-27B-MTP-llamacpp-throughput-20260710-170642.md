# Tier 2 — Inference (Bytkim-27B-MTP-llamacpp-throughput-20260710-170642)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1240 | 23.2 | 43.2 | 820 | 512 |
| 8006 | 9668 | 23.5 | 42.6 | 828 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 21 | 22.3 | 1065 | 1065 | 1/1 |
| 8 | 55 | 15.3 | 35858 | 40827 | 8/8 |
| 16 | 56 | 15.0 | 76852 | 114889 | 16/16 |

