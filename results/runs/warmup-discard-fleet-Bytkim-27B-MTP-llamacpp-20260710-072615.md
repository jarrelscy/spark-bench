# Tier 2 — Inference (warmup-discard-fleet-Bytkim-27B-MTP-llamacpp-20260710-072615)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1520 | 23.9 | 42.5 | 669 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 20 | 26.1 | 731 | 731 | 1/1 |
| 16 | 32 | 12.8 | 18012 | 27792 | 16/16 |

