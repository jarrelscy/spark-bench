# Tier 2 — Inference (Ornith-35B-NVFP4-vLLM-throughput-20260710-074325)

- model `fleet-model` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 209 | 38.1 | 26.3 | 4873 | 512 |
| 8006 | 1242 | 37.6 | 26.6 | 6446 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 38 | 38.1 | 197 | 197 | 1/1 |
| 8 | 219 | 29.2 | 1241 | 1243 | 8/8 |
| 16 | 330 | 22.5 | 1849 | 2442 | 16/16 |

