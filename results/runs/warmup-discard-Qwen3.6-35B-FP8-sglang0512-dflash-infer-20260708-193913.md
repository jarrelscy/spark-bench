# Tier 2 — Inference (warmup-discard-Qwen3.6-35B-FP8-sglang0512-dflash-infer-20260708-193913)

- model `qwen` @ `http://10.0.0.183:8899/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 885 | 85.6 | 11.9 | 1149 | 64 |
| 8006 | 1970 | 39.1 | 26.0 | 4063 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 59 | 82.2 | 314 | 314 | 1/1 |
| 8 | 133 | 26.0 | 1434 | 1435 | 8/8 |
| 16 | 150 | 22.8 | 1932 | 5792 | 16/16 |

