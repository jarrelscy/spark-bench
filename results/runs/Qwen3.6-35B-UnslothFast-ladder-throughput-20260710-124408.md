# Tier 2 — Inference (Qwen3.6-35B-UnslothFast-ladder-throughput-20260710-124408)

- model `fast35b` @ `http://10.0.0.120:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 228 | 92.4 | 10.8 | 4468 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 87 | 90.4 | 223 | 223 | 1/1 |
| 8 | 304 | 42.4 | 1154 | 1156 | 8/8 |
| 16 | 420 | 30.5 | 2226 | 2297 | 16/16 |
| 24 | 494 | 24.6 | 3374 | 3465 | 24/24 |
| 32 | 549 | 20.3 | 3556 | 4619 | 32/32 |
| 48 | 633 | 15.7 | 4745 | 7053 | 48/48 |
| 64 | 685 | 12.7 | 5926 | 9556 | 64/64 |

