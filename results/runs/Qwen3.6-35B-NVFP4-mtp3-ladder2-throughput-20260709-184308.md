# Tier 2 — Inference (Qwen3.6-35B-NVFP4-mtp3-ladder2-throughput-20260709-184308)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 233 | 100.2 | 10.0 | 4358 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 64 | 696 | 13.0 | 6058 | 9776 | 64/64 |
| 96 | 6 | 10416.9 | 8538 | 15903 | 96/96 |
| 128 | ERR | - | - | - | 0 |
| 160 | ERR | - | - | - | 0 |
| 192 | ERR | - | - | - | 0 |

