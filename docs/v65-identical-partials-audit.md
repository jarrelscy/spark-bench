# v6.5 Identical-Partial Audit

Date: 2026-07-31

## Evidence

The corrected 76-scenario v6.5 reports for GLM-5.2, Inkling Small, and
DeepSeek V4 Flash 0731 contain seven scenarios with the same partial score in
all three model families:

| Scenario | GLM | Inkling | DeepSeek | Audit finding |
|---|---:|---:|---:|---|
| CODE-01 | 0.80 | 0.80 | 0.80 | Hidden leading-zero rule was absent from the prompt. |
| CODE-02 | 0.50 | 0.50 | 0.50 | Fixture expected Bob at 50 despite a `>100` requirement and mislabeled Carol's net revenue. |
| TUH-05 | 0.00 | 0.00 | 0.00 | Grader required `list_directory`, but the scenario did not offer that tool. |
| IFH-03 | 0.67 | 0.67 | 0.67 | Metric regex accepted singular `meter`/`metre`, but rejected normal plurals. |
| MSC-01 | 0.125 | 0.125 | 0.125 | Prefilled chain calculated tax, not after-tax value, so every model correctly made another calculator call instead of emailing. |
| AP-02 | 0.46 | 0.46 | 0.46 | Grader searched the final response for prefilled DB calls and searched text rather than the email body for the result. |
| CODE-13 | 0.40 | 0.40 | 0.40 | Source inspection cannot work on dynamically executed classes; HTTP mocks returned status objects instead of raising `urllib.error.HTTPError`. |

The three reports are preserved in the qualification packs under:

- `glm52-quanttrio-200k/evidence/2026-07-31-v65-fixed-316k`
- `tonyd2wild-inkling-tp2-dspark/evidence/2026-07-31-v65-fixed-reasoning0`
- `deepseek-v4-flash-0731-spark/evidence/2026-07-31-dsv4-0731-qualified`

## Transcript Limitation

The v6.5 runner preserved per-repeat scores, the final grading reason, token
counts, and visual artifacts, but discarded non-visual response text and tool
calls. Therefore the old runs do not contain three recoverable raw transcripts
per scenario. Claims above are limited to facts proven by the three reports and
the deterministic rubric source; they do not pretend missing transcripts were
reviewed.

The repaired runner now writes one JSON transcript per scenario repeat under
the run artifact directory. Each record includes messages, offered tools,
response text, reasoning, assembled tool calls, score, and grading reason.

## Repair Contract

- Every tool required by a grader must be present in the offered schema.
- A prefilled multi-step history must leave exactly one executable next step.
- Values placed in structured tool arguments count as delivered output when
  the task explicitly asks for that tool action.
- Hidden code tests may test stated requirements, not unstated conventions.
- Network mocks must reproduce the documented standard-library behavior.
- Reruns after these changes form a new methodology cohort and must not be
  compared numerically with v6.5 as though only model weights changed.
