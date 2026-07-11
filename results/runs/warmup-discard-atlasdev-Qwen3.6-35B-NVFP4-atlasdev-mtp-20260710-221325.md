# Tier 2 — Inference (warmup-discard-atlasdev-Qwen3.6-35B-NVFP4-atlasdev-mtp-20260710-221325)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 443 | 96.0 | 10.5 | 2293 | 127 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 78 | 102.6 | 429 | 429 | 1/1 |

