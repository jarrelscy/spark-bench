# Deep Eval (spark-native-thinking-tail-recovery-agentic-resume-20261015-011245)

- model `glm-5.3-flash-nq` @ `http://127.0.0.1:18976/v1`  thinking `on` repeats `2` temp `0.7` request policy `uncapped` timeout `7200`

- grader `f2ac787` · golden gate golden gate PASSED: 73/73 cases · preflight passed

## TrueScore 85.3/100  —  ⭐⭐⭐⭐ Strong (grade B)

| headline score | value | meaning |
|----------------|------:|---------|
| Capability Score | 89.7 | quality/correctness without speed penalty |
| Operational Score | 34.1 | efficiency + latency/responsiveness |
| **TrueScore** | **85.3** | combined deployment score |

| component | score | TrueScore weight |
|-----------|------:|-----------------:|
| quality | 89.7 | 73% |
| calibration | n/a | — |
| reliability | 86.1 | 20% |
| efficiency | 100.0 | 2% |
| responsiveness | 5.9 | 5% |

Median turn latency 317.59s · 6 scenarios · thinking on

## Trial Statistics

| metric | value | meaning |
|--------|------:|---------|
| Methodology | v7.0-full-subset-uncapped | scenario and grader contract |
| Run Valid | yes | transport error rate 0.0% |
| Pass@1 | 100.0% | scenarios passing (≥50%) on at least 1 repeat |
| Pass@K | 83.3% | scenarios passing on ALL repeats |
| Reliability Gap | 16.7% | Pass@1 − Pass@K (flakiness cost) |
| Score StdDev | 0.16 | cross-scenario score spread |
| Scenario StdDev | 0.069 | mean per-scenario repeat variance |

## Domain breakdown

| domain | group | n | quality | reliability |
|--------|-------|--:|--------:|------------:|
| agentic | capability | 6 | 89.7 | 86.1 |

## Per-scenario

| id | domain | tier | score | cons | latency | reason |
|----|--------|------|------:|-----:|--------:|--------|
| AG-07 | agentic | expert | 1.00 | 1.00 | 192.4s | agentic 9/9: ✓ all 4 cities' weather checked, ✓ events for t |
| AG-08 | agentic | expert | 1.00 | 1.00 | 257.0s | agentic 7/7: ✓ calendar retried after failure, ✓ incident re |
| AG-09 | agentic | expert | 0.83 | 1.00 | 78.3s | agentic 5/6: ✓ query with properly NESTED date_range, ✓ over |
| AG-10 | agentic | expert | 0.58 | 0.17 | 413.0s | agentic 6/6: stateful exact_events=pass, exact_emails=pass,  |
| AG-11 | agentic | expert | 1.00 | 1.00 | 378.2s | agentic 6/6: stateful exact_events=pass, exact_emails=pass,  |
| AG-12 | agentic | expert | 1.00 | 1.00 | 449.5s | agentic 6/6: stateful exact_events=pass, exact_emails=pass,  |

## Serving Throughput Sweep

Skipped by `--skip-throughput`.

