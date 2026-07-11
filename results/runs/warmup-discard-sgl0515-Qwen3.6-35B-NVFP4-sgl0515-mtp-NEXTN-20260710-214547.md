# Tier 2 — Inference (warmup-discard-sgl0515-Qwen3.6-35B-NVFP4-sgl0515-mtp-NEXTN-20260710-214547)

- model `sgl35b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 512 | 98.0 | 10.4 | 1985 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 69 | 107.5 | 337 | 337 | 1/1 |
| 16 | 366 | 35.9 | 749 | 753 | 16/16 |

