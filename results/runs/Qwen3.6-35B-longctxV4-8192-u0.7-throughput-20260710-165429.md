# Tier 2 — Inference (Qwen3.6-35B-longctxV4-8192-u0.7-throughput-20260710-165429)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 8006 | 1196 | 106.6 | 9.4 | 6692 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 81 | 99.9 | 1184 | 1184 | 1/1 |
| 4 | 148 | 57.5 | 5599 | 5643 | 4/4 |
| 8 | 189 | 35.4 | 7241 | 9700 | 8/8 |
| 16 | 228 | 22.7 | 12169 | 19619 | 16/16 |

