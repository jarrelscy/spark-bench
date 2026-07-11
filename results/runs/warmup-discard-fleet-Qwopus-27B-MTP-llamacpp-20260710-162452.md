# Tier 2 — Inference (warmup-discard-fleet-Qwopus-27B-MTP-llamacpp-20260710-162452)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1504 | 22.1 | 46.0 | 676 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 21 | 27.6 | 733 | 733 | 1/1 |
| 16 | 32 | 11.6 | 16656 | 27601 | 16/16 |

