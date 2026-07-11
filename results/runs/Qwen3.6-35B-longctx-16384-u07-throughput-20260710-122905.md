# Tier 2 — Inference (Qwen3.6-35B-longctx-16384-u07-throughput-20260710-122905)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 15981 | 7453 | 47.3 | 21.2 | 2144 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 28 | 44.3 | 6592 | 6592 | 1/1 |
| 4 | 23 | 7.9 | 27345 | 31620 | 4/4 |
| 8 | 58 | 15.1 | 34876 | 50725 | 8/8 |
| 16 | 0 | 562500.0 | 103020 | 103027 | 16/16 |
| 24 | ERR | - | - | - | 0 |
| 32 | ERR | - | - | - | 0 |

