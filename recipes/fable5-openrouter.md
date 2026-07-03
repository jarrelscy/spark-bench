# Fable 5 (claude-fable-5) — TrueScore runbook (OpenRouter)

Staged 2026-07-01. **Do not run until Fable 5 is live on OpenRouter.**
Goal: land Fable 5 on the wesche.com/dgx leaderboard as a new #1 (API "thinking-on"
asterisk category — same class as GLM-5.2, which is currently #1 at 77.3).

## What Fable 5 is (for the writeup)
- Model id `claude-fable-5` (OpenRouter: `anthropic/claude-fable-5`).
- 1M context; **$10 in / $50 out per 1M** (above Opus-tier — most expensive entry on the board).
- Anthropic's most capable model; strongest reasoning/agentic/coding.

## Why this needs special handling (4 gotchas)
1. **Thinking is always ON.** `thinking:{type:"disabled"}` → HTTP 400. Fable cannot run
   your think-OFF standard. It's a *thinking-on* entry (asterisk), directly comparable to
   the GLM-5.2 #1 (which was run `thinking:auto`), NOT to the think-OFF local models.
2. **Sampling params rejected.** `temperature`/`top_p`/`top_k` → 400. Handled by the
   env-gated guard added to `chat_stream()` (`SPARK_BENCH_OMIT_SAMPLING=1`), which pops
   them from the request body. Zero effect on any other model's runs.
3. **Depth via `effort`, not budget.** Guard injects `body["reasoning"]={"effort": ...}`
   from `SPARK_BENCH_REASONING_EFFORT`. OpenRouter accepts **low|medium|high**. `xhigh`/`max`
   only work on the native Anthropic API — if you want those, route direct (see below).
4. **`refusal` stop reason.** Cyber/bio safety classifiers may decline a request (HTTP 200,
   `stop_reason:"refusal"`). Your safety scenarios are already excluded from TrueScore, but a
   coding/tool scenario could trip a false positive → that scenario scores 0. Log refusals;
   optionally re-run refused scenarios with a fallback (see below). Expect a few, not many.

Also: **Efficiency + Responsiveness sub-scores (30% combined) will take a hit** from API
latency + minutes-long thinking turns — same as GLM-5.2's efficiency weakness. Expected;
note it in the published findings, don't "fix" it.

## Prereqs
- `export OPENROUTER_API_KEY=sk-or-...` (spark-bench reads OPENROUTER_API_KEY).
  ⚠️ **This is the #1 failure mode.** The 2026-07-01 `Sonnet-5-OpenRouter` run failed on
  ALL 64 scenarios with `HTTP 401 Unauthorized` (bogus TrueScore 15.5) because the key
  wasn't set/valid. The smoke test below catches this in ~1 min — do NOT skip it.
- Confirm the model id is live: `curl -s https://openrouter.ai/api/v1/models | grep -i fable`.

## Fire sequence
1. **Smoke test first (1 domain, no repeats):**
   ```
   ./run_fable5.sh --tier base --domains coding --repeats 1
   ```
   Verify: requests return 200 (not 400 on temperature/effort), text comes back, timing looks
   sane, no auth errors. If OpenRouter 400s on `effort:high`, drop to `medium` via
   `FABLE_EFFORT=medium ./run_fable5.sh ...`. If it 400s on a param, check the guard is active
   (`SPARK_BENCH_OMIT_SAMPLING` exported).
2. **Full run:**
   ```
   ./run_fable5.sh
   ```
   57 scenarios × repeats 2 + the auto throughput sweep is meaningless for an API model —
   add `--skip-throughput` (API tok/s isn't a cluster serving number).
   Long thinking turns may exceed the per-scenario timeout — if scenarios error on timeout,
   bump it (see spark_bench.py `eval` timeout handling) and re-run just the failed domains.
3. **Publish:** regenerate the leaderboard + wesche.com/dgx (`build_site.py` / `html_report.py`),
   then Sparkbench tweet with the new #1 line and @NVIDIAAI/@AnthropicAI tags. Update
   `obsidian-vault/Projects/Spark-Bench-Results.md` (leaderboard table + a Fable 5 findings note).

## Optional: native Anthropic path (for xhigh/max effort + server-side refusal fallback)
OpenRouter caps effort at `high` and has no server-side refusal fallback. To run Fable at
`xhigh`/`max` and auto-recover refusals to opus-4-8, point spark-bench at an OpenAI-compatible
Anthropic shim (or extend `chat_stream` to hit `/v1/messages` natively) with:
`thinking` omitted, `output_config.effort:"xhigh"`, betas `["server-side-fallback-2026-06-01"]`,
`fallbacks:[{"model":"claude-opus-4-8"}]`. Not needed for a first leaderboard entry — do the
OpenRouter run first, add the native path only if you want the max-effort number.

## Guard reference (added to chat_stream, env-gated, safe for all other models)
- `SPARK_BENCH_OMIT_SAMPLING=1` → drops temperature/top_p/top_k from the request body.
- `SPARK_BENCH_REASONING_EFFORT=high` → sets `reasoning:{effort:"high"}`.
Both are no-ops unless set, so existing local/GLM runs are unaffected.
