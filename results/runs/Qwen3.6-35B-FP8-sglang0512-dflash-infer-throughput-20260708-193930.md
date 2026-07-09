# Tier 2 — Inference (Qwen3.6-35B-FP8-sglang0512-dflash-infer-throughput-20260708-193930)

- model `qwen` @ `http://10.0.0.183:8899/v1`  topology `single` parallelism `1` spec_decode `dflash`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 258 | 54.3 | 18.4 | 3941 | 512 |
| 8006 | 1283 | 37.5 | 26.7 | 6239 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 54 | 55.1 | 246 | 246 | 1/1 |
| 8 | 177 | 23.4 | 1310 | 1313 | 8/8 |
| 16 | 175 | 16.5 | 1472 | 34668 | 16/16 |

