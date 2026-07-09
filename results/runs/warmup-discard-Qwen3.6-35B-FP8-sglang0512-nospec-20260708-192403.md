# Tier 2 — Inference (warmup-discard-Qwen3.6-35B-FP8-sglang0512-nospec-20260708-192403)

- model `qwen` @ `http://10.0.0.183:8899/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 880 | 52.0 | 19.5 | 1156 | 64 |
| 8006 | 1778 | 49.7 | 20.4 | 4502 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 41 | 51.6 | 312 | 312 | 1/1 |
| 8 | 181 | 38.6 | 1333 | 1335 | 8/8 |
| 16 | 155 | 25.8 | 2641 | 5349 | 16/16 |

