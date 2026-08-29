# SparkBench v6.8.0 Uncapped

Date: 2026-08-29

## Why this is a new version

SparkBench v6.8.0 keeps the v6.7.1 scenario bank, prompts, rubrics, domain
weights, and TrueScore formula. It changes the generation and validation
contract materially enough to create a new comparability boundary.

A client-side completion cap can truncate hidden reasoning before a model emits
its final answer. Removing that cap exposed the opposite failure mode: a model
can also consume its entire context with malformed repetition. v6.8.0 measures
both honestly instead of treating either transport truncation or degenerate
output as a valid answer.

## Qualification contract

A `v6.8.0-full-uncapped` qualification run uses:

- all 76 scenarios;
- two repeats unless a published cohort declares another count;
- no client `max_tokens` field;
- no model-request timeout (`--timeout 0`);
- native server token accounting where available;
- native terminal finish-reason preservation;
- score zero for `finish_reason=length` or detected runaway output;
- repeated-character and repeated-phrase degeneration detection;
- immutable source evidence for any recovered or corrected transcript;
- exact scenario and repeat identities for tail recovery;
- the normal golden gate, grader git provenance, endpoint identity check,
  structured tool-call preflight, and run markers.

The server context window remains a real limit. “Uncapped” means SparkBench does
not impose a smaller client completion budget.

## Degeneration guards

The reference guard supports two targeted signals:

1. a full rolling window containing one repeated visible character;
2. an extremely compressible rolling window indicating a repeated phrase or
   code block.

These guards are not blanket answer-length limits. A legitimately long,
high-entropy response can continue to the server context ceiling. A triggered
guard records `finish=runaway`, preserves the observed output and request
identity, aborts or disconnects the request according to backend support, and
scores the repeat as a model failure.

Recommended reference windows for the inaugural cohort are 4,096 characters
for a single-character loop and 8,192 characters for a repeated-phrase loop.
They are the v6.8 CLI defaults and must both remain positive for an uncapped
run. Abort mode defaults to `auto`: `/models` metadata selecting
`owned_by=sglang` uses SGLang's explicit request abort, while other backends
close the stream and rely on disconnect cancellation. All three values are
recorded as run provenance.

## Version boundary

- Capped legacy runs retain `v6.7.1-full` or `v6.7.1-challenge`.
- Uncapped full runs stamp `v6.8.0-full-uncapped`.
- Uncapped challenge runs stamp `v6.8.0-challenge-uncapped`.
- Diagnostic subsets stamp `v6.8.0-full-subset-uncapped`.

Scores should only be compared when scenario bank, repeat count, temperature,
thinking mode, and v6.8.0 generation/validation contract match. Hardware,
quantization, runtime, context ceiling, and speculative-decoding recipe remain
deployment variables and must be disclosed.

## Inaugural comparison

The first v6.8.0 evidence package compares Qwen3.8-Flash-Next NVFP4 TP2 with
speculative decoding disabled against GLM-5.3-Flash NVFP4 TP2 with DFlash2 K7:

[`results/comparisons/2026-08-29-qwen38-flash-next-vs-glm53-flash-v680`](../results/comparisons/2026-08-29-qwen38-flash-next-vs-glm53-flash-v680/README.md)

The package includes the corrected scorecard, per-domain and per-repeat scores,
failure classifications, transcript hashes, and sanitization/validation notes.
