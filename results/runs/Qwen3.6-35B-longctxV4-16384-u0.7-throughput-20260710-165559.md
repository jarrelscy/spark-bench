# Tier 2 — Inference (Qwen3.6-35B-longctxV4-16384-u0.7-throughput-20260710-165559)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 15981 | 2556 | 101.7 | 9.8 | 6253 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 66 | 98.0 | 2535 | 2535 | 1/1 |
| 4 | 107 | 47.3 | 9052 | 10404 | 4/4 |
| 8 | 125 | 28.8 | 14372 | 20857 | 8/8 |

