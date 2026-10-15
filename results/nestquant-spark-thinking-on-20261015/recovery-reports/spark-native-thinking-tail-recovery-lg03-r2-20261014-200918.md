# Deep Eval (spark-native-thinking-tail-recovery-lg03-r2-20261014-200918)

- model `glm-5.3-flash-nq` @ `http://127.0.0.1:18976/v1`  thinking `on` repeats `2` temp `0.7` request policy `uncapped` timeout `7200`

- grader `f2ac787` · golden gate golden gate PASSED: 73/73 cases · preflight passed

## TrueScore 86.1/100  —  ⭐⭐⭐⭐ Strong (grade B)

| headline score | value | meaning |
|----------------|------:|---------|
| Capability Score | 90.0 | quality/correctness without speed penalty |
| Operational Score | 2.2 | efficiency + latency/responsiveness |
| **TrueScore** | **86.1** | combined deployment score |

| component | score | TrueScore weight |
|-----------|------:|-----------------:|
| quality | 90.0 | 73% |
| calibration | n/a | — |
| reliability | 100.0 | 20% |
| efficiency | 6.7 | 2% |
| responsiveness | 0.2 | 5% |

Median turn latency 8381.08s · 1 scenarios · thinking on

## Trial Statistics

| metric | value | meaning |
|--------|------:|---------|
| Methodology | v7.0-full-subset-uncapped | scenario and grader contract |
| Run Valid | yes | transport error rate 0.0% |
| Pass@1 | 100.0% | scenarios passing (≥50%) on at least 1 repeat |
| Pass@K | 100.0% | scenarios passing on ALL repeats |
| Reliability Gap | 0.0% | Pass@1 − Pass@K (flakiness cost) |
| Score StdDev | 0.0 | cross-scenario score spread |
| Scenario StdDev | 0.0 | mean per-scenario repeat variance |

## Domain breakdown

| domain | group | n | quality | reliability |
|--------|-------|--:|--------:|------------:|
| long_gen | capability | 1 | 90.0 | 100.0 |

## Per-scenario

| id | domain | tier | score | cons | latency | reason |
|----|--------|------|------:|-----:|--------:|--------|
| LG-03 | long_gen | hard | 0.90 | 1.00 | 8381.1s | 9/10 groups; tests 39/40; broken: graph_scale | test_perform |

## Saved artifacts (open / post these)

- `LG-03` (long_gen, score 0.90): `/home/jarrelscy/enverge-spark-watch/full80-sampled-ahead-thinking/recovery-results/artifacts/spark-native-thinking-tail-recovery-lg03-r2-20261014-200918/LG-03.md`

## Serving Throughput Sweep

Skipped by `--skip-throughput`.

