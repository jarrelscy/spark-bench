# Deep Eval (Grok-4.5-effort-low-SMOKE-code-v6.4c-OpenRouter-20260710-154818)

- model `x-ai/grok-4.5` @ `https://openrouter.ai/api/v1`  thinking `auto` repeats `1` temp `0.3`

- grader `d340b6e` · golden gate golden gate PASSED: 8/8 cases · preflight passed

## TrueScore 82.6/100  —  ⭐⭐⭐⭐ Strong (grade B)

| headline score | value | meaning |
|----------------|------:|---------|
| Capability Score | 79.0 | quality/correctness without speed penalty |
| Operational Score | 69.6 | efficiency + latency/responsiveness |
| **TrueScore** | **82.6** | combined deployment score |

| component | score | TrueScore weight |
|-----------|------:|-----------------:|
| quality | 79.0 | 73% |
| calibration | n/a | — |
| reliability | 100.0 | 20% |
| efficiency | 61.8 | 2% |
| responsiveness | 72.9 | 5% |

Median turn latency 7.43s · 14 scenarios · thinking auto

## Trial Statistics

| metric | value | meaning |
|--------|------:|---------|
| Pass@1 | 85.7% | scenarios passing (≥50%) on at least 1 repeat |
| Pass@K | 85.7% | scenarios passing on ALL repeats |
| Reliability Gap | 0.0% | Pass@1 − Pass@K (flakiness cost) |
| Score StdDev | 0.3 | cross-scenario score spread |
| Scenario StdDev | 0.0 | mean per-scenario repeat variance |

## Domain breakdown

| domain | group | n | quality | reliability |
|--------|-------|--:|--------:|------------:|
| code | capability | 14 | 79.0 | 100.0 |

## Per-scenario

| id | domain | tier | score | cons | latency | reason |
|----|--------|------|------:|-----:|--------:|--------|
| CODE-01 | code | base | 0.80 | 1.00 | 4.4s | 4/5 tests: t1:pass, t2:pass, t3:pass, t4:pass, t5:fail(007 s |
| CODE-02 | code | base | 0.50 | 1.00 | 7.0s | 2/4 checks passed: returns 2 rows (Alice=200, Bob=50):fail,  |
| CODE-03 | code | base | 1.00 | 1.00 | 4.1s | 4/4 tests: t1:pass, t2:pass, t3:pass, t4:pass |
| CODE-04 | code | base | 1.00 | 1.00 | 8.5s | 5/5 tests: t1:pass, t2:pass, t3:pass, t4:pass, t5:pass |
| CODE-05 | code | base | 1.00 | 1.00 | 16.4s | 5/5 tests: t1:pass, t2:pass, t3:pass, t4:pass, t5:pass |
| CODE-06 | code | hard | 1.00 | 1.00 | 10.5s | 4/4 tests: t1:pass, t2:pass, t3:pass, t4:pass |
| CODE-07 | code | hard | 1.00 | 1.00 | 2.6s | all tests passed |
| CODE-08 | code | hard | 1.00 | 1.00 | 3.0s | 3/3 checks passed: returns 6 rows:pass, has window function  |
| CODE-09 | code | hard | 1.00 | 1.00 | 12.7s | 3/3 tests: t1:pass, t2:pass, t3:pass |
| CODE-10 | code | hard | 1.00 | 1.00 | 2.0s | 4/4 tests: t1:pass, t2:pass, t3:pass, t4:pass |
| CODE-11 | code | hard | 1.00 | 1.00 | 5.5s | 5/5 tests: t1:pass, t2:pass, t3:pass, t4:pass, t5:pass |
| CODE-12 | code | hard | 0.75 | 1.00 | 33.7s | 3/4 tests: t1:pass, t2:error(can't start new thread), t3:pas |
| CODE-13 | code | hard | 0.40 | 1.00 | 7.9s | 2/5 tests: t1:pass, t2:pass, t3:skip(no source), t4:skip(no  |
| CODE-14 | code | hard | 0.00 | 1.00 | 22.3s | 0/5 tests: t1:error(merge_sorted_streams() takes 1 positiona |

## Serving Throughput Sweep

Skipped by `--skip-throughput`.

