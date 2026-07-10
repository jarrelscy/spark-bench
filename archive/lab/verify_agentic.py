#!/usr/bin/env python3
"""Run ONLY the 6 agentic scenarios against a live endpoint, print per-scenario
scores — to verify the current _run_agentic grader isn't auto-passing (1.0)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import eval_suite as E
from spark_bench import chat_stream

ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else "http://10.0.0.120:8902/v1"
MODEL = sys.argv[2] if len(sys.argv) > 2 else "gemma-26b"

def chat_fn(messages, max_tokens, temperature, tools, extra):
    r = chat_stream(ENDPOINT, MODEL, messages, max_tokens, temperature=temperature,
                    tools=tools, timeout=300, extra=extra)
    return r

ag = [sc for sc in E.SCENARIOS if sc.get("agentic")]
print(f"agentic scenarios found: {[s['id'] for s in ag]}")
scores = []
for sc in ag:
    try:
        score, reason, lat, text, ratio = E._run_agentic(sc, chat_fn, {}, 0.3, 300)
    except Exception as ex:
        score, reason = 0.0, f"ERROR {ex}"
    scores.append(score)
    print(f"  {sc['id']}: score={score:.3f}  ({reason[:80]})")
avg = sum(scores)/len(scores) if scores else 0
print(f"\nAGENTIC DOMAIN (avg): {avg*100:.1f}")
print(f"  v6.1 board said: 100.0 (inflated)  |  v5 harness said: 5.3 (correct)")
print(f"  VERDICT: {'✅ FIXED (grades strictly)' if avg < 0.5 else '❌ STILL AUTO-PASSING (broken)'}")
