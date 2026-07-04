# Tier 2 — Inference (Nemotron3-Super-120B-NVFP4-vllm-1Spark-throughput-20260703-115653)

- model `nemotron-super` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1092 | 959 | 15.7 | 63.9 | 1139 | 512 |
| 8563 | 3689 | 15.6 | 64.1 | 2322 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 15 | 15.6 | 605 | 605 | 1/1 |
| 8 | 61 | 8.0 | 3326 | 4226 | 8/8 |
| 16 | 86 | 5.7 | 4989 | 7940 | 16/16 |

