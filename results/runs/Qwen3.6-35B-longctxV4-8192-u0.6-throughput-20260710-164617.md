# Tier 2 — Inference (Qwen3.6-35B-longctxV4-8192-u0.6-throughput-20260710-164617)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 8006 | 1178 | 105.6 | 9.5 | 6795 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 84 | 103.8 | 1166 | 1166 | 1/1 |
| 4 | 142 | 54.4 | 5464 | 5510 | 4/4 |
| 8 | 194 | 36.6 | 7204 | 9549 | 8/8 |
| 16 | 229 | 22.6 | 12140 | 19457 | 16/16 |

