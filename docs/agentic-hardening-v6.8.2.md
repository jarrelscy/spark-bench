# v6.8.2 — Five stateful agentic replacements

This revision upgrades **AG-01, AG-02, AG-10, AG-11 and AG-12** in place.
They are the five agentic entries in the earlier six-deployment saturation audit,
not a newly invented subset. The existing coding refresh is retained unchanged.
There are still 76 scenarios and 12 domains, with the same IDs, weights, tiers,
selection rules and turn budgets. The existing `spark_bench.py eval` command works.
An AST comparison against parent commit `9101054` verified that only these five
scenario definitions changed; the other 71 definitions are unchanged.

## What the agent must resolve

- **AG-01 — travel coordination:** resolve an active New York account manager
  among similarly named/retired/London contacts. The correct contact is beyond
  the first directory page. Paginated, unsorted calendar data affects the earliest
  legal slot. Weather values must reach the correct recipient and final receipt.
- **AG-02 — launch coordination:** distinguish the latest approved plan from an
  older superseded plan and a newer unapproved draft. A competing booking arrives
  after the first calendar read. The first create reports a conflict without
  committing; the agent must refresh availability and resolve it before notifying
  both teams using the approved revision's actual duration and preparation tasks.
- **AG-10 — severe-weather recovery:** an event creation and an email delivery
  commit successfully but lose their acknowledgements. Request lookup or retrying
  the identical idempotency key/payload both work. Fresh keys can cause duplicates,
  which are retained in simulated state and fail the task. The non-severe branch
  is tested separately and must produce no writes.
- **AG-11 — exact-target repair:** reconcile approved incident documents and nearly
  identical calendar entries using incident ID, booking code and active status.
  Update the correct existing event in place using its observed version. Preserve
  the other incident's event. Creation/cancellation tools are not available here;
  inventing a legacy tool name cannot bypass the isolated simulator.
- **AG-12 — missing information:** use the final approved amount and sign-off,
  but do not copy a currency from an obsolete draft. An explicit `ask_user` tool
  supplies the simulated user's answer. If the user cannot answer, the valid
  outcome is an honest `needs_input` receipt and zero dependent writes.

## Stateful execution and scoring

Each repeat receives a fresh isolated world. The existing simulator continues to
serve the other seven agentic tasks without these new semantics. Tools expose
only observations, not expected answers or grader internals. Pagination tokens
are query-bound; idempotency keys are bound to both tool and payload; stale update
versions fail without mutation. Invalid model arguments are recoverable tool
errors, not transport failures or benchmark crashes.

The new grader checks:

1. Exact created/updated event state, including preserved unrelated records.
2. Exact delivered notifications, recipients and structured payload facts.
3. Every applied mutation, including unwanted intermediate writes and duplicates.
4. Observed source facts and completed listings before dependent writes.
5. Exact record reads after the last write; event verification before dependent
   email notifications. A write acknowledgement or request lookup is not enough.
6. A truthful structured final receipt listing the actual affected IDs and facts.

A wrong write followed by a repair is still visible to the safety check. A lucky
currency guess is not grounded approval. Partial diagnostics remain available,
but **any failed required check caps the score at 0.49**, below the existing 0.5
task-pass threshold. Only complete correctness earns 1.0. Non-clean terminal
finishes also cannot qualify. This does not change global benchmark weights or
redefine repeat consistency as successful completion.

All tested requirements are stated in the scenario/tool contracts. Notifications
use a structured `details` payload rendered into the simulated email, and the
final response is a documented JSON receipt. This avoids unreliable keyword
matches being mistaken for verified task outcomes.

## Evidence and comparability

Each transcript includes `scenario_revision: agentic-hardening-1`, plus
`response.agentic_trace.environment` (source state, read receipts, mutation audit,
idempotency records and final records) and `response.agentic_trace.outcome`
(per-check diagnostics and strict success). These grader-side receipts are
saved after execution; they are not sent to the agent as tool results.

Methodology labels advance to `v6.8.2-uncapped`, `v6.8.2-full` and
`v6.8.2-challenge`. Historical results and labels remain untouched. The earlier
coding tasks retain `scenario_revision: coding-2026-09-v1`.

Dirty-tree provenance now includes the modular coding/agentic graders and the
oracle files used by the golden gate, as well as the render graders. Editing an
imported grader module must not silently retain a clean grader revision stamp.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 golden_gate.py
```

Use the existing `SPARK_BENCH_CHROMIUM` override if the host needs its installed
Playwright Chromium instead of system Chrome. Do not loosen render thresholds.

Tests exercise all five reference policies, alternate facts, a no-severe-weather
branch, answered and unanswered clarification, both safe unknown-write recovery
strategies, repeat isolation, malformed arguments, query-bound pagination,
optimistic conflicts, idempotency conflicts, and wrong-then-repaired mutations.
There are 26 deliberate bad-policy variants plus two unanswered-clarification
failures. A real `run_suite` integration test executes the five scripted policies
twice and reads all ten persisted transcripts, including uncapped/thinking-off
request settings and outcome receipts.

The startup golden gate checks a good and bad interactive policy for every new
task, rejects old count-only transcripts without authoritative state, and retains
the coding and real browser-render checks. A separate fault-injection UNIT test
proves the gate catches auto-pass, text-only scoring, parser failure and rounding
partial credit up to success. Rendering is explicitly mocked only for this
fault-injection unit test; standalone golden-gate validation uses the real browser.

**These policies are hand-written grader oracles, not model outputs or model
scores.** No fresh deployment comparison has been run. Empirical separation of
Qwen, GLM or other deployments still requires matched-contract runs on this new
revision. Serving setups are not changed by this implementation.
