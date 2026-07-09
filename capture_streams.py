#!/usr/bin/env python3
"""capture_streams.py — fire N concurrent streaming completions, record real per-token arrival times.

Output JSON drives the demo animation (honest replay of measured timings). Every token carries
its wall-clock offset from the shared start, so the animation reproduces true concurrency + tok/s.
"""
import argparse, json, time, threading, urllib.request

PROMPTS = [
    "Explain how speculative decoding accelerates LLM inference, in detail.",
    "Write a Python class for an LRU cache with TTL. Full implementation.",
    "Describe the GB10 Grace-Blackwell architecture and why unified memory matters.",
    "Solve: a train leaves at 60mph, another 2h later at 90mph. When do they meet? Show all work and generalize.",
    "Write a flowing essay on edge AI workstations vs cloud GPUs.",
    "Return valid JSON extracting people, roles, and orgs from a paragraph about computing pioneers.",
    "Explain MoE routing and how active vs total parameters differ.",
    "Write a merge-intervals function in Python with a self-test and complexity analysis.",
    "Summarize the tradeoffs between NVFP4, FP8, and Q4_K_M quantization.",
    "Describe how MTP draft heads work and why they beat external drafters on bandwidth-bound hardware.",
    "Plan a 4-node DGX Spark deployment checklist: network, containers, cache, smoke test, rollback.",
    "Explain flash attention and why it reduces memory traffic.",
    "Write a short story about a compact AI workstation that dreams in tokens.",
    "Compare tensor parallelism and pipeline parallelism for MoE serving.",
    "Explain KV-cache quantization and its effect on long-context throughput.",
    "Describe block-diffusion drafting and where it wins over autoregressive drafting.",
]


def stream_one(idx, endpoint, model, prompt, max_tokens, timeout, out, start_evt, t0_holder):
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.7, "top_p": 0.95,
        "stream": True, "stream_options": {"include_usage": True},
        "chat_template_kwargs": {"enable_thinking": False},
        "ignore_eos": True, "min_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer none"})
    start_evt.wait()
    t0 = t0_holder[0]
    events = []          # wall-clock offset of each SSE content event (decode step)
    completion_tokens = 0  # ground-truth token count from usage
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            for raw in r:
                line = raw.decode("utf-8", "ignore").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    d = json.loads(data)
                    u = d.get("usage")
                    if u and u.get("completion_tokens"):
                        completion_tokens = u["completion_tokens"]
                    ch = d.get("choices") or []
                    if ch:
                        delta = ch[0].get("delta") or {}
                        if delta.get("content") or delta.get("reasoning_content"):
                            events.append(round(time.perf_counter() - t0, 4))
                except Exception:
                    continue
    except Exception as e:
        out[idx] = {"stream": idx, "events": events, "completion_tokens": completion_tokens, "error": str(e)[:120]}
        return
    out[idx] = {"stream": idx, "events": events, "n_events": len(events),
                "completion_tokens": completion_tokens}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    out = [None] * a.n
    start_evt = threading.Event()
    t0_holder = [0.0]
    threads = []
    for i in range(a.n):
        t = threading.Thread(target=stream_one, args=(i, a.endpoint, a.model, PROMPTS[i % len(PROMPTS)],
                                                       a.max_tokens, a.timeout, out, start_evt, t0_holder))
        t.start(); threads.append(t)
    time.sleep(0.5)
    t0_holder[0] = time.perf_counter()
    start_evt.set()
    for t in threads:
        t.join()

    total_tokens = sum((s.get("completion_tokens") or 0) for s in out if s)
    total_events = sum(len(s.get("events", [])) for s in out if s)
    wall = max((s["events"][-1] for s in out if s and s.get("events")), default=0)
    agg_tokens = round(total_tokens / wall, 1) if wall else 0
    agg_events = round(total_events / wall, 1) if wall else 0
    summary = {"n_streams": a.n, "model": a.model, "endpoint": a.endpoint,
               "total_tokens": total_tokens, "total_events": total_events,
               "wall_s": round(wall, 2),
               "aggregate_tps": agg_tokens, "aggregate_events_per_s": agg_events,
               "mean_accept_len": round(total_tokens / total_events, 2) if total_events else 0,
               "streams": out}
    with open(a.out, "w") as f:
        json.dump(summary, f)
    print(f"captured n={a.n} total_tokens={total_tokens} wall={wall:.1f}s aggregate={agg} tok/s -> {a.out}")


if __name__ == "__main__":
    main()
