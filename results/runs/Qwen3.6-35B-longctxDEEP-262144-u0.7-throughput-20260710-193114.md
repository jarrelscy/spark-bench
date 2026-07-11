# Tier 2 — Inference (Qwen3.6-35B-longctxDEEP-262144-u0.7-throughput-20260710-193114)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 251548 | 134921 | 72.0 | 13.9 | 1864 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 4 | 63.5 | 134642 | 134642 | 1/1 |
| 2 | 4 | 24.4 | 136414 | 270718 | 2/2 |
| 4 | 4 | 9.8 | 408986 | 543077 | 4/4 |
| 8 | 3 | 1.9 | 408973 | 820952 | 6/8 |
| 16 | 3 | 1.8 | 409047 | 820326 | 6/16 |

