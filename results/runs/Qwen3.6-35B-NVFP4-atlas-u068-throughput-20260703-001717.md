# Tier 2 — Inference (Qwen3.6-35B-NVFP4-atlas-u068-throughput-20260703-001717)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8890/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 463 | 85.3 | 11.7 | 2197 | 934 |
| 8006 | 2978 | 61.5 | 16.3 | 2688 | 852 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 82 | 85.3 | 459 | 459 | 1/1 |
| 8 | 98 | 13.0 | 3563 | 3565 | 8/8 |
| 16 | 100 | 6.6 | 7090 | 7094 | 16/16 |

