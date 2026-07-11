# Tier 2 — Inference (warmup-discard-fleet-Qwen3.6-27B-NVFP4-OFFICIAL-mtp3-20260710-093509)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 1417 | 26.3 | 38.6 | 718 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 17 | 26.3 | 1247 | 1247 | 1/1 |
| 16 | 51 | 15.2 | 15120 | 15373 | 16/16 |

