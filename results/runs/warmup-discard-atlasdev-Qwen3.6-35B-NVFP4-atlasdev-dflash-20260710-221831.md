# Tier 2 — Inference (warmup-discard-atlasdev-Qwen3.6-35B-NVFP4-atlasdev-dflash-20260710-221831)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 505 | 25.6 | 39.4 | 2016 | 127 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 69 | 89.9 | 490 | 490 | 1/1 |

