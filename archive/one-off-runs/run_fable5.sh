#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Fire-ready Fable 5 (claude-fable-5) TrueScore run via OpenRouter.
# DO NOT run until Fable 5 is actually live on OpenRouter.
# See recipes/fable5-openrouter.md for the full runbook + gotchas.
#
# Usage:
#   export OPENROUTER_API_KEY=sk-or-...
#   ./run_fable5.sh                 # full v5c eval (57 scenarios, repeats 2)
#   ./run_fable5.sh --tier base     # smoke: base tier only (do this FIRST)
#   ./run_fable5.sh --domains coding # single-domain probe
# ---------------------------------------------------------------------------
set -euo pipefail
: "${OPENROUTER_API_KEY:?set OPENROUTER_API_KEY first}"

MODEL="${FABLE_MODEL:-anthropic/claude-fable-5}"

# Fable 5 rejects sampling params and takes reasoning depth via `effort`.
# The env-gated guard in spark_bench.py chat_stream() handles both.
export SPARK_BENCH_OMIT_SAMPLING=1
# OpenRouter's reasoning.effort accepts low|medium|high. xhigh/max only work on
# the native Anthropic API (see runbook). Default to high for the OpenRouter path.
export SPARK_BENCH_REASONING_EFFORT="${FABLE_EFFORT:-high}"
export OPENROUTER_X_TITLE="spark-bench"
export OPENROUTER_HTTP_REFERER="https://wesche.com/dgx"

cd "$(dirname "$0")"

exec ./spark_bench.py eval \
  --label "fable5-openrouter" \
  --endpoint "https://openrouter.ai/api/v1" \
  --model "$MODEL" \
  --topology "OpenRouter API" \
  --thinking auto \
  --repeats 2 \
  --notes "Fable 5 (claude-fable-5) via OpenRouter. Thinking always-on (effort=${SPARK_BENCH_REASONING_EFFORT}); sampling params omitted (400 otherwise). API 'thinking-on' asterisk category, same as GLM-5.2 #1. Efficiency/Responsiveness reflect API latency + long thinking turns." \
  "$@"
