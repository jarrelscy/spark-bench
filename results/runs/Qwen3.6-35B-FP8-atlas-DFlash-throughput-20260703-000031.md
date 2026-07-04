# Tier 2 — Inference (Qwen3.6-35B-FP8-atlas-DFlash-throughput-20260703-000031)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 789 | 43.3 | 23.1 | 1290 | 923 |
| 8006 | 3647 | 42.5 | 23.5 | 2195 | 898 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 51 | 52.7 | 767 | 767 | 1/1 |
| 8 | 52 | 7.1 | 6084 | 6086 | 8/8 |
| 16 | 1 | 0.2 | 12189 | 12193 | 16/16 |

