# v6.8.1: in-place coding-task refresh

This revision replaces the prompts and executable graders of exactly eight
existing scenarios: **CODE-02, CODE-06, CODE-07, CODE-08, CODE-09, CODE-10,
CODE-11, and CODE-12**. It does not create a new benchmark or scenario tier.
The other 68 scenario definitions, IDs, domains, weights, and selection rules
are unchanged. Run it through the existing `spark_bench.py eval` command.

## Changes

- **CODE-02 — revenue SQL:** completed-order filtering; pre-aggregate duplicate
  refunds to avoid join multiplication; NULL values; refund status; duplicate
  customer names; exact threshold and tie order. Five SQLite databases, with
  full ordered rows checked against independently computed Python expectations.
- **CODE-06 — TTL/LRU cache:** injected clock; exact expiration boundary;
  expired-entry purge before eviction; update TTL reset; explicit falsy values;
  zero-capacity and zero-TTL semantics; input validation.
- **CODE-07 — recursive structures:** ordered heterogeneous leaves, RFC 6901
  paths and escaping, nesting beyond the normal recursion limit, aliases vs
  ancestor cycles, empty structures, and rejection of unsupported inputs.
- **CODE-08 — window SQL:** duplicate months, row-level running totals,
  amount-only competition ranking with gaps, NULL partitions/amounts, empty
  input, deterministic output. Five SQLite databases with Python-computed
  expected rows; partial or merely plausible outputs do not pass a dataset.
- **CODE-09 — retry helper:** explicit initial attempt plus additional retries;
  injectable sleep; capped exponential delays; selective exception handling;
  exception identity; cancellation propagation; validation before side effects.
- **CODE-10 — state machine:** snapshot caller-owned mappings; falsy states;
  guards and actions in a specified order; failed-action rollback; reentrant
  transition rejection and recovery; observational `can_trigger`.
- **CODE-11 — refactoring:** preserve legacy floating-point rounding and edge
  behavior; reuse a shared helper (checked by replacing it with a spy); preserve
  iterator and step-by-step rounding semantics in discount chains.
- **CODE-12 — counter:** preserve original instance-lock requirement; add
  atomic compare-and-set and transfers; validate before mutation; opposite-
  direction contention with bounded joins; instrument locks to detect unlocked
  CAS and one-lock-at-a-time transfers without relying on accidental GIL races.

Every requirement is disclosed in its prompt. Test inputs, fixtures, and
expected answers stay grader-side; they are not appended to model messages.
The public repository includes these tests for auditability; "hidden" means
not supplied in a scenario prompt, not secret from someone reading the repo.

## Scoring and provenance

Behavioral groups/datasets retain partial credit. A score of 1.0 requires every
group/dataset to pass. Invalid code and sandbox timeouts cannot earn full credit.
The original code execution sandbox and SQLite executor remain in use.

Transcripts for these eight tasks contain
`scenario_revision: coding-hardening-1`. Methodology stamps now read
`v6.8.1-uncapped`, `v6.8.1-full`, or `v6.8.1-challenge`, depending on the existing
run mode. Capped modes must also get the new revision because their prompts
changed. Historical result files are not modified or relabeled. Do not rank
v6.8.1 scores together with v6.8.0/v6.7.1 scores as a comparable cohort.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 golden_gate.py
```

On a host with a nonstandard browser installation, set `SPARK_BENCH_CHROMIUM`
to its existing Chromium executable before running the golden gate. Do not
remove the visual checks simply to get a green gate.

The tests contain explicitly hand-written reference implementations and
plausible broken variants. These are **grader oracles, not model outputs or
benchmark scores**. Startup golden-gate checks now exercise a passing reference
and a failing variant for each of the eight production graders. Integration
also runs all eight through `run_suite`, twice, with a scripted oracle callback,
and verifies uncapped request behavior and persisted revision receipts.

The successful local verification comprised 64 unittest methods, 17/17 existing
check-level self-tests, and 28/28 golden-gate cases (including the existing real
browser-render tests). An AST comparison against the parent commit verified
that only the specified eight scenario definitions changed.

**Not yet established:** score separation across actual model deployments.
There has been no new Qwen/GLM run, no regrading of old model answers against
new prompts, and no claim that these tasks are empirically unsaturated. Fresh,
matched-contract runs are needed to calibrate their difficulty.
