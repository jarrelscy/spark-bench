# Tier 2 — Inference (warmup-discard-ss2-attn-triton-20260709-170338)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 3325 | 112.1 | 9.0 | 306 | 128 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 89 | 135.7 | 498 | 498 | 1/1 |

