# Tier 2 — Inference (Qwen3.6-35B-NVFP4-vllm-eugr0706-parity-throughput-20260708-170657)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `na`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 201 | 78.0 | 12.8 | 5072 | 512 |
| 8006 | 1218 | 74.3 | 13.5 | 6571 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 76 | 77.8 | 181 | 181 | 1/1 |
| 8 | 275 | 36.7 | 908 | 1266 | 8/8 |
| 16 | 357 | 24.1 | 1516 | 2736 | 16/16 |

