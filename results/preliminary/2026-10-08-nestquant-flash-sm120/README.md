# Preliminary NestQuant Flash results — SM120, v7 uncapped

**Incomplete run. Not an official leaderboard submission, final TrueScore, or measured DGX Spark performance.**
Snapshot: 2026-10-08T21:56:52.644943+00:00. Run `glm53-flash-nq15-4bit-sm120-single-paced25-20261008-123602`. Earlier interrupted runs are excluded entirely.

## Results so far

- 35/80 scenarios complete; 71/160 trials saved.
- 61/71 completed trials scored exactly 1.0.
- Raw mean across saved trials: **94.61/100**. This is not TrueScore.
- Difficulty-weighted capability on fully completed scenarios: **93.82/100**.
- Difficulty-weighted calibration on fully completed scenarios: **97.74/100**.
- No provisional TrueScore is supplied: the saved transcript artifacts do not contain all latency and token-efficiency data needed to reconstruct it faithfully.

The completed subset is ordered, not a random sample. Later tasks may change results substantially.
Partial scenarios contribute to the raw trial mean but are excluded from component scores.
Content-refusal scenarios are informational and excluded from capability/calibration per v7 rules.
Full marks are not the same as the benchmark's >=0.5 trial-pass threshold.

## Deployment and methodology

- Model: [jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit](https://huggingface.co/jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit).
- Hardware: one RTX PRO 6000 Blackwell 96 GB, SM120, TP1 on a multi-GPU host. This is a local single-Spark configuration simulation; GB10 performance was not measured.
- vLLM `0.1.dev20051+g487ecf187` with the local NestQuant Flash port; FP8 attention/lm_head, FP8 KV, FP8 MTP experts, one probabilistic speculative token, eager mode, prefix caching disabled, 131072-token context.
- All routed experts have 1.5-bit bases; zero permanently fixed upgrades. Published `spark_128K` jT preset: 102 floating upgrades per layer 3–17, 74 per layer 18–44; 3528 active slots plus 8 spare slots. Residual slots are host-mapped over PCIe on this machine.
- Throughput-aware delivery enabled throughout this fresh run, with bounded outstanding replacements; unavailable upgrades fall back to base precision. Predictor desired-pool policy is unchanged.
- Explicit 25 output tok/s pacing ceiling. Real throughput can be lower. This artificially paced SM120 run should not be used for Spark latency or throughput comparisons.
- Temperature 1.0, top_p 0.95, concurrency one, two repeats, native thinking enabled (`--thinking auto`, model template default max effort). This differs from thinking-off comparison cohorts.
- `SPARK_BENCH_SEED_PER_REPEAT=42`; exact seed interpretation follows this grader's code.
- `--uncapped`, full 80-scenario suite. Context still limits generation; 7200-second per-request timeout, built-in runaway guard. No throughput sweep.
- Grader `bcba2dd`, parent upstream `0a2e2af`; golden gate 73/73 and tool-call preflight passed. The local grader patch allows required pthreads while retaining process-creation restrictions; scoring rules are unchanged. That patch is included in this branch for review.

## Artifacts

[`snapshot.json`](snapshot.json) contains each saved trial's score and grading reason,
plus source-transcript SHA256 digests. Conversation/tool traces remain local; this
snapshot does not upload prompts, generated code, tokens, activations, credentials,
or private calibration data. Source files can be matched to digests for later audit.

The 0.0691 KLD, 67.1% activation coverage and 81.8% salience coverage are prior
held-out harness references, not reproduced measurements in this benchmark. The
live salience counter has been implemented but is not enabled in this run.

## Completed and partial scenario scores

| Scenario | Repeat 1 | Repeat 2 | Mean |
|---|---:|---:|---:|
| AG-01 | 1.0000 | 0.4900 | 0.7450 |
| AG-02 | 0.4900 | 0.4900 | 0.4900 |
| AG-03 | 1.0000 | 1.0000 | 1.0000 |
| IF-01 | 1.0000 | 1.0000 | 1.0000 |
| AG-04 | 1.0000 | 1.0000 | 1.0000 |
| IF-03 | 1.0000 | 1.0000 | 1.0000 |
| IF-04 | 1.0000 | 0.0000 | 0.5000 |
| AG-05 | 1.0000 | 1.0000 | 1.0000 |
| AG-06 | 1.0000 | 1.0000 | 1.0000 |
| SO-02 | 1.0000 | 1.0000 | 1.0000 |
| LC-03 | 1.0000 | 1.0000 | 1.0000 |
| CODE-01 | 1.0000 | 1.0000 | 1.0000 |
| CODE-02 | 1.0000 | 1.0000 | 1.0000 |
| CODE-03 | 1.0000 | 1.0000 | 1.0000 |
| CODE-04 | 1.0000 | 1.0000 | 1.0000 |
| CODE-05 | 1.0000 | 1.0000 | 1.0000 |
| SA-01 | 1.0000 | 1.0000 | 1.0000 |
| SA-02 | 1.0000 | 1.0000 | 1.0000 |
| SA-03 | 1.0000 | 0.6667 | 0.8333 |
| SA-04 | 1.0000 | 1.0000 | 1.0000 |
| RO-01 | 1.0000 | 0.5000 | 0.7500 |
| RO-02 | 1.0000 | 1.0000 | 1.0000 |
| RO-03 | 1.0000 | 1.0000 | 1.0000 |
| RO-04 | 1.0000 | 1.0000 | 1.0000 |
| IFH-01 | 1.0000 | 1.0000 | 1.0000 |
| IFH-02 | 1.0000 | 1.0000 | 1.0000 |
| LCH-01 | 1.0000 | 1.0000 | 1.0000 |
| SOH-01 | 1.0000 | 1.0000 | 1.0000 |
| VIS-01 | 1.0000 | 1.0000 | 1.0000 |
| VIS-02 | 0.8333 | 1.0000 | 0.9167 |
| TUH-05 | 1.0000 | 1.0000 | 1.0000 |
| SAH-01 | 1.0000 | 1.0000 | 1.0000 |
| IFH-03 | 1.0000 | 1.0000 | 1.0000 |
| SOH-02 | 1.0000 | 1.0000 | 1.0000 |
| VIS-03 | 0.9583 | 0.9167 | 0.9375 |
| VIS-04 | 0.8300 | Pending | Pending |
