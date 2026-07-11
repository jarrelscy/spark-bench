# Tier 2 — Inference (warmup-discard-fleet-Qwopus-AWQ-vLLM-20260710-085013)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1063 | 9.6 | 106.2 | 956 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 8 | 9.6 | 1019 | 1019 | 1/1 |
| 16 | 43 | 6.7 | 13239 | 15591 | 16/16 |

