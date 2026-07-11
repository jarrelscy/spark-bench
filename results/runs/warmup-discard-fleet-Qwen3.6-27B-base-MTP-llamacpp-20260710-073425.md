# Tier 2 — Inference (warmup-discard-fleet-Qwen3.6-27B-base-MTP-llamacpp-20260710-073425)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1543 | 26.1 | 38.9 | 659 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 20 | 25.7 | 749 | 749 | 1/1 |
| 16 | 33 | 12.1 | 17078 | 27781 | 16/16 |

