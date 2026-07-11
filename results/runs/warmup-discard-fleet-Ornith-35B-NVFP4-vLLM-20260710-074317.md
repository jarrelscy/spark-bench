# Tier 2 — Inference (warmup-discard-fleet-Ornith-35B-NVFP4-vLLM-20260710-074317)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 249 | 38.9 | 26.1 | 4086 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 35 | 38.6 | 193 | 193 | 1/1 |
| 16 | 213 | 24.1 | 1876 | 2464 | 16/16 |

