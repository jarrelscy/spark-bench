# Tier 2 — Inference (warmup-discard-fleet-AEON-Ultimate-MM-NVFP4-MTP-vLLM-20260710-075101)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 807 | 18.5 | 55.0 | 1260 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 17 | 20.5 | 698 | 698 | 1/1 |
| 16 | 72 | 14.6 | 9700 | 9702 | 16/16 |

