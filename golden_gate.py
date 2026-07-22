#!/usr/bin/env python3
"""Golden gate: the grader must prove itself on known transcripts before any
eval run is allowed to record results.

Three layers, all offline (no network, no model):
  1. check-level   : eval_suite._selftest() — individual grader checks on
                     canned responses.
  2. grader-level  : _grade_agentic() on hand-built transcripts with
                     hand-computed expected scores (perfect / partial / garbage).
                     A perfect transcript scoring <1.0 = grader too strict or
                     dead parser class; a garbage transcript scoring >0 = the
                     v6.1 auto-pass class.
  3. harness-level : _run_agentic() driven end-to-end by scripted chat_fns
                     (no network), so the tool-call assembly + simulated env +
                     grading pipeline is tested as one unit.

`--prove` sabotages the grader in-memory (auto-pass stub, dead parser) and
asserts the gate FAILS — i.e. it demonstrates the gate would have caught the
two historical disasters.

Exit code 0 = gate passed, 1 = gate failed. run_eval refuses to start on 1.
"""
import sys

import eval_suite as ev

EPS = 1e-6


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def _env():
    return ev._make_env()


def _ag11_perfect_env():
    """Hand-built end state of a model that did AG-11 perfectly."""
    env = _env()
    env["events_created"].append(
        {"title": "Postmortem SPARK-7741", "day": "next_thursday",
         "start": "10:00", "duration": 60})
    env["emails_sent"].append(
        {"to": "priya@corp.com", "subject": "Postmortem scheduled",
         "body": "Booking code SPARK-7741, postmortem on next_thursday."})
    tool_log = [
        {"tool": "create_event",
         "args": {"title": "Postmortem SPARK-7741", "day": "next_thursday",
                  "start": "10:00", "duration": 60},
         "result": "Event created"},
        {"tool": "send_email",
         "args": {"to": "priya@corp.com", "subject": "Postmortem scheduled",
                  "body": "Booking code SPARK-7741 on next_thursday."},
         "result": "Email sent"},
    ]
    text = ["The booking code is SPARK-7741, the postmortem is on next_thursday "
            "(Thursday), and the escalation contact is priya@corp.com."]
    return env, tool_log, text


def _ag11_partial_env():
    """Event has the code but the WRONG day; no email; summary omits the day.
    Exactly 1 of 5 checks passes -> expected score 0.2."""
    env = _env()
    env["events_created"].append(
        {"title": "Postmortem SPARK-7741", "day": "friday",
         "start": "10:00", "duration": 60})
    tool_log = [{"tool": "create_event",
                 "args": {"title": "Postmortem SPARK-7741", "day": "friday"},
                 "result": "Event created"}]
    text = ["I scheduled the postmortem."]
    return env, tool_log, text


def _ag11_garbage_env():
    """A model that called NO tools and just claimed success (what a dead
    tool-call parser looks like to the grader). Expected score: exactly 0."""
    env = _env()
    return env, [], ["Done! I have completed all the requested steps."]


# --------------------------------------------------------------------------- #
# scripted chat_fns for layer 3 (no network)
# --------------------------------------------------------------------------- #
def _resp(text="", tool_calls=None):
    """Shape a response exactly like spark_bench.chat_stream returns."""
    return {"text": text, "reasoning": "", "tool_calls": tool_calls or [],
            "total": 0.01, "ttft": 0.01, "completion_tokens": len(text) // 4,
            "prompt_tokens": 100, "finish": "tool_calls" if tool_calls else "stop"}


def _tc(name, args_json):
    """One streamed tool-call fragment as chat_stream would collect it."""
    return {"index": 0, "function": {"name": name, "arguments": args_json}}


