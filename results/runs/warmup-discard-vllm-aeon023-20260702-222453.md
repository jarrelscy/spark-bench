# Tier 2 — Inference (warmup-discard-vllm-aeon023-20260702-222453)

- model `qwen36-35b-fp8` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 308 | 54.1 | 18.8 | 3307 | 64 |
| 8006 | 1720 | 52.6 | 19.3 | 4655 | 64 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 45 | 54.2 | 248 | 248 | 1/1 |
| 8 | 127 | 23.5 | 1430 | 1630 | 8/8 |
| 16 | 174 | 16.5 | 1927 | 2853 | 16/16 |

