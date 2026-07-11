# Tier 2 — Inference (warmup-discard-fleet-Gemma-4-26B-A4B-UDQ4-llamacpp-20260710-071734)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1057 | 582 | 55.5 | 18.3 | 1817 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 49 | 55.5 | 163 | 163 | 1/1 |
| 16 | 64 | 29.1 | 7036 | 14093 | 16/16 |

