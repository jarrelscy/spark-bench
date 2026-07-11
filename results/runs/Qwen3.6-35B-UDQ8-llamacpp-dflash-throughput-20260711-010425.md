# Tier 2 — Inference (Qwen3.6-35B-UDQ8-llamacpp-dflash-throughput-20260711-010425)

- model `llamacpp-35b` @ `http://10.0.0.120:8080/v1`  topology `single` parallelism `1` spec_decode `dflash`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 366 | 52.9 | 19.0 | 2780 | 512 |
| 7832 | 4297 | 50.6 | 19.8 | 1823 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 50 | 52.0 | 445 | 445 | 1/1 |
| 8 | 83 | 23.0 | 25002 | 29038 | 8/8 |
| 16 | 81 | 22.2 | 47204 | 83709 | 16/16 |

