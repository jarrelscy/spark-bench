# Canonical NestQuant single-Spark result

**TrueScore 89.21513 · quality 94.18840 · 80 tasks × 2 repeats · thinking on · validity PASS · zero transport errors.**

This run evaluated `GLM-5.3-Flash-NestQuant-1.5-4bit` on one native ARM64 DGX Spark GB10 with MTP2, uncapped generation, temperature 0.7, top-p 0.95, and repeat seeds 43/44. It used Spark Bench v7.0 and official grader commit `f2ac7876c1782047fe4ac37290a1466daa3a1c05`.

| Metric | Result |
|---|---:|
| TrueScore | **89.21513** |
| Quality | **94.18840** |
| Calibration | **87.88007** |
| Reliability | **93.68070** |
| Efficiency | **41.98068** |
| Responsiveness | **21.70526** |
| Completed | **160/160** |
| Transport errors | **0%** |

[All 160 response transcripts](transcripts) · [Full scorer record](recovered-full-score.json) · [SHA-256 manifest](SHA256SUMS.json) · [Docker serving recipe](https://github.com/jarrelscy/nestquant/tree/spark-flash/spark/flash/sampled_ahead_sentinel) · [Hugging Face model](https://huggingface.co/jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit)

## Tested configuration

| Setting | Value |
|---|---|
| Predictor | 75% jT / 25% EMA, updated every committed token, G=1 |
| Expert slots | 2,630 active: 526 fixed (20%) + 2,104 floating; 8 spares |
| Allocation | U050 / `spark_256K_U_2630_flat50` |
| EMA / hysteresis | Half-life 64 / 4 |
| Speculative decoding | MTP2 probabilistic |
| Context / KV | 262,144 tokens / 2 GiB |
| Sampling | Temperature 0.7, top-p 0.95, thinking on |
| Serving | TP1, one sequence, native uncapped |
| Docker image | `docker.io/jarrelscy/nestquant@sha256:3859a4e0018ec915ca0d4a3f9488158026fc2525534051433e2b37a729102364` (`linux/arm64`) |

The nominal capacity-weighted routed-expert precision is 2.0436 bpw, excluding metadata, backbone, and KV cache. The separately measured four-window asynchronous decode KLD is 0.09006744. That KLD test and this benchmark measure different things.

## Recovery provenance

The initial pass produced all 160 files but 15 late files contained transport-error placeholders. The model service was not OOM-killed. Those exact scenario/repeat slots were rerun under the unchanged configuration using Spark Bench's `--scenario-ids` and `--repeat-indices` selectors. The official per-task scores from those 15 runs replaced only the placeholders; the official v7.0 aggregation was then applied to all 80 scenarios and 160 valid repeats.

`recovered-full-score.json` records the scorer source, grader revision, final components, and a per-transcript source/hash manifest. `SHA256SUMS.json` hashes everything in this publication directory. The recovery reports are included under `recovery-reports/`.

## Reproduce

Start the pinned ARM64 image with the [published single-Spark recipe](https://github.com/jarrelscy/nestquant/tree/spark-flash/spark/flash/sampled_ahead_sentinel). Run Spark Bench commit `f2ac7876c1782047fe4ac37290a1466daa3a1c05` from a separate scorer machine through an authenticated SSH tunnel:

```bash
export SPARK_BENCH_FORCE_TEMPERATURE=0.7
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"chat_template_kwargs":{"enable_thinking":true}}'
export SPARK_BENCH_CONTEXT=262144
export SPARK_BENCH_SEED_PER_REPEAT=42
unset SPARK_BENCH_REASONING_EFFORT
python -u spark_bench.py eval \
  --endpoint http://127.0.0.1:18975/v1 \
  --model glm-5.3-flash-nq \
  --label spark-native-full80-sampled-ahead-thinking \
  --topology single-dgx-spark-gb10 --parallelism TP1 \
  --spec-decode mtp2-probabilistic --repeats 2 \
  --temperature 0.7 --thinking on --uncapped --tier all \
  --skip-throughput --timeout 7200 --out-dir results
```

The result is an observed benchmark outcome, not a guarantee that stochastic reruns will produce the same score.
