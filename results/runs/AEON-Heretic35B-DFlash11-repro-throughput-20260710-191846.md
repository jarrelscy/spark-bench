# Tier 2 — Inference (AEON-Heretic35B-DFlash11-repro-throughput-20260710-191846)

- model `qwen36-35b-heretic` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `dflash11`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 420 | 70.2 | 14.3 | 2422 | 512 |
| 8006 | 1376 | 73.9 | 13.6 | 5817 | 512 |
| 31960 | 5628 | 60.2 | 16.6 | 5678 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 67 | 69.2 | 252 | 252 | 1/1 |
| 8 | 198 | 29.6 | 1954 | 1956 | 8/8 |

