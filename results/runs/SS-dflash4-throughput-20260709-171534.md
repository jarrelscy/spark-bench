# Tier 2 — Inference (SS-dflash4-throughput-20260709-171534)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `dflash-k4`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 245 | 80.2 | 12.5 | 4144 | 512 |
| 8006 | 1340 | 75.1 | 13.3 | 5974 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 75 | 77.5 | 233 | 233 | 1/1 |

