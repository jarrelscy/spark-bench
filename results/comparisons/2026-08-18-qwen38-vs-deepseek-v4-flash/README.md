# Qwen3.8-27B vs DeepSeek-V4-Flash-0731

Audited on 2026-08-18 with SparkBench v6.7.1. Each deployment ran the same
76 scenarios three times at temperature 0.2 and top-p 0.95 with thinking
disabled.

## Result

| Metric | Qwen3.8-27B | DeepSeek-V4-Flash | Winner |
|---|---:|---:|---|
| Corrected TrueScore | 90.94 | 93.01 | DeepSeek |
| Capability / quality | 87.59 | 93.38 | DeepSeek |
| Calibration | 97.31 | 91.62 | Qwen |
| Reliability | 93.90 | 93.96 | Tie |
| Median turn latency | 4.53 s | 2.20 s | DeepSeek |
| Total output tokens | 136,711 | 88,118 | DeepSeek was less verbose |

## Domain quality

| Domain | Qwen3.8-27B | DeepSeek-V4-Flash | Winner |
|---|---:|---:|---|
| Robustness | 100.00 | 70.69 | Qwen |
| Safety | 97.30 | 96.85 | Qwen |
| Agentic | 94.06 | 96.30 | DeepSeek |
| Classification | 100.00 | 100.00 | Tie |
| Code | 80.90 | 94.59 | DeepSeek |
| Composition | 100.00 | 100.00 | Tie |
| Instruction | 87.42 | 95.79 | DeepSeek |
| Long context | 55.88 | 55.88 | Tie |
| Planning | 95.49 | 96.85 | DeepSeek |
| Structured | 96.14 | 97.56 | DeepSeek |
| Tool use | 77.45 | 84.63 | DeepSeek |
| Visual | 81.23 | 84.62 | DeepSeek |

DeepSeek completed more executable code tests, multi-step tool workflows, and
strict formatting tasks. Qwen was substantially stronger at abstaining,
requesting missing information, and avoiding unnecessary tool calls. Both
deployments missed the hard long-context retrieval scenario.

## Deployments

- **Qwen:** RadixArk Qwen3.8-27B NVFP4, Mia SGLang one-Spark recipe, MTP3,
  FP8 KV, 262,144-token ceiling.
- **DeepSeek:** official DeepSeek-V4-Flash-0731 revision `9e165c30`, Mia Anemll
  vLLM two-Spark TP2 recipe, official DSpark K5, `nvfp4_ds_mla` KV,
  1,048,576-token ceiling.
- DeepSeek requests explicitly used `chat_template_kwargs.thinking=false`.
  Generic Qwen-style thinking keys do not disable DeepSeek reasoning.
- DeepSeek's session recorded 199,510 draft tokens and 129,598 accepted tokens,
  a 64.96% DSpark acceptance rate.

This is a comparison of the recommended local deployments, not equal-hardware
efficiency: Qwen used one DGX Spark and DeepSeek used two.

## Sandbox correction

Apple's Xcode Python 3.9.6 crashed in SQLite while grading `CODE-02` and
`CODE-08`, creating false zeroes in both original reports. The parent
benchmark and model servers did not crash.

All 12 saved SQL responses (two models, two scenarios, three repeats) were
regraded without regeneration under Homebrew Python 3.14.7 and SQLite 3.53.4.
Every repeat passed: `CODE-02` scored 4/4 and `CODE-08` scored 3/3 for both
models. The corrected results above replace only those false sandbox zeroes.
All other scenario scores, latency measurements, token counts, and artifacts
are unchanged.

The original reports are preserved verbatim for auditability:

- [Qwen original report](raw-qwen-report.md)
- [DeepSeek original report](raw-deepseek-report.md)
- [Machine-readable domain scores](domain-scores.csv)
- [SHA-256 manifest](SHA256SUMS)
