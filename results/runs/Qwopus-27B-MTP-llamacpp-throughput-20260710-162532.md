# Tier 2 — Inference (Qwopus-27B-MTP-llamacpp-throughput-20260710-162532)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1221 | 24.7 | 40.6 | 833 | 512 |
| 8006 | 9592 | 25.5 | 39.4 | 835 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 23 | 24.3 | 1076 | 1076 | 1/1 |
| 8 | 61 | 16.9 | 32821 | 37189 | 8/8 |
| 16 | 62 | 17.0 | 65660 | 103652 | 16/16 |

