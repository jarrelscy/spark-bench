# Tier 2 — Inference (Qwen3.6-35B-longctx-32768-u07-throughput-20260710-123404)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 32768 | ERR | - | - | - | - |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | ERR | - | - | - | 0 |
| 4 | ERR | - | - | - | 0 |
| 8 | ERR | - | - | - | 0 |
| 16 | ERR | - | - | - | 0 |
| 24 | ERR | - | - | - | 0 |
| 32 | ERR | - | - | - | 0 |

