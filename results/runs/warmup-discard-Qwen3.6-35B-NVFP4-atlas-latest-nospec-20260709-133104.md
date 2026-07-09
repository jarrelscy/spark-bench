# Tier 2 — Inference (warmup-discard-Qwen3.6-35B-NVFP4-atlas-latest-nospec-20260709-133104)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 484 | 89.6 | 11.3 | 2103 | 127 |
| 8006 | 2970 | 64.7 | 15.6 | 2696 | 133 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 69 | 89.6 | 461 | 461 | 1/1 |
| 8 | 80 | 13.4 | 3572 | 3574 | 8/8 |
| 16 | 82 | 6.9 | 7116 | 7119 | 16/16 |

