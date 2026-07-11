# Tier 2 — Inference (warmup-discard-Qwen3.6-27B-NVFP4-OFFICIAL-atlasdev-mtp-20260711-015625)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1993 | 14.8 | 68.0 | 510 | 141 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 12 | 14.7 | 1966 | 1966 | 1/1 |

