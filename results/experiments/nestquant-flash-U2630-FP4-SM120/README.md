# NestQuant Flash U2630 + FP4 — provisional SM120 experiment

**Not a native DGX Spark result, not a completed leaderboard submission.**
Snapshot: 70/80 scenarios completed, two repeats, 2026-10-09.

| Component | Score /100 |
|---|---:|
| Quality / capability |84.4332|
| Calibration |89.1329|
| Reliability |90.6525|
| Token efficiency |100.0000|
| Responsiveness |76.2517|
| Provisional TrueScore |86.4882|

Only scenarios with both repeats enter the aggregate. Quality is not a task pass
percentage. Token efficiency is the harness answer-versus-reasoning metric;
100% with thinking off does not mean minimal output or universally correct answers.
Remaining tasks can change every component. Do not compare this partial subset
against another model's full80 score as a controlled ranking.

Model: jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit. Hardware: one RTX PRO6000
Blackwell SM12096GiB plus host RAM and SSD; hot residual slots are host-mapped
across PCIe. This approximates a memory budget, not Spark compute/memory/storage.
TP1, concurrency1, U2630 active floating slots,0 fixed,8 spares. E2M1/g16 FP4 MLA
cache with FP16 scales, FP8 indexer, unchanged KDA;262144 max context.
MTP2 probabilistic, temperature0.7, top_p0.95, thinking-off template,35tok/s cap,
async throughput-aware prefetch with64 transitions/32 demotions maximum.
No prefix caching or CUDA graphs. Seeds43/44; timeout7200s; uncapped response
policy. Grader base bcba2dd permits required pthreads while denying process
creation; scoring unchanged. No native Spark latency claim.

This run started from feature revision e2e90e9 plus the U2630 allocation, now
published in [NestQuant8d15c80](https://github.com/jarrelscy/nestquant/commit/8d15c80).
The native serving default is now uncapped; that differs from this benchmark.
See [HF serving default](https://huggingface.co/jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit/blob/main/serving/default.json)
and the [Spark monitoring guide](https://huggingface.co/jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit/blob/main/serving/SPARK_MONITORING.md).

`provisional.json` contains per-repeat scores, latency and efficiency inputs
plus the aggregate. No prompts, private calibration data, tokens or credentials
are included. Full transcripts are retained on the experiment host, not uploaded
with this snapshot. Reproduce the aggregate with `tools/provisional_score.py`'s
`aggregate(records)` function. The previous thinking-on run is not included.

Observed cumulative decode coverage was about54% hot activations and72–73%
salience. Desired salience was about73–74%. These are observations, not quality
guarantees. U's causal benefit has not been isolated from temperature/KV changes.
