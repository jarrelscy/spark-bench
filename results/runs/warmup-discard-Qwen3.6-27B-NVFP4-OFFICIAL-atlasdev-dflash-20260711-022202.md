# Tier 2 — Inference (warmup-discard-Qwen3.6-27B-NVFP4-OFFICIAL-atlasdev-dflash-20260711-022202)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2059 | 5.6 | 181.0 | 494 | 141 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 11 | 12.8 | 2031 | 2031 | 1/1 |

