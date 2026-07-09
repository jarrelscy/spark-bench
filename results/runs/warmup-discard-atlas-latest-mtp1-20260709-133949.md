# Tier 2 — Inference (warmup-discard-atlas-latest-mtp1-20260709-133949)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 496 | 95.0 | 10.6 | 2049 | 127 |
| 8006 | 2970 | 75.2 | 13.4 | 2695 | 133 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 75 | 99.8 | 461 | 461 | 1/1 |
| 4 | 78 | 25.7 | 1803 | 1804 | 4/4 |

