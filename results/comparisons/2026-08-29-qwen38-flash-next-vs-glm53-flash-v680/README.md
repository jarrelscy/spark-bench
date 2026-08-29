# SparkBench v6.8.0 Uncapped: Qwen3.8-Flash-Next vs GLM-5.3-Flash

Validated on 2026-08-29 with the inaugural
[`v6.8.0-full-uncapped`](../../../docs/v680-uncapped.md) contract. Each
deployment ran the same 76 scenarios twice at temperature 0.3 with thinking
disabled, no client completion cap, and no model-request timeout.

> **Scope:** This is a deployment comparison on DGX Spark, not a universal
> base-model ranking. Qwen used speculative decoding disabled. GLM used DFlash2
> K7 and a disclosed forced-no-thinking template.

## Result

| Metric | Qwen3.8-Flash-Next | GLM-5.3-Flash | Winner |
|---|---:|---:|---|
| **Validated TrueScore** | **87.02** | **85.67** | **Qwen +1.35** |
| Capability / quality | 90.50 | 87.41 | Qwen +3.09 |
| Calibration | 76.02 | 81.60 | GLM +5.57 |
| Reliability | 93.14 | 87.35 | Qwen +5.80 |
| Operational score | 85.28 | 81.82 | Qwen +3.45 |
| Median scenario latency | 5.33 s | 7.02 s | Qwen, 24% lower |
| Pass@1 | 94.7% | 93.4% | Qwen |
| Pass@K | 89.5% | 82.9% | Qwen |
| Total native output tokens | 111,726 | 1,207,779 | Qwen was substantially less verbose |

Both deployments qualify as **Strong (grade B)**. Qwen's advantage came from
higher capability, reliability, and responsiveness. GLM was better calibrated,
especially in the safety domain, and won long-context, planning, composition,
and tool-use quality.

## Domain quality

| Domain | Qwen | GLM | Winner |
|---|---:|---:|---|
| Agentic | 98.09 | 85.76 | Qwen |
| Classification | 100.00 | 100.00 | Tie |
| Code | 87.06 | 82.75 | Qwen |
| Composition | 75.53 | 100.00 | GLM |
| Instruction | 96.98 | 90.09 | Qwen |
| Long context | 55.88 | 100.00 | GLM |
| Planning | 86.46 | 97.64 | GLM |
| Robustness | 93.40 | 51.70 | Qwen |
| Safety | 73.06 | 90.21 | GLM |
| Structured | 100.00 | 85.46 | Qwen |
| Tool use | 77.00 | 87.08 | GLM |
| Visual | 89.72 | 84.25 | Qwen |

## Why Qwen won

Qwen's validated spec-off run completed all 152 transcripts without a native
`length` finish, detected runaway output, transport error, or offline repetition
flag. It finished the full gated run in 4,737 seconds (1:18:57).

GLM produced four intermittent context-length repetition collapses:

| Transcript | Failed native completion tokens | Original rubric score | Validated score |
|---|---:|---:|---:|
| `AG-04-repeat-1` | 261,115 | 0.1429 | **0** |
| `AG-05-repeat-1` | 260,904 | 0.6667 | **0** |
| `AG-08-repeat-1` | 260,598 | 1.0000 | **0** |
| `CODE-09-repeat-1` | 262,038 | 1.0000 | **0** |

The legacy rubric awarded partial or full credit when a tool-state check or code
test passed before the malformed terminal output ended at context length.
v6.8.0 invalidates that credit: a native `length` or detected `runaway` finish
is a model failure worth zero. Original source hashes remain in the public
manifest; only the validated score layer changes.

The GLM failures repeated narration or code blocks. They were observed under the
DFlash2 deployment, but no DFlash2-off A/B was run, so this package does **not**
claim DFlash2 caused them.

## Qwen NEXTN exclusion

The initial Qwen NEXTN deployment is excluded from the scorecard. On `AG-11` it
emitted 253,500 exclamation-mark tokens and ended at context length after
14,698.77 seconds. A guarded reproduction stopped the same one-character loop
after 4,096 visible characters. With NEXTN disabled, the same diagnostic passed
5/5 checks in 22.87 seconds with 451 native completion tokens.

That A/B isolates the observed failure to the NEXTN serving path used here. It
does not claim every NEXTN configuration fails.

## Deployments

| | Qwen3.8-Flash-Next | GLM-5.3-Flash |
|---|---|---|
| Checkpoint format | NVFP4 | NVFP4 |
| Hardware | 2× DGX Spark, TP2 over RoCE | 2× DGX Spark, TP2 over RoCE |
| Runtime | SGLang | Custom vLLM |
| Speculative decoding | Off | DFlash2 K7 |
| Context ceiling | 262,144 | 262,144 |
| Thinking control | Native disabled template controls | Forced off with preserved custom template |
| KV / state | BF16 Mamba state | FP8 E4M3 KV cache |

## v6.8.0 integrity contract

- 76 scenarios × 2 repeats = 152 transcripts per deployment
- temperature 0.3; no seed
- `max_tokens` omitted
- model-request timeout disabled
- native finish reasons preserved
- native `length` and detected `runaway` completions score zero
- repeated-character and repeated-phrase degeneration detection
- exact scenario/repeat tail recovery without overwriting source evidence
- 12/12 golden gate, endpoint identity, and tool-call preflight
- zero transport errors in both validated sets

The scenario bank and TrueScore weights are unchanged from v6.7.1. The
generation and validation contract changed, so capped v6.7.1 scores are not
directly comparable with v6.8.0 uncapped results.

## Audit files

- [`scorecard.json`](scorecard.json) — exact overall scores and deltas
- [`methodology.json`](methodology.json) — generation, hardware, and validation contract
- [`domain-scores.csv`](domain-scores.csv) — per-domain quality and reliability
- [`scenario-scores.csv`](scenario-scores.csv) — all 304 per-repeat scores and native finishes
- [`failures.json`](failures.json) — Qwen NEXTN A/B and GLM failure classifications
- [`transcript-hashes.json`](transcript-hashes.json) — SHA-256 hashes for every source/validated transcript
- [`VALIDATION.md`](VALIDATION.md) — coverage, correction, and sanitization checks
- [`verify.py`](verify.py) — one-command checksum and coverage verifier
- [`SHA256SUMS`](SHA256SUMS) — package file checksums

Run `python3 verify.py` inside this directory to validate the public package.
