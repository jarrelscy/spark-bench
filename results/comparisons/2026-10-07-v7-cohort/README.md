# v7.0 cohort: GLM-5.3-Flash, RED-SNOW, Qwen3.8 (October 2026)

Six deployments ran the full **v7.0 suite**: 80 scenarios across 13 domains, 2 repeats, thinking off, uncapped. Uncapped means every request may use the whole remaining context window as its output budget. All runs used grader `15c65bc`, passed the golden gate (73/73), and had 0 transport errors. Per-run reports are in [`runs/`](runs/).

These runs were made on the pre-release branch at grader `15c65bc`, so their reports carry the methodology stamp `v6.8.3-full-uncapped`. The scenario set and graders are identical to the v7.0 release. The release commit only renames the version labels.

| # | Deployment | Hardware | Engine | TrueScore |
|---:|---|---|---|---:|
| 1 | RED-SNOW-5.3-Flash 2.49bpw SAGE EXL3 (@vic305 × @Blackfrost_AI) | 1 Spark | exllamav3 `7c1636f`, MTP 2, Q4 KV, 262K | **85.1** |
| 2 | GLM-5.3-Flash EXL3 4bpw | 2 Sparks TP2 | TensorFold v0.6.0 + patches, DFlash2, FP8 KV | **84.8** |
| 3 | Qwen3.8-27B MLX-4bit | 1 Spark | TensorFold 0.6.5 + DFlash2 | **82.9** |
| 4 | Qwen3.8-Flash-Next NVFP4 (RadixArk) | 2 Sparks TP2+EP | vLLM, MTP 3, 262K | **79.4** |
| 5 | Qwen3.8-Flash-Next MLX-4bit | 1 Spark | TensorFold 0.6.5 + MTP | **78.5** |
| 6 | Qwen3.8-Flash-Next NVFP4 (nvidia) | 2 Sparks TP2 | TensorFold Zig engine, 1M | **77.9** |

Sampling followed each model's recommendation:
- **GLM-5.3-Flash:** temp 1.0, top_p 0.95.
- **RED-SNOW:** temp 0.7, top_p 0.95, min_p 0, from its `generation_config`.
- **Qwen3.8:** temp 1.0, top_p 0.95, top_k 20.

Repeats use distinct seeds (`SPARK_BENCH_SEED_PER_REPEAT`).

## Reading these numbers

- **These are deployments, not models.** Engine, quantization, Spark count and sampling all differ between rows. Rows 4–6 are the same model on three stacks, and they land within 1.5 points of each other.
- **Gaps under about 1 point are within run-to-run noise.** Rows 1 and 2 are a tie.
- **RED-SNOW is a security fine-tune.** Row 1 compares fine-tune + quant against base + quant. Its lower Safety domain average comes entirely from the two content-refusal scenarios (SA-03, RR-04). Those are informational and carry 0% weight in TrueScore. On the 9 scored security scenarios, rows 1 and 2 both pass 8 of 9.
- **Not shown:** a GLM-5.3 (full) 2.75bpw run on 4 Sparks scored 70.8. It's left out of the table because one TensorFold rank hung, and the last two scenarios were scored 0 after a 12-hour stall.

Deployment recipe for row 1: [Weschera/RED-SNOW-5.3-Flash-2.49bpw-1x-DGX-Spark](https://github.com/Weschera/RED-SNOW-5.3-Flash-2.49bpw-1x-DGX-Spark).
