# Tier 2 — Inference (warmup-discard-fleet-Qwythos-9B-vLLM-20260710-081448)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 287 | 13.0 | 78.3 | 3539 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 13.0 | 240 | 240 | 1/1 |
| 16 | 121 | 11.0 | 1949 | 3347 | 16/16 |

