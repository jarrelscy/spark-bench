# Tier 2 — Inference (Qwen3.6-35B-NVFP4-vllm-eugr0706-recipe-mtp3-throughput-20260708-171225)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 237 | 102.0 | 9.8 | 4297 | 512 |
| 8006 | 1202 | 105.3 | 9.5 | 6658 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 97 | 101.4 | 223 | 223 | 1/1 |
| 8 | 312 | 45.4 | 1254 | 1256 | 8/8 |
| 16 | 450 | 33.3 | 2371 | 2435 | 16/16 |

