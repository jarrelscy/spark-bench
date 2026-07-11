# Tier 2 — Inference (Qwen3.6-27B-NVFP4-OFFICIAL-atlasdev-dflash-throughput-20260711-022243)

- model `atlas-model` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `dflash`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2048 | 12.4 | 81.0 | 497 | 964 |
| 7832 | 13060 | 9.7 | 103.2 | 600 | 970 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 10 | 10.3 | 2032 | 2032 | 1/1 |
| 4 | 16 | 4.1 | 7899 | 7899 | 4/4 |

