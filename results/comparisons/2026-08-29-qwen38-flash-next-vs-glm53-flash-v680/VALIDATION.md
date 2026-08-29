# Validation and sanitization

## Coverage

- Qwen validated set: 152 unique transcript identities, 76 scenarios, two repeats
- GLM validated set: 152 unique transcript identities, 76 scenarios, two repeats
- Missing identities: 0
- Extra identities: 0
- Duplicate identities: 0
- Transport errors: 0 for both validated sets

The Qwen run has a native DONE marker and no `length`, `runaway`, or offline
repetition flags. The GLM validated set combines its immutable original run with
exact tail-recovery identities under the unchanged deployment. Four native
context-length failures are preserved by source hash and scored zero under the
v6.8.0 terminal-validation rule.

## Score recomputation

The exact component values were recomputed from the 304 per-repeat transcript
records with the repository's TrueScore weights:

```text
0.55 × Quality
+ 0.25 × Calibration
+ 0.15 × Reliability
+ 0.015 × Efficiency
+ 0.035 × Responsiveness
```

The GLM derived report and manifest reproduced byte-for-byte across a second
recomputation. The public scorecard contains the exact floating-point results;
the README rounds to two decimals.

## Correction boundary

Only four GLM records change score:

- `AG-04-repeat-1.json`
- `AG-05-repeat-1.json`
- `AG-08-repeat-1.json`
- `CODE-09-repeat-1.json`

Each contains a native `length` finish at approximately the 262K context
ceiling. Every corrected score is zero. No clean terminal transcript score was
changed. `transcript-hashes.json` records both the immutable source hash and the
validated derived hash for GLM.

The excluded Qwen NEXTN deployment does not contribute any score. Its failure
and the spec-off control are diagnostic evidence only.

## Public-data boundary

The public package intentionally excludes raw million-character responses,
private endpoint addresses, usernames, machine-specific absolute paths, RoCE
addresses, credentials, and internal launcher details. It publishes:

- exact scores and native finish classifications;
- per-repeat native completion-token counts;
- the four corrected failure identities;
- transcript SHA-256 hashes;
- sanitized deployment settings sufficient to identify the compared recipes;
- all benchmark prompts and graders through the repository source.

A private-data scan must return zero matches before the package is pushed.
