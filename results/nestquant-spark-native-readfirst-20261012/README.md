# Native single-Spark NestQuant full80 result

Completed 2026-10-12 on one DGX Spark GB10: 80 scenarios, two repeats (160 total), official run valid PASS, zero errors. Official rounded TrueScore **87.5**, quality **85.4**. Local SM120 reference: TrueScore 87.03197, quality 84.01199; that reference used a 35-token/s cap and different hardware.

The `official/` directory contains the scorer CSV, reports, generated artifacts and complete per-repeat transcripts. Routing telemetry and coverage summaries are alongside it. These are benchmark fixture conversations, not production chats. `manifest.json` records SHA-256 hashes of the original evidence files.

Serving source: jarrelscy/nestquant commit `d185808c108681d6f2995b2353679d44d3c5f0ca`, tag `spark-readfirst-full80-20261012`. Benchmark source: `f2ac7876c1782047fe4ac37290a1466daa3a1c05` from Weschera/spark-bench. Later experimental publication/admission candidates are excluded.

Configuration: U050-F20-jT75-G1; 2630 active expert slots (526 fixed, 2104 floating), eight spares, jT75/EMA25 refreshed every committed token, native uncapped pacing, MTP2 probabilistic, FP4-g16 MLA, FP8 KV, context262144, explicit KV2GiB, one sequence, eager, no prefix cache, temperature0.7/top_p0.95, thinking off. Preserve the supplied host-memory guard. Startup memory pressure can stop a launch even though this completed soak passed; do not disable the guard.

## Reproduce scoring

Run the official scorer on a separate machine to avoid competing with Spark unified memory. Establish your own SSH tunnel to the authenticated serving port. Set `SPARK_BENCH_API_KEY` privately to the serving key. Install the dependencies from the pinned benchmark checkout.

```bash
export SPARK_BENCH_FORCE_TEMPERATURE=0.7
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"chat_template_kwargs":{"enable_thinking":false}}'
export SPARK_BENCH_CONTEXT=262144
export SPARK_BENCH_SEED_PER_REPEAT=42
unset SPARK_BENCH_REASONING_EFFORT
python -u spark_bench.py eval --endpoint http://127.0.0.1:18975/v1 \
  --model glm-5.3-flash-nq --label spark-native-full80-readfirst \
  --topology single-dgx-spark-gb10 --parallelism TP1 \
  --spec-decode mtp2-probabilistic --repeats 2 --temperature 0.7 \
  --thinking off --uncapped --tier all --skip-throughput \
  --timeout 7200 --out-dir results
```

This selects all80 scenarios and repeat seeds43/44. GPU inference and asynchronous delivery can produce different trajectories despite matched settings. Latencies include the SSH tunnel. The dedicated throughput sweep was skipped: median positive serving-log generation interval was17.2tokens/s, maximum22.2tokens/s; these are not isolated decode-kernel throughput measurements.

Coverage comparisons use approximate periodic telemetry boundaries and different generated trajectories. See the saved summaries rather than treating every selected expert as delivered hot.

## Published serving recipe

The validated ARM64 runtime is published as `docker.io/jarrelscy/nestquant:spark-flash-jt75-g1-20261011`, pinned by digest:

```
docker.io/jarrelscy/nestquant@sha256:3859a4e0018ec915ca0d4a3f9488158026fc2525534051433e2b37a729102364
```

[Complete checkpoint preparation, guarded startup and benchmark instructions](https://github.com/jarrelscy/nestquant/blob/7cd890e/spark/flash/README.md). The portable launcher is tagged `spark-readfirst-recipe-20261012-v2`; the original measured runtime source remains tagged `spark-readfirst-full80-20261012`. The image excludes model weights and benchmark traces. Prepare weights using the pinned checkpoint and documented commands.
