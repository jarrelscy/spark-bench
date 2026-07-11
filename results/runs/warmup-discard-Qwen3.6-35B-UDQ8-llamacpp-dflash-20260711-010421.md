# Tier 2 — Inference (warmup-discard-Qwen3.6-35B-UDQ8-llamacpp-dflash-20260711-010421)

- model `llamacpp-35b` @ `http://10.0.0.120:8080/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1855 | 53.4 | 19.0 | 548 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 57 | 84.1 | 352 | 352 | 1/1 |

