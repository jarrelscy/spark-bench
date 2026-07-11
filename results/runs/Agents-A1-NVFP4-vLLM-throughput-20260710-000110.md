# Tier 2 — Inference (Agents-A1-NVFP4-vLLM-throughput-20260710-000110)

- model `fleet-model` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode ``

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 207 | 38.2 | 26.2 | 4906 | 512 |
| 8006 | 1152 | 37.6 | 26.6 | 6948 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 38 | 38.2 | 189 | 189 | 1/1 |
| 8 | 212 | 28.1 | 1157 | 1158 | 8/8 |
| 16 | 322 | 21.8 | 1767 | 2251 | 16/16 |

