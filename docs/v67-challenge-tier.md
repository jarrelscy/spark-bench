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

## Validation cohort

The challenge tier was validated with three repeats per scenario on benchmark
commit `eff5ca0d170b12bf8e69f578d1bff9182339ee27`. All runs passed the 12/12
golden gate and endpoint/tool-parser preflight, and none had a transport error.

| deployment | ChallengeScore | capability | reliability | Pass@K | median latency | output tokens | wall time |
|---|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek V4 Flash 0731, TP2 DSpark K5, 1M | **79.2** | **76.8** | 86.1 | **75%** | 2.36s | 32,606 | **14.6m** |
| GLM-5.2 QuantTrio, TP4 MTP K5, 316K | 75.6 | 68.5 | 80.3 | 65% | 3.29s | 50,342 | 33.9m |
| Inkling Small, TP2 spec off reasoning0, 262K | 69.7 | 52.7 | **97.0** | 65% | **1.73s** | **18,199** | 20.8m |

These are deployment scores, not a weights-only comparison: topology, context,
speculation, and serving engine are part of each qualified contract. Wall time
includes the golden gate and rendered visual grading.

The tier reduced the shared-perfect ceiling from 36/76 scenarios (47%) in the
full v6.6 cohort to 3/20 (15%). Mean per-scenario score spread increased from
0.164 to 0.393, and median spread increased from 0.062 to 0.357.

## Pairwise view

| pair | first wins | second wins | ties | mean score delta |
|---|---:|---:|---:|---:|
| DeepSeek vs GLM | 8 | 5 | 7 | +0.036 DeepSeek |
| DeepSeek vs Inkling | 8 | 5 | 7 | +0.125 DeepSeek |
| GLM vs Inkling | 8 | 3 | 9 | +0.090 GLM |

Single-model scenario wins were DeepSeek 5, GLM 2, and Inkling 1; twelve cases
had a two- or three-model tie. The per-task matrix matters more than that count:

- DeepSeek led dependency-heavy planning, multi-tool completion, and the
  thread-safe counter implementation. It was the best balanced deployment.
- GLM led the merge-stream code case and average race-animation quality, and
  tied DeepSeek on computed composition and phased animation. It was verbose
  and weak on buried-fact retrieval and tool completion.
- Inkling led long-context retrieval and tied for the strongest abstention and
  robustness behavior. It was fast and consistent on short turns, but several
  planning, composition, and code failures were consistently wrong.

Three scenarios remained perfect for all models (`RR-01`, `SAH-02`, `SAH-03`),
while `RR-02` remained identically weak at 0.25. Keep the perfect cases as
compact regression gates; redesign `RR-02` before using it to rank models.

The two rendered cases consumed most wall time, especially for GLM. They should
remain in model-selection runs, while routine regressions can use domain filters
to run the non-visual challenge cases first and schedule rendered validation as
a separate add-on.
