# v6.7 Challenge Tier

The v6.7 challenge tier is a 20-scenario diagnostic view selected from the
first controlled three-model v6.6 cohort. It is meant to expose model profile
differences that the nearly tied full-suite scores conceal. It does not replace
the 76-scenario v6.6 suite or its shared regression gates.

## Source cohort

All three runs used benchmark commit `e6d1f462cfba7b122d713cd349a7cc95098fc4ba`,
three repeats, temperature 0.3, thinking off, and the browser golden gate.

| model | run id | TrueScore | capability | operational | median latency |
|---|---|---:|---:|---:|---:|
| GLM-5.2 QuantTrio NVFP4, vLLM TP4 MTP K5 | `GLM-5.2-QuantTrio-NVFP4-vLLM-TP4-MTPK5-4Spark-316K-thinkOFF-76scen-v6.6-r3-20260801-000001` | 90.3 | 91.5 | 87.9 | 4.17s |
| Inkling Small NVFP4, vLLM TP2 spec off reasoning0 | `Inkling-Small-NVFP4-vLLM-TP2-specOFF-reasoning0-2Spark-262K-76scen-v6.6-r3-20260801-012952` | 89.0 | 86.6 | 88.8 | 3.80s |
| DeepSeek V4 Flash 0731 NVFP4, vLLM TP2 DSpark K5 | `DeepSeek-V4-Flash-0731-NVFP4-vLLM-TP2-DSparkK5-2Spark-1M-thinkOFF-76scen-v6.6-r3-20260801-023054` | 90.6 | 92.7 | 93.0 | 2.22s |

Thirty-six of 76 scenarios scored 1.0 for every model. Those cases are useful
regression gates, but they provide no ranking information in this cohort.

## Selection rule

The challenge manifest contains scenarios that separated at least two models,
prioritizing score spread and coverage of distinct failure modes. It spans ten
domains and preserves the two rendered visual checks. Scenario prompts and
graders are unchanged from v6.6.

`AG-07, AP-01, CODE-12, CODE-13, CODE-14, CP-02, IFH-02, LCH-01, MSC-02,
PL-02, RO-01, RO-03, RR-01, RR-02, RR-04, SAH-02, SAH-03, TUH-10, VIS-04,
VIS-05`

Run it with:

```bash
python3 spark_bench.py eval \
  --tier challenge \
  --repeats 3 \
  --temperature 0.3 \
  --thinking off \
  --skip-throughput
```

Challenge runs stamp methodology `v6.7-challenge`. Their scores are comparable
to other challenge runs using the same contract, not to full-suite v6.6 scores.
The full suite remains the correctness and regression qualification gate.

## Interpretation

Use the challenge aggregate as a compact first view, then inspect pairwise wins,
per-scenario repeat variance, and domain profiles. A model can tie on the full
suite while failing very different workloads. The source cohort showed GLM
strongest in code and composition, Inkling strongest in long-context retrieval
and visual work, and DeepSeek strongest as a balanced planning and agentic model.

This tier is intentionally cohort-derived, so it is diagnostic rather than a
fresh holdout. A future challenge revision should add new variants with buried
distractors, stateful recovery, cross-document synthesis, and temporal rendered
assertions before it is used as a public model-ranking claim.
