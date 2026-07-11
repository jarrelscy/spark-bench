# Tier 2 — Inference (Qwen3.6-35B-longctxV4ext-32768-u0.7-throughput-20260710-172002)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 5862 | 99.4 | 10.1 | 5452 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 8 | 66 | 19.5 | 32358 | 49098 | 8/8 |
| 16 | 70 | 10.7 | 56682 | 97933 | 16/16 |

