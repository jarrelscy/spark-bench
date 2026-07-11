# Tier 2 — Inference (warmup-discard-ss2-batched-16384-20260709-171336)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 2902 | 105.9 | 9.5 | 350 | 128 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 82 | 132.0 | 593 | 593 | 1/1 |

