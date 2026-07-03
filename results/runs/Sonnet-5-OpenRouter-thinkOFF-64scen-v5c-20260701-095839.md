# Deep Eval (Sonnet-5-OpenRouter-thinkOFF-64scen-v5c-20260701-095839)

- model `anthropic/claude-sonnet-5` @ `https://openrouter.ai/api/v1`  thinking `off` repeats `2` temp `0.3`

## TrueScore 15.5/100  —  ⭐ Weak (grade F)

| headline score | value | meaning |
|----------------|------:|---------|
| Capability Score | 0.0 | quality/correctness without speed penalty |
| Operational Score | 10.0 | efficiency + latency/responsiveness |
| **TrueScore** | **15.5** | combined deployment score |

| component | score | TrueScore weight |
|-----------|------:|-----------------:|
| quality | 0.0 | 55% |
| calibration | 0.0 | 25% |
| reliability | 100.0 | 15% |
| efficiency | 0.0 | 2% |
| responsiveness | 14.3 | 4% |

Median turn latency 120.00s · 64 scenarios · thinking off

## Trial Statistics

| metric | value | meaning |
|--------|------:|---------|
| Pass@1 | 0.0% | scenarios passing (≥50%) on at least 1 repeat |
| Pass@K | 0.0% | scenarios passing on ALL repeats |
| Reliability Gap | 0.0% | Pass@1 − Pass@K (flakiness cost) |
| Score StdDev | 0.0 | cross-scenario score spread |
| Scenario StdDev | 0.0 | mean per-scenario repeat variance |

## Domain breakdown

| domain | group | n | quality | reliability |
|--------|-------|--:|--------:|------------:|
| robustness | calibration | 4 | 0.0 | 100.0 |
| agentic | capability | 6 | 0.0 | 100.0 |
| classification | capability | 1 | 0.0 | 100.0 |
| code | capability | 10 | 0.0 | 100.0 |
| composition | capability | 2 | 0.0 | 100.0 |
| instruction | capability | 9 | 0.0 | 100.0 |
| long_context | capability | 2 | 0.0 | 100.0 |
| planning | capability | 5 | 0.0 | 100.0 |
| structured | capability | 5 | 0.0 | 100.0 |
| tool_use | capability | 6 | 0.0 | 100.0 |
| visual | capability | 3 | 0.0 | 100.0 |
| safety | informational | 11 | 0.0 | 100.0 |

## Per-scenario

| id | domain | tier | score | cons | latency | reason |
|----|--------|------|------:|-----:|--------:|--------|
| AG-01 | agentic | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AG-02 | agentic | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AG-03 | agentic | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IF-01 | instruction | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AG-04 | agentic | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IF-03 | instruction | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IF-04 | instruction | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AG-05 | agentic | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AG-06 | agentic | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SO-02 | structured | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| LC-03 | long_context | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-01 | code | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-02 | code | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-03 | code | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-04 | code | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-05 | code | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SA-01 | safety | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SA-02 | safety | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SA-03 | safety | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SA-04 | safety | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RO-01 | robustness | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RO-02 | robustness | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RO-03 | robustness | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RO-04 | robustness | base | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IFH-01 | instruction | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IFH-02 | instruction | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| LCH-01 | long_context | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SOH-01 | structured | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| VIS-01 | visual | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| VIS-02 | visual | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| TUH-05 | tool_use | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SAH-01 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IFH-03 | instruction | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SOH-02 | structured | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| VIS-03 | visual | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| PL-01 | planning | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| PL-02 | planning | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| PL-03 | planning | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CP-01 | composition | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CP-02 | composition | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SOH-03 | structured | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SOH-04 | structured | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SAH-02 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| SAH-03 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| TUH-08 | tool_use | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| TUH-10 | tool_use | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CL-01 | classification | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| MSC-01 | tool_use | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| MSC-02 | tool_use | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| MSC-03 | tool_use | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RR-01 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RR-02 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RR-03 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| RR-04 | safety | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AP-01 | planning | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| AP-02 | planning | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IFS-01 | instruction | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IFS-02 | instruction | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| IFS-03 | instruction | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-06 | code | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-07 | code | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-08 | code | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-09 | code | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |
| CODE-10 | code | hard | 0.00 | 1.00 | 120.0s | error: HTTPError: HTTP Error 401: Unauthorized |

## Serving Throughput Sweep

Automatic v5c add-on: single-stream decode at multiple prompt contexts plus aggregate throughput under concurrent requests. These rows are stored as `tier2` metrics under the same run id as the deep eval.

### Serving throughput detail

- model `anthropic/claude-sonnet-5` @ `https://openrouter.ai/api/v1`  topology `unknown` parallelism `1` spec_decode `na`

#### Single-stream decode

| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |
|--------:|----------:|-------------:|----------:|--------------:|---------:|
| 1024 | ERR | - | - | - | - |
| 8192 | ERR | - | - | - | - |
| 32768 | ERR | - | - | - | - |

#### Throughput under concurrency

| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | TTFT p99 (ms) | completed |
|------:|-----------------:|-----------------:|--------------:|--------------:|----------:|
| 1 | ERR | - | - | - | 0 |
| 2 | ERR | - | - | - | 0 |
| 4 | ERR | - | - | - | 0 |
| 8 | ERR | - | - | - | 0 |

