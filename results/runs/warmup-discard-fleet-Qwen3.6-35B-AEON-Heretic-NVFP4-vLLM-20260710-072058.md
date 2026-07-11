# Tier 2 — Inference (warmup-discard-fleet-Qwen3.6-35B-AEON-Heretic-NVFP4-vLLM-20260710-072058)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 234 | 42.8 | 23.8 | 4339 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 38 | 42.8 | 188 | 188 | 1/1 |
| 16 | 211 | 22.2 | 1784 | 2244 | 16/16 |

