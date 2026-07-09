#!/usr/bin/env python3
"""category_probe.py — single-stream decode tok/s by workload category.

Mirrors AEON-7's DFlash benchmark categories (math/reasoning, code, prose,
extraction/JSON) so MTP vs DFlash can be compared per-workload, not on one
fixed filler prompt. Reuses spark_bench.chat_stream for identical timing.

Emits one CSV-ish line per (category) to stdout and a JSON summary to --out.
Acceptance length is NOT measured here (it lives in vLLM SpecDecoding logs);
the driver greps those separately.
"""
import argparse, json, statistics, sys
from spark_bench import chat_stream

CATEGORIES = {
    "math": ("Solve step by step, showing all work: A train leaves city A at 60 mph. "
             "Two hours later a second train leaves the same station at 90 mph on the same "
             "track. Derive the time and distance at which the second train catches the first, "
             "then generalize to speeds v1, v2 and head start t0, and prove your general formula. "
             "Then compute three more worked examples with different numbers."),
    "code": ("Write a complete, production-quality Python module implementing an LRU cache with "
             "TTL expiry: a class with get/set/delete, O(1) operations using a doubly linked list "
             "plus dict, thread safety via a lock, and a full docstring. Include a __main__ block "
             "with a self-test covering eviction, expiry, and concurrency. Explain each design choice."),
    "prose": ("Write a flowing ~500 word essay on how unified-memory edge AI workstations change "
              "the economics of local model serving compared to cloud GPUs. Natural prose, no lists, "
              "no headings, varied sentence structure."),
    "extraction": ("Return ONLY valid JSON, no prose. Extract structured data from this text into an "
                   "array of objects with keys name, role, org, year_joined, skills (array): "
                   "'Ada Lovelace, lead analyst at Analytical Engines, joined 1843, skilled in "
                   "mathematics, algorithms, and note-taking. Charles Babbage, founder at Analytical "
                   "Engines since 1837, expert in mechanical design and computation. Grace Hopper, "
                   "compiler architect at Naval Systems, year 1952, knows COBOL, linking, and debugging.' "
                   "Produce 6 objects by inventing 3 more plausible historical entries."),
}


def measure(endpoint, model, cat, prompt, max_tokens, reps, warmup, timeout):
    # warmup (discard)
    for _ in range(warmup):
        chat_stream(endpoint, model, [{"role": "user", "content": prompt}],
                    max_tokens=max_tokens, timeout=timeout)
    tps, outs = [], []
    for _ in range(reps):
        r = chat_stream(endpoint, model, [{"role": "user", "content": prompt}],
                        max_tokens=max_tokens, timeout=timeout)
        tps.append(r["decode_tps"]); outs.append(r["completion_tokens"] or 0)
    return {"category": cat, "decode_tps_med": round(statistics.median(tps), 1),
            "decode_tps_all": [round(x, 1) for x in tps],
            "out_tokens_med": int(statistics.median(outs))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for cat, prompt in CATEGORIES.items():
        r = measure(a.endpoint, a.model, cat, prompt, a.max_tokens, a.reps, a.warmup, a.timeout)
        rows.append(r)
        print(f"[{a.label}] {cat:11s} decode_tps_med={r['decode_tps_med']:6.1f} "
              f"out={r['out_tokens_med']} all={r['decode_tps_all']}", flush=True)
    summary = {"label": a.label, "endpoint": a.endpoint, "model": a.model, "rows": rows}
    with open(a.out, "w") as f:
        json.dump(summary, f, indent=2)
    avg = round(statistics.mean(r["decode_tps_med"] for r in rows), 1)
    print(f"[{a.label}] AVG decode_tps_med={avg}", flush=True)


if __name__ == "__main__":
    main()
