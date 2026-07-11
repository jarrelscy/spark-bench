# Tier 2 — Inference (SS-ngram-noasync-throughput-20260709-172619)

- model `qwen36-35b-nvfp4` @ `http://10.0.0.183:8891/v1`  topology `single` parallelism `1` spec_decode `ngram4`

## Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1017 | 195 | 70.4 | 14.2 | 5224 | 512 |
| 8006 | 1639 | 68.6 | 14.6 | 4885 | 512 |

## Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | 69 | 70.7 | 180 | 180 | 1/1 |

