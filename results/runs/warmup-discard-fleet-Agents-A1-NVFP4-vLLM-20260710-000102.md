# Tier 2 — Inference (warmup-discard-fleet-Agents-A1-NVFP4-vLLM-20260710-000102)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 237 | 38.8 | 26.2 | 4289 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 35 | 38.7 | 189 | 189 | 1/1 |
| 16 | 219 | 24.2 | 1815 | 2298 | 16/16 |

