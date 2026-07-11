# Tier 2 — Inference (Qwen3.6-35B-longctxV4-32768-u0.7-throughput-20260710-165719)

- model `lctx35b` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `mtp3`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 31960 | 5846 | 102.0 | 9.8 | 5467 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 47 | 99.1 | 5827 | 5827 | 1/1 |
| 2 | 55 | 61.4 | 7140 | 11896 | 2/2 |
| 4 | 61 | 34.0 | 19320 | 23887 | 4/4 |

