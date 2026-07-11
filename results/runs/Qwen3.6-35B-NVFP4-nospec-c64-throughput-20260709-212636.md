# Tier 2 — Inference (Qwen3.6-35B-NVFP4-nospec-c64-throughput-20260709-212636)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 197 | 78.8 | 12.7 | 5172 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 77 | 78.7 | 182 | 182 | 1/1 |
| 16 | 377 | 25.8 | 1644 | 2173 | 16/16 |
| 64 | 2 | 0.0 | 4906 | 8799 | 64/64 |

