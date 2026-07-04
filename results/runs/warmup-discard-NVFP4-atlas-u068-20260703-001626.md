# Tier 2 — Inference (warmup-discard-NVFP4-atlas-u068-20260703-001626)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 497 | 89.4 | 11.3 | 2047 | 124 |
| 8006 | 2981 | 63.7 | 15.8 | 2685 | 136 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 70 | 89.4 | 456 | 456 | 1/1 |
| 8 | 80 | 13.4 | 3578 | 3579 | 8/8 |
| 16 | 82 | 6.8 | 7098 | 7101 | 16/16 |