def perfect_ag11_model():
    """Scripted model that solves AG-11 correctly in 3 turns."""
    state = {"turn": 0}

    def chat_fn(messages, max_tokens, temperature, tools, extra):
        t = state["turn"]
        state["turn"] += 1
        if t == 0:
            return _resp(tool_calls=[_tc(
                "create_event",
                '{"title": "Postmortem SPARK-7741", "day": "next_thursday", '
                '"start": "10:00", "duration": 60}')])
        if t == 1:
            return _resp(tool_calls=[_tc(
                "send_email",
                '{"to": "priya@corp.com", "subject": "Postmortem scheduled", '
                '"body": "Booking code SPARK-7741, postmortem next_thursday."}')])
        return _resp(text="Summary: booking code SPARK-7741, required day "
                          "next_thursday (Thursday), escalation contact "
                          "priya@corp.com.")
    return chat_fn


def dead_parser_model():
    """Scripted model emulating a wrong --tool-call-parser: fluent text,
    never a structured tool_call. The v5-agentic failure mode."""
    def chat_fn(messages, max_tokens, temperature, tools, extra):
        return _resp(text="I have checked the calendar, created the event and "
                          "sent the emails. Everything is complete.")
    return chat_fn


# --------------------------------------------------------------------------- #
# the gate
# --------------------------------------------------------------------------- #
def _sc(scenario_id):
    for s in ev.SCENARIOS:
        if s["id"] == scenario_id:
            return s
    raise KeyError(scenario_id)




# ---- v6.5 render-grader fixtures (2D canvas, time-based, compressed) ------ #
V3D_RACE_PASS = """<!DOCTYPE html><html><body style="margin:0;background:#123">
<canvas id="c" width="480" height="300"></canvas><script>
const x = document.getElementById("c").getContext("2d");
const t0 = performance.now();
function draw() {
  const t = ((performance.now() - t0) / 1000) % 6;  // 6s loop
  x.fillStyle = "#334455"; x.fillRect(0, 0, 480, 300);
  const bx = 40 + t * 60;                 // blue: steady
  const rx = 20 + t * t * 14;             // red: accelerates, crosses ~4.3s
  x.fillStyle = "#0026ff"; x.fillRect(bx, 130, 60, 30);
  x.fillStyle = "#ff1a1a"; x.fillRect(rx, 180, 60, 30);
  requestAnimationFrame(draw);
}
draw();
</script></body></html>"""

V3D_RACE_FAIL = """<!DOCTYPE html><html><body style="margin:0;background:#123">
<canvas id="c" width="480" height="300"></canvas><script>
const x = document.getElementById("c").getContext("2d");
x.fillStyle = "#334455"; x.fillRect(0, 0, 480, 300);
x.fillStyle = "#ff1a1a"; x.fillRect(100, 150, 60, 30);  // static, red only
</script></body></html>"""

V3D_RUN_PASS = """<!DOCTYPE html><html><body style="margin:0;background:#111">
<canvas id="c" width="480" height="300"></canvas><script>
const x = document.getElementById("c").getContext("2d");
const t0 = performance.now();
function amp(t) {           // stand 2s / walk 3s / run 3s / stand 4s+
  if (t < 2) return 0; if (t < 5) return 14; if (t < 8) return 46; return 0;
}
function draw() {
  const t = (performance.now() - t0) / 1000;
  x.fillStyle = "#181818"; x.fillRect(0, 0, 480, 300);
  const a = amp(Math.min(t, 12));
  const dx = Math.sin(performance.now() / 55) * a;
  const dy = Math.cos(performance.now() / 45) * a * 0.6;
  x.fillStyle = "#e8d8b0"; x.fillRect(210 + dx, 90 + dy, 60, 120);
  requestAnimationFrame(draw);
}
draw();
</script></body></html>"""

