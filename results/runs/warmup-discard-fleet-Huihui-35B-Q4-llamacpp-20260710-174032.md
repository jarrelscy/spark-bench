# Tier 2 — Inference (warmup-discard-fleet-Huihui-35B-Q4-llamacpp-20260710-174032)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 547 | 78.5 | 12.9 | 1861 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 59 | 78.7 | 265 | 265 | 1/1 |
| 16 | 89 | 34.6 | 6423 | 10068 | 16/16 |

