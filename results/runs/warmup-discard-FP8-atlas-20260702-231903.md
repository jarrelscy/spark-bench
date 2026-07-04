# Tier 2 — Inference (warmup-discard-FP8-atlas-20260702-231903)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 681 | 54.8 | 18.4 | 1494 | 136 |
| 8006 | 3332 | 43.9 | 23.0 | 2402 | 126 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 43 | 55.0 | 684 | 684 | 1/1 |
| 8 | 45 | 7.3 | 5424 | 5425 | 8/8 |
| 16 | 45 | 3.7 | 10802 | 10806 | 16/16 |