V3D_RUN_FAIL = """<!DOCTYPE html><html><body style="margin:0;background:#111">
<canvas id="c" width="480" height="300"></canvas><script>
const x = document.getElementById("c").getContext("2d");
function draw() {           // constant max-energy jiggle, no phases
  x.fillStyle = "#181818"; x.fillRect(0, 0, 480, 300);
  const dx = performance.now() / 40;  // constant velocity, no wrap
  x.fillStyle = "#e8d8b0"; x.fillRect(210 + dx, 90, 60, 120);
  requestAnimationFrame(draw);
}
draw();
</script></body></html>"""


def run_gate(verbose=True):
    """Returns (ok: bool, summary: str). Prints a per-case line when verbose."""
    failures = []
    n = 0

    def case(name, got, want, reason=""):
        nonlocal n
        n += 1
        ok = abs(got - want) < EPS
        if verbose:
            print(f"  [{'ok ' if ok else 'FAIL'}] {name}: want {want} got {got:.4f}"
                  f"  {reason[:70]}")
        if not ok:
            failures.append(f"{name}: want {want} got {got:.4f}")

    # ---- layer 1: check-level selftest (16 canned grader cases) ----
    if verbose:
        print("golden gate — layer 1: check-level selftest")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        l1_ok = ev._selftest()
    n += 1
    if verbose:
        tail = [ln for ln in buf.getvalue().splitlines() if "self-tests" in ln]
        print(f"  [{'ok ' if l1_ok else 'FAIL'}] {tail[0].strip() if tail else ''}")
    if not l1_ok:
        failures.append("check-level selftest failed:\n" + buf.getvalue())

    # ---- layer 2: grader-level golden transcripts ----
    if verbose:
        print("golden gate — layer 2: agentic grader on golden transcripts")
    env, log, text = _ag11_perfect_env()
    s, r = ev._grade_agentic("AG-11", env, log, text, n_turns=3, turn_budget=14)
    case("AG-11 perfect transcript", s, 1.0, r)
    if "✓" not in r:
        n += 1
        failures.append("AG-11 perfect: reason has no per-check ✓ marks — "
                        "grader is not reporting per-check results")

    env, log, text = _ag11_partial_env()
    s, r = ev._grade_agentic("AG-11", env, log, text, n_turns=3, turn_budget=14)
    case("AG-11 partial transcript (1/5 checks)", s, 0.2, r)

    env, log, text = _ag11_garbage_env()
    s, r = ev._grade_agentic("AG-11", env, log, text, n_turns=1, turn_budget=14)
    case("AG-11 garbage transcript (no tools)", s, 0.0, r)
    if "✗" not in r:
        n += 1
        failures.append("AG-11 garbage: reason has no per-check ✗ marks")

    s, r = ev._grade_agentic("AG-99", _env(), [], [""], n_turns=1)
    case("unknown scenario id scores 0", s, 0.0, r)

    # ---- layer 3: end-to-end through _run_agentic with scripted models ----
    if verbose:
        print("golden gate — layer 3: harness end-to-end with scripted models")
    sc = _sc("AG-11")
    s, r, _lat, _txt, _ratio = ev._run_agentic(sc, perfect_ag11_model(), {}, 0.0, 30)
    case("harness+grader: perfect scripted model on AG-11", s, 1.0, r)

    for sid in ("AG-11", "AG-09"):
        s, r, _lat, _txt, _ratio = ev._run_agentic(_sc(sid), dead_parser_model(),
                                                   {}, 0.0, 30)
        case(f"harness+grader: dead-parser model on {sid}", s, 0.0, r)


    # ---- layer 4: v6.5 render-based visual graders (range asserts) ----
    if verbose:
        print("golden gate — layer 4: v6.5 render graders on canned fixtures")
    from visual_3d_grader import grade_race_render, grade_runner_render

    def case_range(name, got, lo, hi, reason=""):
        nonlocal n
        n += 1
        ok = lo <= got <= hi
        if verbose:
            print(f"  [{'ok ' if ok else 'FAIL'}] {name}: want [{lo},{hi}] "
                  f"got {got:.2f}  {reason[:60]}")
        if not ok:
            failures.append(f"{name}: want [{lo},{hi}] got {got:.2f} ({reason[:80]})")

    s, r = grade_race_render(V3D_RACE_PASS, render_seconds=10, fps=4.0)
    case_range("v3d race: crossing fixture passes", s, 0.85, 1.0, r)
    s, r = grade_race_render(V3D_RACE_FAIL, render_seconds=6, fps=4.0)
    case_range("v3d race: static fixture fails", s, 0.0, 0.45, r)
    s, r = grade_runner_render(V3D_RUN_PASS, render_seconds=13, fps=4.0)
    case_range("v3d runner: phased fixture passes", s, 0.85, 1.0, r)
    s, r = grade_runner_render(V3D_RUN_FAIL, render_seconds=13, fps=4.0)
    case_range("v3d runner: constant-motion fixture fails", s, 0.0, 0.6, r)


    ok = not failures
    summary = (f"golden gate {'PASSED' if ok else 'FAILED'}: "
               f"{n - len(failures)}/{n} cases")
    if verbose:
        print(f"  => {summary}")
        for f in failures:
            print(f"     FAIL {f}")
    return ok, summary


