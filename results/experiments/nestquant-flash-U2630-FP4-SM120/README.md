# NestQuant Flash:75/25 jT, U2630, FP4 MLA — completed SM120 experiment

**80/80 scenarios, two repeats each. Not native DGX Spark performance or an official leaderboard entry.**

| Component | Score /100 |
|---|---:|
| Quality |84.011992|
| Calibration |94.805743|
| Reliability |88.546261|
| Token efficiency |100.000000|
| Responsiveness |66.914355|
| **TrueScore** |**87.031973**|

Median turn latency9.888953s. TrueScore weights: quality.55, calibration.25,
reliability.15, efficiency.015, responsiveness.035. Quality is not a pass rate.
Efficiency100 reflects thinking-off output accounting, not minimal token use.

One RTX PRO6000 Blackwell SM12096GiB plus host RAM/SSD, TP1, concurrency1,
host-mapped residual slots. This is a discrete-GPU experiment, not a hardware
simulation establishing Spark compute/storage performance or shared-memory fit.
Flat50 U2630:526 fixed experts selected using shipped salience scores,
2104 floating,8spares. jT block predictions75% +EMA25%,refresh every committed
token,EMA half-life64,hysteresis4. No single-token urgency or jMT.
FP4 E2M1/g16 MLA with FP16 scales,FP8 indexer,KDA unchanged,262144 context,
MTP2 probabilistic,T.7,P.95,thinkingOFF,seeds43/44,35TPS cap,no prefix cache,
eager execution. Throughput-aware asynchronous prefetch:64 pending transitions,
32 demotions maximum. Rejected draft rows do not advance predictor history.

Harness run: predictor-jt75-g1-full80-gpu0-20261010-104043.
Grader bcba2dd, golden gate73/73, preflight passed. Uncapped output policy,
7200s request timeout, all80 scenarios; separate throughput sweep skipped.
The native serving default has no artificial TPS cap.

Runtime changes are published at
[NestQuant948e242](https://github.com/jarrelscy/nestquant/commit/948e24243624d182507d4d0910acd6b8d5599945).
The measured run used c154543 plus predictor tuning overrides;948e242 publishes
those defaults and launcher wiring. See
[HF serving defaults](https://huggingface.co/jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit/blob/main/serving/default.json).

`provisional.json` retains its historical filename but now contains **all80**
completed scenarios, per-repeat scores/latency/efficiency and final aggregates.
Reconstruct with `tools/provisional_score.py` using its aggregate(records)
function. Original transcripts remain on the experiment host; no private data,
prompts or credentials are included here. This replaces the older70-task snapshot.
