# Tier 2 — Inference (SS-dflash16-throughput-20260709-171939)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-k16`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 257 | 71.5 | 14.0 | 3963 | 512 |
| 8006 | 1241 | 62.1 | 16.1 | 6449 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 57 | 58.6 | 247 | 247 | 1/1 |

