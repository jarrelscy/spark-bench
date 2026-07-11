# Tier 2 — Inference (warmup-discard-sgl0515-Qwen3.6-35B-NVFP4-sgl0515-nospec-20260710-213710)

- model `sgl35b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 272 | 69.9 | 14.5 | 3739 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 60 | 69.3 | 135 | 135 | 1/1 |
| 16 | 405 | 29.9 | 392 | 395 | 16/16 |

