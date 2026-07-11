# Tier 2 — Inference (Qwen3.6-35B-longctxV4ceil-32768-u0.7-throughput-20260710-173414)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 5824 | 95.8 | 10.5 | 5488 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 24 | 72 | 7.6 | 80411 | 148351 | 24/24 |
| 32 | 73 | 6.0 | 105248 | 198720 | 32/32 |
| 48 | 74 | 4.4 | 156072 | 304361 | 48/48 |
| 64 | 74 | 3.7 | 206294 | 407321 | 64/64 |

