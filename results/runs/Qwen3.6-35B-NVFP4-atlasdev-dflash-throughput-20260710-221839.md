# Tier 2 — Inference (Qwen3.6-35B-NVFP4-atlasdev-dflash-throughput-20260710-221839)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `dflash`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 494 | 86.6 | 11.6 | 2057 | 930 |
| 8006 | 3084 | 49.6 | 20.2 | 2596 | 890 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 61 | 63.1 | 492 | 492 | 1/1 |
| 4 | 105 | 28.2 | 1915 | 1915 | 4/4 |