# --------------------------------------------------------------------------- #
# --prove : sabotage the grader in-memory, assert the gate catches it
# --------------------------------------------------------------------------- #
def prove_gate_catches_sabotage():
    """Meta-test: each historical disaster, injected, must FAIL the gate."""
    results = []

    # sabotage 1: the v6.1 auto-pass bug — grader always returns full marks
    real = ev._grade_agentic
    ev._grade_agentic = lambda *a, **k: (1.0, "agentic 6/6: all passed")
    try:
        ok, _ = run_gate(verbose=False)
    finally:
        ev._grade_agentic = real
    results.append(("auto-pass grader (v6.1 bug class)", not ok))

    # sabotage 2: grader that scores presence of ANY text as success
    ev._grade_agentic = lambda sid, env, log, text, n_turns, turn_budget=15: \
        (1.0 if any(text) else 0.0, "text present")
    try:
        ok, _ = run_gate(verbose=False)
    finally:
        ev._grade_agentic = real
    results.append(("text-presence grader", not ok))

    # sabotage 3: tool-call assembly silently broken (dead parser INSIDE the
    # harness) — assemble_tool_calls returns nothing
    real_asm = ev.assemble_tool_calls
    ev.assemble_tool_calls = lambda resp: []
    try:
        ok, _ = run_gate(verbose=False)
    finally:
        ev.assemble_tool_calls = real_asm
    results.append(("broken tool-call assembly (v5 parser bug class)", not ok))

    # sabotage 4: turn-budget penalty accidentally dropped
    real2 = ev._grade_agentic

    def no_partial(sid, env, log, text, n_turns, turn_budget=15):
        s, r = real2(sid, env, log, text, n_turns, turn_budget)
        return (1.0 if s > 0 else 0.0), r  # rounds partial credit up
    ev._grade_agentic = no_partial
    try:
        ok, _ = run_gate(verbose=False)
    finally:
        ev._grade_agentic = real2
    results.append(("partial credit rounded up to full", not ok))

    print("prove mode — the gate must FAIL under each sabotage:")
    all_ok = True
    for name, caught in results:
        print(f"  [{'ok ' if caught else 'MISS'}] gate catches: {name}")
        all_ok &= caught
    # and with no sabotage it must PASS
    ok, _ = run_gate(verbose=False)
    print(f"  [{'ok ' if ok else 'MISS'}] gate passes on the real grader")
    all_ok &= ok
    print(f"  => prove mode {'PASSED' if all_ok else 'FAILED'}")
    return all_ok


if __name__ == "__main__":
    if "--prove" in sys.argv:
        sys.exit(0 if prove_gate_catches_sabotage() else 1)
    ok, _ = run_gate(verbose=True)
    sys.exit(0 if ok else 1)
