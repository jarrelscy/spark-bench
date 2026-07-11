# Tier 2 — Inference (Qwopus-27B-MTP-llamacpp-throughput-20260710-072128)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 978 | 24.3 | 41.3 | 1040 | 512 |
| 8006 | 9506 | 24.5 | 40.9 | 842 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 25 | 25.9 | 1068 | 1068 | 1/1 |
| 8 | 60 | 17.0 | 33236 | 39125 | 8/8 |
| 16 | 62 | 16.9 | 66356 | 104168 | 16/16 |

