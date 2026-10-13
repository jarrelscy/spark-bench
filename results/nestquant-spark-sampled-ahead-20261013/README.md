# Canonical NestQuant single-Spark result

**TrueScore 86.68697 · quality 84.36596 · 80 tasks × 2 repeats · run validity PASS · 0 transport errors.**

GLM-5.3-Flash-NestQuant-1.5-4bit on one native ARM64 DGX Spark GB10, thinking off, MTP2, uncapped, temperature0.7/top_p0.95, seeds43/44. Official grader commit `f2ac7876c1782047fe4ac37290a1466daa3a1c05`; runtime commit `9adf4beb0a503fe15218fb575760782c574f201e`.

[Official report](runs/spark-native-full80-sampled-ahead-20261013-093617.md) · [CSV](spark_bench.csv) · [160 response transcripts](artifacts/spark-native-full80-sampled-ahead-20261013-093617/transcripts) · [Docker serving recipe](https://github.com/jarrelscy/nestquant/tree/spark-flash/spark/flash/sampled_ahead_sentinel) · [HF model](https://huggingface.co/jarrelscy/GLM-5.3-Flash-NestQuant-1.5-4bit).

2630 active slots (526 fixed +2104 floating),8spares;75%jT/25%EMA,G1;2GiBKV,262144context. Nominal capacity-weighted routed-expert precision is2.0436bpw, excluding metadata/backbone/KV. Separate four-window decode KLD is0.09006744. The21.25TPS synthetic probe is not benchmark throughput.

CODE-13 repeat2 generated257644tokens and ended at the length limit, receiving0 under the official scorer. The final score includes this failure. Thinking-on is a separate ongoing run and has no final result here.

This is the canonical fork result. Reports and response transcripts are included; the large runtime routing trace is still being archived and is not included in this Git package. `SHA256SUMS.json` hashes the original result artifacts. No upstream leaderboard endorsement is claimed.
