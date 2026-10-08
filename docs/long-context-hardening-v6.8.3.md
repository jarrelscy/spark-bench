# v6.8.3 — LC-03 cross-document reconciliation

This replaces the saturated **LC-03** single-passcode lookup in place. It does
not add a benchmark, domain, scenario, new weight, or new model run. The suite
remains 76 scenarios, and the other 75 scenario definitions are unchanged from
`80fa1b7` (v6.8.2), verified by AST comparison. In particular, **LCH-01 is unchanged**.
The earlier eight coding and five agentic replacements are retained.

## New task

A fixed export contains 112 individually cited records. Resolve four archive
routing requests at the explicit UTC cutoff `2026-09-10T12:00:00Z`:

- Join ticket → exact account ID → region/service binding → policy revision →
  correctly scoped approval. Two accounts have the same display name and IDs
  differing only in digit `1` versus capital `I`.
- Separate effective dates from approval timestamps and document order. Reject
  future-effective revisions, approvals issued after the cutoff, unapproved or
  wrong-region revisions, and a revision expiring exactly at the cutoff.
- Reconcile a newer approval that was subsequently withdrawn. Fall back to the
  latest still-approved effective revision; a high revision label or recently
  issued approval for an older effective revision does not outrank it.
- Report `conflict` for two approved revisions tied on the greatest effective
  timestamp, rather than inventing a label-based tiebreaker.
- Report `insufficient_evidence` when the exact mapped policy has no revision
  passages. A similarly named account or another region's policy is not evidence.
- Cite the complete required mapping and authority chains. The withdrawal that
  justifies fallback and both sides of a genuine conflict must be cited.

All precedence, validity, abstention, output, and citation rules appear in the
prompt. The answer values use opaque route identifiers, so their wording does
not reveal which revision is current, future, or withdrawn. Relevant joins are
spread across the export, mixed with different kinds of similarly shaped records.

## Input and request contract

- Fixed input: **17,701 UTF-8 bytes**, including instructions and export.
- Build-time input guard: at most **24,000 UTF-8 bytes**.
- Declared context requirement: **32,768 tokens**, persisted in each LC-03
  transcript as `context_requirement_tokens`.
- This is a conservative operating requirement, **not** an exact token count,
  automatic server admission check, or measured model context ceiling. Before
  model comparison, verify each backend's locally templated request fits its
  configured window with response headroom. Do not truncate the export.
- Uncapped runs still pass `max_tokens=None` to the existing request layer. No
  new response or wall-time limit is added to uncapped evaluation.
- Only in the pre-existing capped mode, LC-03's allowance changes from 200 to
  1,600 tokens to accommodate the four-answer cited JSON rather than a passcode.
  No other scenario's budget changes.

## Scoring

`long_context_hardening.py` provides the fixed prompt and a hand-authored
outcome oracle. Expected answers are grader-side and are not added to messages.
These fixtures are publicly auditable, not claimed to be a private held-out set.

Full credit requires all four answers, exact identities and relationships,
correct values/abstentions, and the required citation sets. Citation order,
JSON key order, and whitespace do not affect correctness. Duplicate/unrelated
citations, duplicate JSON keys, non-finite constants, invented values, extra
fields/prose, wrong answer order, and malformed responses cannot pass.

Malformed contracts score zero. For schema-shaped but incorrect answers,
partial diagnostics score `0.49 * correct_fields / 32`. Only complete correctness
scores `1.0`, so any wrong answer or missing essential citation remains below
the existing harness pass threshold of `0.5`. The textual grading receipt lists
failed fields and `strict_success`; nonterminal finishes cannot pass.

## Validation

All validation below is **offline grader/harness testing, not model evidence**:

- Full unittest discovery: **98 tests passed**.
- Golden gate: **73/73 cases passed**, including the existing real-browser visual
  fixtures, the new positive reference, and **35 deliberately defective outputs**.
- A separately written relational resolver derives the answer from the actual
  document export and agrees with the independently hand-written golden answer.
- Every individual answer field and every required citation is mutation-tested.
- Five deterministic export-order/distractor variants preserve the correct
  resolution. Seven single-fact source changes exercise effective/expiry bounds,
  scope, cutoff, revocation, revision precedence, and genuine conflict resolution.
  These are fixture invariants, not held-out model trials.
- Fault injection confirms the golden gate rejects auto-pass, reject-all,
  substring-only, and corrupted-expectation graders. Render mocks are used only
  for these unit fault-injection tests; the standalone gate uses the real browser.
- The actual suite runner writes and verifies both LC-03 repeat receipts with
  revision, context requirement, original messages, and score. A near-correct
  answer with one wrong value is verified to produce a zero task pass rate.
- New production and golden-oracle modules are included in dirty-tree provenance.

Reproduce from the repository root:

```sh
python3 -m unittest discover -s tests -q
python3 golden_gate.py
```

On the validation Mac the real render gate used its existing
`SPARK_BENCH_CHROMIUM` override pointing to Playwright's bundled Chromium.
No rendering thresholds were changed.

## Versioning and limitations

Methodology stamps advance to `v6.8.3-full`, `v6.8.3-challenge`, and their
existing subset/uncapped forms. LC-03 transcripts carry
`scenario_revision: long-context-reconciliation-1`. IDs, selection rules,
domain/group, difficulty weight, and repeat policy are preserved.

Historical reports/results are not edited or relabeled. Do not rank scores
across these methodology revisions as directly comparable. No fresh model
runs, discrimination measurements, pushes, publications, or serving changes
were performed for this replacement. A matched fresh cohort is still required
to establish whether the new case separates real models.
