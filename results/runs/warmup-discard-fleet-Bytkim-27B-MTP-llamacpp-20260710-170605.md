# Tier 2 — Inference (warmup-discard-fleet-Bytkim-27B-MTP-llamacpp-20260710-170605)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1520 | 23.7 | 42.8 | 669 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 20 | 25.9 | 738 | 738 | 1/1 |
| 16 | 34 | 13.0 | 17321 | 26519 | 16/16 |

