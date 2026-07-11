# Tier 2 — Inference (warmup-discard-fleet-Qwopus-27B-MTP-llamacpp-20260710-072048)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1496 | 22.0 | 46.1 | 680 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 21 | 27.5 | 733 | 733 | 1/1 |
| 16 | 32 | 12.1 | 17268 | 28482 | 16/16 |

