#!/usr/bin/env python3
"""
spark-bench: parameterized benchmark harness for the DGX Spark cluster.

Three tiers, one comparable CSV (long format) + markdown and HTML report per run:
  Tier 1  interconnect : ib_write_bw / ib_read_bw per RoCE link (nccl-tests if present)
  Tier 2  inference    : TTFT, TPOT/inter-token latency, single-stream tok/s,
                         prefill tok/s, context sweep, throughput under concurrency
  Tier 3  real-workload: coding prompt, tool-call prompt, long-context retrieval (E2E)

All inference talks to OpenAI-compatible endpoints (vLLM, llama.cpp) over plain
urllib streaming, so the SAME harness compares both backends. Token counts come
from server-reported usage (stream_options.include_usage) for accuracy.

Run dimensions (recorded on every row for cross-run comparison):
  model, endpoint, label, parallelism, topology, context, batch, spec_decode

Examples:
  # Tier 2 single-stream + context sweep against DeepSeek V4 Flash (2-node direct 200G)
  ./spark_bench.py tier2 --label dseek-2node --endpoint http://10.0.0.29:8000/v1 \
      --model deepseek-v4-flash --topology direct-200g --parallelism PP2 \
      --contexts 4096,32768,131072 --concurrency 1,4,16

  # Tier 3 real workloads against Qwopus MTP (llama.cpp)
  ./spark_bench.py tier3 --label qwopus-mtp --endpoint http://10.0.0.120:8080/v1 \
      --model Qwopus3.6-27B-v2-MTP-Q4_K_M.gguf --spec-decode mtp-on --topology single

  # Tier 1 RoCE interconnect, 9f73 <-> 78f1 direct links
  ./spark_bench.py tier1 --label link-9f73-78f1 --topology direct-200g \
      --peer-ssh 10.0.0.29 --links rocep1s0f0:192.168.2.2,roceP2p1s0f0:192.168.3.2

  # Everything (tier2+tier3) in one shot
  ./spark_bench.py all --label dseek-2node --endpoint http://10.0.0.29:8000/v1 \
      --model deepseek-v4-flash --topology direct-200g --parallelism PP2 \
      --contexts 4096,32768 --concurrency 1,8
"""
import argparse, csv, json, os, re, statistics, subprocess, sys, threading, time, urllib.request, uuid, zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional
from html_report import infer_run_kind, write_run_report

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "results")
CSV_FIELDS = ["run_id", "timestamp", "tier", "model", "label", "endpoint", "topology",
              "parallelism", "context", "batch", "spec_decode", "workload",
              "metric", "value", "unit", "notes"]


# --------------------------------------------------------------------------- #
# Run context / output
# --------------------------------------------------------------------------- #
@dataclass
class Ctx:
    label: str
    model: str = ""
    endpoint: str = ""
    topology: str = "unknown"
    parallelism: str = "1"
    spec_decode: str = "na"
    out_dir: str = DEFAULT_OUT
    run_kind: str = "benchmark"
    notes: str = ""
    run_id: str = ""
    rows: list = field(default_factory=list)
    md: list = field(default_factory=list)

    def __post_init__(self):
        if not self.run_id:
            ts = time.strftime("%Y%m%d-%H%M%S")
            self.run_id = f"{self.label}-{ts}"
        if self.run_kind == "auto":
            self.run_kind = infer_run_kind(self.label)
        os.makedirs(os.path.join(self.out_dir, "runs"), exist_ok=True)

    def add(self, tier, workload, metric, value, unit, *, context="", batch="", notes=""):
        row = {
            "run_id": self.run_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tier": tier, "model": self.model, "label": self.label, "endpoint": self.endpoint,
            "topology": self.topology, "parallelism": self.parallelism, "context": context,
            "batch": batch, "spec_decode": self.spec_decode, "workload": workload,
            "metric": metric, "value": value, "unit": unit, "notes": notes,
        }
        self.rows.append(row)
        v = f"{value:.2f}" if isinstance(value, float) else value
        print(f"  [{tier}] {workload:<22} {metric:<22} = {v} {unit}"
              + (f"  ({notes})" if notes else ""))

    def mdln(self, line=""):
        self.md.append(line)

    def flush(self):
        csv_path = os.path.join(self.out_dir, "spark_bench.csv")
        new = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            if new:
                w.writeheader()
            for r in self.rows:
                w.writerow(r)
        md_path = os.path.join(self.out_dir, "runs", f"{self.run_id}.md")
        with open(md_path, "w") as f:
            f.write("\n".join(self.md) + "\n")
        html_path = os.path.join(self.out_dir, "runs", f"{self.run_id}.html")
        html_path, latest_path = write_run_report(self, html_path)
        print(f"\n  -> appended {len(self.rows)} rows to {csv_path}")
        print(f"  -> wrote summary {md_path}")
        print(f"  -> wrote html report {html_path}")
        print(f"  -> updated latest report {latest_path}")
        return csv_path, md_path, html_path


# --------------------------------------------------------------------------- #
# OpenAI-compatible streaming client
# --------------------------------------------------------------------------- #
def _is_single_char_runaway(text_tail, window_chars):
    """Return True when the complete rolling window is one repeated character."""
    if window_chars <= 0 or len(text_tail) < window_chars:
        return False
    return len(set(text_tail[-window_chars:])) == 1


def _is_repeated_phrase_runaway(text_tail, window_chars, max_compressed_ratio=0.08):
    """Detect an extremely repetitive phrase loop in a complete rolling window."""
    if window_chars <= 0 or len(text_tail) < window_chars:
        return False
    sample = text_tail[-window_chars:].encode("utf-8", "replace")
    if not sample:
        return False
    return len(zlib.compress(sample, 9)) / len(sample) <= max_compressed_ratio


def _abort_sglang_request(endpoint, rid):
    """Best-effort abort for an SGLang request with a caller-supplied rid."""
    base = endpoint.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    payload = json.dumps({"rid": rid, "abort_all": False}).encode()
    req = urllib.request.Request(
        base + "/abort_request", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


def chat_stream(endpoint, model, messages, max_tokens, *, temperature=0.0,
                tools=None, timeout: Optional[float] = 600, extra=None):
    """One streaming chat completion. Returns dict with timing + usage + text."""
    body = {"model": model, "messages": messages, "temperature": temperature,
            "stream": True, "stream_options": {"include_usage": True}}
    # Reasoning models consume max_tokens across hidden reasoning + visible answer.
    # None means intentionally omit the field and let the endpoint use its full
    # remaining context window; numeric values preserve the historical contract.
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    if extra:
        body.update(extra)
    url = endpoint.rstrip("/") + "/chat/completions"
    import os
    # --- strict-API guard (env-gated; no effect on existing runs unless set) ---
    # Adaptive-thinking API models (e.g. Fable 5 / claude-fable-5) reject sampling
    # params (temperature/top_p/top_k -> HTTP 400) and take reasoning depth via an
    # `effort` field instead. Set these two envs only for such endpoints.
    if os.environ.get("SPARK_BENCH_OMIT_SAMPLING"):
        for _k in ("temperature", "top_p", "top_k"):
            body.pop(_k, None)
    _eff = os.environ.get("SPARK_BENCH_REASONING_EFFORT")
    if _eff:
        body["reasoning"] = {"effort": _eff}
    # --- cross-engine sampling parity (env-gated; Fable review 2026-07-03) ---
    # Engines diverge on top_p/top_k defaults (vLLM adopts generation_config.json,
    # SGLang/Atlas do not). Pin them explicitly for engine-comparison runs:
    #   SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'
    _extra_body = os.environ.get("SPARK_BENCH_EXTRA_BODY")
    if _extra_body:
        body.update(json.loads(_extra_body))
    # Opt-in SGLang safety valve for proven low-entropy model failures. It does
    # not cap normal output: only a full window of one identical visible
    # character triggers an abort and a model-failure finish reason.
    _runaway_window = int(os.environ.get("SPARK_BENCH_RUNAWAY_CHAR_WINDOW", "0") or 0)
    _phrase_window = int(os.environ.get("SPARK_BENCH_RUNAWAY_PHRASE_WINDOW", "0") or 0)
    _abort_backend = os.environ.get("SPARK_BENCH_RUNAWAY_ABORT_BACKEND", "sglang")
    _request_rid = None
    if (_runaway_window > 0 or _phrase_window > 0) and _abort_backend == "sglang":
        _request_rid = str(body.get("rid") or uuid.uuid4().hex)
        body["rid"] = _request_rid
    # ---------------------------------------------------------------------------
    _api_key = (os.environ.get("SPARK_BENCH_API_KEY")
                or os.environ.get("OPENROUTER_API_KEY")
                or os.environ.get("OPENAI_API_KEY")
                or "none")
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {_api_key}"}
    if "openrouter.ai" in endpoint:
        headers["HTTP-Referer"] = os.environ.get("OPENROUTER_HTTP_REFERER",
                                                  "https://wesche.com/dgx")
        headers["X-Title"] = os.environ.get("OPENROUTER_X_TITLE", "spark-bench")
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=headers)
    t0 = time.perf_counter()
    ttft = None
    text_parts = []
    reasoning_parts = []
    tool_calls = []
    usage = {}
    finish = None
    runaway = None
    runaway_tail = ""
    stop_stream = False
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line or not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue
            if obj.get("usage"):
                usage = obj["usage"]
            for ch in obj.get("choices", []):
                delta = ch.get("delta", {})
                # reasoning models (DeepSeek) stream reasoning tokens before content
                # under either `reasoning` or `reasoning_content`; the first token of
                # EITHER is the true TTFT and those tokens count as decode.
                rc = delta.get("reasoning") or delta.get("reasoning_content")
                if rc:
                    if ttft is None:
                        ttft = time.perf_counter() - t0
                    reasoning_parts.append(rc)
                if delta.get("content"):
                    if ttft is None:
                        ttft = time.perf_counter() - t0
                    content = delta["content"]
                    text_parts.append(content)
                    if _runaway_window > 0 or _phrase_window > 0:
                        tail_window = max(_runaway_window, _phrase_window)
                        runaway_tail = (runaway_tail + content)[-tail_window:]
                        runaway_kind = None
                        runaway_window = None
                        if _is_single_char_runaway(runaway_tail, _runaway_window):
                            runaway_kind = "single_character"
                            runaway_window = _runaway_window
                        elif _is_repeated_phrase_runaway(runaway_tail, _phrase_window):
                            runaway_kind = "repeated_phrase"
                            runaway_window = _phrase_window
                        if runaway_kind:
                            runaway = {
                                "kind": runaway_kind,
                                "character": runaway_tail[-1],
                                "window_chars": runaway_window,
                                "observed_text_chars": sum(len(x) for x in text_parts),
                                "request_rid": _request_rid,
                                "abort_backend": _abort_backend,
                            }
                            finish = "runaway"
                            runaway["abort_sent"] = (
                                _abort_sglang_request(endpoint, _request_rid)
                                if _abort_backend == "sglang" else False)
                            stop_stream = True
                            break
                if delta.get("tool_calls"):
                    if ttft is None:
                        ttft = time.perf_counter() - t0
                    tool_calls.extend(delta["tool_calls"])
                if ch.get("finish_reason"):
                    finish = ch["finish_reason"]
            if stop_stream:
                break
    total = time.perf_counter() - t0
    comp = usage.get("completion_tokens")
    prompt_toks = usage.get("prompt_tokens")
    text = "".join(text_parts)
    if comp is None and runaway is not None:
        # A deliberately aborted stream has no final native usage packet. Keep
        # the token count unavailable instead of calling a character estimate
        # a token count.
        comp = 0
    elif comp is None:  # llama.cpp sometimes omits usage on tool calls
        comp = max(1, len(text) // 4)
    decode_t = max(total - (ttft or total), 1e-6)
    # --- raw request/response provenance dump (env-gated; Fable review 2026-07-03)
    # Set SPARK_BENCH_DUMP_DIR to append every request+response as JSONL so any
    # disputed score can be re-scored offline (rescore_v61.py) for ALL engines.
    _dump_dir = os.environ.get("SPARK_BENCH_DUMP_DIR")
    if _dump_dir:
        try:
            with open(os.path.join(_dump_dir, "raw_dump.jsonl"), "a") as _df:
                _df.write(json.dumps({
                    "ts": time.time(), "endpoint": url, "request": body,
                    "text": text, "reasoning": "".join(reasoning_parts),
                    "tool_calls": tool_calls, "finish": finish, "usage": usage,
                    "runaway": runaway,
                    "ttft": ttft, "total": total}, ensure_ascii=False) + "\n")
        except OSError:
            pass  # provenance must never break a run
    return {
        "ttft": ttft if ttft is not None else total,
        "total": total,
        "decode_s": decode_t,
        "prompt_tokens": prompt_toks,
        "completion_tokens": comp,
        "decode_tps": comp / decode_t if comp else 0.0,
        "tpot_ms": (decode_t / max(comp - 1, 1)) * 1000 if comp > 1 else 0.0,
        "text": text,
        "reasoning": "".join(reasoning_parts),
        "tool_calls": tool_calls,
        "finish": finish,
        "runaway": runaway,
        "request_rid": _request_rid,
    }


# --------------------------------------------------------------------------- #
# Tier 1 : interconnect
# --------------------------------------------------------------------------- #
def _parse_ib_bw(stdout):
    """Pull peak BW (Gb/sec) and MsgRate from ib_*_bw table output."""
    best_bw, best_mr = 0.0, 0.0
    for ln in stdout.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", ln)
        if m:
            bw = float(m.group(4))      # BW peak[Gb/sec] column (avg is group 4 typically)
            mr = float(m.group(5))
            best_bw = max(best_bw, bw)
            best_mr = max(best_mr, mr)
    return best_bw, best_mr


def run_tier1(ctx, args):
    ctx.mdln(f"# Tier 1 — Interconnect ({ctx.run_id})\n")
    ctx.mdln(f"- topology: `{ctx.topology}`  peer-ssh: `{args.peer_ssh}`\n")
    links = []
    for spec in args.links.split(","):
        spec = spec.strip()
        if not spec:
            continue
        dev, peer_ip = spec.split(":")
        links.append((dev, peer_ip))

    if not _which("ib_write_bw"):
        ctx.add("tier1", "tooling", "ib_write_bw", "MISSING", "", notes="install perftest")
    if not _which("all_reduce_perf"):
        ctx.add("tier1", "tooling", "nccl-tests", "MISSING", "", notes="TODO install nccl-tests")
        ctx.mdln("> **TODO:** `nccl-tests` not installed — all_reduce/all_gather/sendrecv "
                 "collectives deferred. RoCE point-to-point bandwidth measured below.\n")

    ctx.mdln("| link | dir | test | BW peak (Gb/s) | MsgRate (Mpps) |")
    ctx.mdln("|------|-----|------|---------------:|---------------:|")
    for dev, peer_ip in links:
        for test in ("ib_write_bw", "ib_read_bw"):
            if not _which(test):
                continue
            bw, mr = _ib_test(args.peer_ssh, dev, peer_ip, test, args.gid, args.ib_size,
                              args.ib_dur, qp=args.ib_qp, mtu=args.ib_mtu)
            direction = "write" if "write" in test else "read"
            note = f"{dev}<->{peer_ip} gid{args.gid}"
            if bw <= 0:
                ctx.add("tier1", f"{dev}", f"{test}", "FAILED", "Gb/s", notes=note)
                ctx.mdln(f"| `{dev}` | {direction} | {test} | FAILED | - |")
            else:
                ctx.add("tier1", f"{dev}", f"{test}_avg", round(bw, 1), "Gb/s", notes=note)
                ctx.add("tier1", f"{dev}", f"{test}_msgrate", round(mr, 4), "Mpps", notes=note)
                ctx.mdln(f"| `{dev}` | {direction} | {test} | {bw:.1f} | {mr:.2f} |")
    ctx.mdln()


def _ib_test(peer_ssh, dev, peer_ip, test, gid, size, dur, qp=4, mtu=4096):
    """Start ib server on peer over ssh, run client locally. Returns (bw_gbps, msgrate).

    NOTE: pkill MUST be `-x {test}` (exact binary), never `-f` — `-f` matches the
    remote ssh shell's own argv (which contains the test name) and kills it (ssh 255).
    """
    flags = ["-d", dev, "-x", str(gid), "-F", "--report_gbits",
             "-m", str(mtu), "-q", str(qp), "-s", str(size), "-D", str(dur)]
    srv_cmd = f"pkill -9 -x {test}; sleep 0.4; {test} " + " ".join(flags)
    cli_args = [test] + flags + [peer_ip]
    srv = subprocess.Popen(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=6", peer_ssh, srv_cmd],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3.5)
    try:
        out = subprocess.run(cli_args, capture_output=True, text=True,
                             timeout=dur + 25).stdout
    except subprocess.TimeoutExpired:
        out = ""
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except subprocess.TimeoutExpired:
            srv.kill()
    return _parse_ib_bw(out)


# --------------------------------------------------------------------------- #
# Tier 2 : inference
# --------------------------------------------------------------------------- #
FILLER = ("The DGX Spark is a compact AI workstation built around the GB10 "
          "Grace-Blackwell superchip with unified LPDDR5X memory. ")


def _make_prompt(approx_tokens):
    """Build a prompt of roughly approx_tokens (≈4 chars/token)."""
    target_chars = int(approx_tokens * 4)
    reps = max(1, target_chars // len(FILLER))
    return FILLER * reps


def run_tier2(ctx, args, *, title=None, heading_level=1):
    h1 = "#" * heading_level
    h2 = "#" * min(heading_level + 1, 6)
    title = title or f"Tier 2 — Inference ({ctx.run_id})"
    ctx.mdln(f"{h1} {title}\n")
    ctx.mdln(f"- model `{ctx.model}` @ `{ctx.endpoint}`  topology `{ctx.topology}` "
             f"parallelism `{ctx.parallelism}` spec_decode `{ctx.spec_decode}`\n")

    # ---- single-stream decode (short prompt, long generation) ----
    ctx.mdln(f"{h2} Single-stream decode\n")
    ctx.mdln("| context | TTFT (ms) | decode tok/s | TPOT (ms) | prefill tok/s | out toks |")
    ctx.mdln("|--------:|----------:|-------------:|----------:|--------------:|---------:|")
    contexts = [int(c) for c in args.contexts.split(",") if c.strip()]
    for cxt in contexts:
        prompt = _make_prompt(cxt) + ("\n\nNow write a detailed ~400 word essay on how "
                                      "speculative decoding accelerates LLM inference.")
        try:
            r = chat_stream(ctx.endpoint, ctx.model,
                            [{"role": "user", "content": prompt}],
                            max_tokens=args.gen_tokens, timeout=args.timeout)
        except Exception as e:
            ctx.add("tier2", "single_stream", "error", str(e)[:60], "", context=cxt)
            ctx.mdln(f"| {cxt} | ERR | - | - | - | - |")
            continue
        ptoks = r["prompt_tokens"] or cxt
        prefill_tps = ptoks / r["ttft"] if r["ttft"] else 0.0
        ctx.add("tier2", "single_stream", "ttft_ms", round(r["ttft"] * 1000, 1), "ms",
                context=ptoks)
        ctx.add("tier2", "single_stream", "decode_tps", round(r["decode_tps"], 2),
                "tok/s", context=ptoks)
        ctx.add("tier2", "single_stream", "tpot_ms", round(r["tpot_ms"], 2), "ms",
                context=ptoks)
        ctx.add("tier2", "single_stream", "prefill_tps", round(prefill_tps, 1),
                "tok/s", context=ptoks, notes=f"prompt={ptoks}tok")
        ctx.add("tier2", "single_stream", "output_tokens", r["completion_tokens"],
                "tok", context=ptoks)
        ctx.mdln(f"| {ptoks} | {r['ttft']*1000:.0f} | {r['decode_tps']:.1f} | "
                 f"{r['tpot_ms']:.1f} | {prefill_tps:.0f} | {r['completion_tokens']} |")
    ctx.mdln()

    # ---- throughput under concurrency ----
    concs = [int(c) for c in args.concurrency.split(",") if c.strip()]
    if concs:
        ctx.mdln(f"{h2} Throughput under concurrency\n")
        ctx.mdln("| batch | agg decode tok/s | per-stream tok/s | TTFT p50 (ms) | "
                 "TTFT p99 (ms) | completed |")
        ctx.mdln("|------:|-----------------:|-----------------:|--------------:|"
                 "--------------:|----------:|")
        cprompt = _make_prompt(args.conc_context) + ("\n\nExplain in ~300 words how "
                                                     "tensor parallelism shards a transformer.")
        for n in concs:
            agg = _concurrency_run(ctx.endpoint, ctx.model, cprompt, args.gen_tokens,
                                   n, args.timeout)
            if not agg["ok"]:
                ctx.add("tier2", "concurrency", "error", "no completed requests", "",
                        batch=n)
                ctx.mdln(f"| {n} | ERR | - | - | - | 0 |")
                continue
            ctx.add("tier2", "concurrency", "agg_decode_tps", round(agg["agg_tps"], 1),
                    "tok/s", batch=n)
            ctx.add("tier2", "concurrency", "per_stream_tps", round(agg["per_tps"], 2),
                    "tok/s", batch=n)
            ctx.add("tier2", "concurrency", "ttft_p50_ms", round(agg["ttft_p50"], 1),
                    "ms", batch=n)
            ctx.add("tier2", "concurrency", "ttft_p99_ms", round(agg["ttft_p99"], 1),
                    "ms", batch=n)
            ctx.mdln(f"| {n} | {agg['agg_tps']:.0f} | {agg['per_tps']:.1f} | "
                     f"{agg['ttft_p50']:.0f} | {agg['ttft_p99']:.0f} | {agg['done']}/{n} |")
        ctx.mdln()


def _concurrency_run(endpoint, model, prompt, max_tokens, n, timeout):
    results = []
    t0 = time.perf_counter()

    def worker(_):
        return chat_stream(endpoint, model, [{"role": "user", "content": prompt}],
                           max_tokens=max_tokens, timeout=timeout)
    with ThreadPoolExecutor(max_workers=n) as ex:
        futs = [ex.submit(worker, i) for i in range(n)]
        for f in as_completed(futs):
            try:
                results.append(f.result())
            except Exception:
                pass
    wall = time.perf_counter() - t0
    if not results:
        return {"ok": False}
    total_out = sum(r["completion_tokens"] for r in results)
    ttfts = sorted(r["ttft"] * 1000 for r in results)
    per = statistics.mean(r["decode_tps"] for r in results)
    return {
        "ok": True, "done": len(results),
        "agg_tps": total_out / wall,
        "per_tps": per,
        "ttft_p50": _pct(ttfts, 50),
        "ttft_p99": _pct(ttfts, 99),
    }


def _pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = max(0, min(len(sorted_vals) - 1, int(round((p / 100) * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


# --------------------------------------------------------------------------- #
# Tier 3 : real workloads
# --------------------------------------------------------------------------- #
CODING_PROMPT = ("Write a Python function `merge_intervals(intervals)` that merges a list "
                 "of [start,end] pairs into sorted non-overlapping intervals, handling "
                 "empty input. Then add exactly two assert-based tests. Output ONLY one "
                 "python code block.")

TOOL_PROMPT = "What is the current weather in Paris, France? Use the available tool."
WEATHER_TOOL = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
        },
    },
}]


def run_tier3(ctx, args):
    ctx.mdln(f"# Tier 3 — Real workloads ({ctx.run_id})\n")
    ctx.mdln(f"- model `{ctx.model}` @ `{ctx.endpoint}`  spec_decode `{ctx.spec_decode}`\n")
    ctx.mdln("| workload | pass | E2E (s) | TTFT (ms) | decode tok/s | out toks | notes |")
    ctx.mdln("|----------|:----:|--------:|----------:|-------------:|---------:|-------|")

    # --- coding ---
    r = chat_stream(ctx.endpoint, ctx.model, [{"role": "user", "content": CODING_PROMPT}],
                    max_tokens=2048, timeout=args.timeout)
    ok = _check_code(r["text"])
    _tier3_emit(ctx, "coding", ok, r, note="merge_intervals exec")

    # --- tool call ---
    try:
        r = chat_stream(ctx.endpoint, ctx.model, [{"role": "user", "content": TOOL_PROMPT}],
                        max_tokens=512, timeout=args.timeout, tools=WEATHER_TOOL)
        called = any((tc.get("function", {}) or {}).get("name") == "get_weather"
                     for tc in r["tool_calls"]) or "get_weather" in r["text"]
        note = "tool_calls" if r["tool_calls"] else ("inline" if called else "no call")
        _tier3_emit(ctx, "tool_call", called, r, note=note)
    except Exception as e:
        ctx.add("tier3", "tool_call", "error", str(e)[:50], "")
        ctx.mdln(f"| tool_call | ERR | - | - | - | - | {str(e)[:30]} |")

    # --- long-context retrieval (needle) ---
    needle_ctx = args.retrieval_context
    passcode = "ZARQON-7741-MERIDIAN"
    haystack = _build_haystack(needle_ctx, passcode, depth=0.55)
    q = (haystack + "\n\nQUESTION: What is the secret passcode mentioned above? "
         "Reply with ONLY the passcode.")
    try:
        r = chat_stream(ctx.endpoint, ctx.model, [{"role": "user", "content": q}],
                        max_tokens=256, timeout=args.timeout)
        ok = passcode in (r["text"] + " " + r["reasoning"]).upper()
        ptoks = r["prompt_tokens"] or needle_ctx
        _tier3_emit(ctx, "long_ctx_retrieval", ok, r, note=f"~{ptoks}tok ctx, depth55%")
    except Exception as e:
        ctx.add("tier3", "long_ctx_retrieval", "error", str(e)[:50], "")
        ctx.mdln(f"| long_ctx_retrieval | ERR | - | - | - | - | {str(e)[:30]} |")
    ctx.mdln()


def _tier3_emit(ctx, name, ok, r, note=""):
    ctx.add("tier3", name, "pass", 1 if ok else 0, "bool", notes=note)
    ctx.add("tier3", name, "e2e_s", round(r["total"], 2), "s")
    ctx.add("tier3", name, "ttft_ms", round(r["ttft"] * 1000, 1), "ms")
    ctx.add("tier3", name, "decode_tps", round(r["decode_tps"], 2), "tok/s")
    ctx.add("tier3", name, "output_tokens", r["completion_tokens"], "tok")
    ctx.mdln(f"| {name} | {'✅' if ok else '❌'} | {r['total']:.1f} | {r['ttft']*1000:.0f} | "
             f"{r['decode_tps']:.1f} | {r['completion_tokens']} | {note} |")


def _check_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    code = m.group(1) if m else text
    if "def merge_intervals" not in code:
        return False
    try:
        ns = {}
        exec(code, ns)
        f = ns.get("merge_intervals")
        return f([[1, 3], [2, 6], [8, 10]]) == [[1, 6], [8, 10]] and f([]) == []
    except Exception:
        return False


def _build_haystack(approx_tokens, passcode, depth=0.5):
    line = ("In the quarterly review, the operations team noted that throughput remained "
            "stable across all regional clusters during the maintenance window. ")
    target_chars = int(approx_tokens * 4)
    n = max(2, target_chars // len(line))
    lines = [line] * n
    insert = int(n * depth)
    lines[insert] = f"IMPORTANT: the secret passcode is {passcode}. Remember it. "
    return "".join(lines)


# --------------------------------------------------------------------------- #
# Integrity gates (added 2026-07-04 after the v5 parser and v6.1 auto-pass
# grader incidents). Order per eval run:
#   1. golden gate  — grader must reproduce known scores on canned transcripts
#   2. provenance   — grader git hash stamped on the run; dirty tree refuses
#   3. box lock     — one eval per endpoint box, enforced by lockfile
#   4. preflight    — endpoint serves the REQUESTED model and its tool-call
#                     parsing actually works, else abort (never record zeros)
#   5. run marker   — .STARTED heartbeat file so watchers verify from disk,
#                     never from pgrep
# --------------------------------------------------------------------------- #
GRADER_FILES = ["eval_suite.py", "spark_bench.py", "golden_gate.py"]

# A flat perfect domain is only non-blocking when the current suite ran the
# complete, known scenario set and its domain-specific evidence proves that
# the graders actually exercised the outputs. This keeps the historical
# all-pass detector while allowing evidence-backed perfect domains to rank.
VERIFIED_FLAT_SCENARIOS = {
    "structured": frozenset({"SO-02", "SOH-01", "SOH-02", "SOH-03", "SOH-04"}),
    "agentic": frozenset({f"AG-{i:02d}" for i in range(1, 13)}),
    "visual": frozenset({f"VIS-{i:02d}" for i in range(1, 6)}),
}


def _all_repeats_exact(rec, expected):
    subs = rec.get("subs")
    return (bool(subs) and all(round(float(x), 6) == expected for x in subs)
            and rec.get("pass_rate") == 1.0
            and not str(rec.get("reason", "")).startswith("error:"))


def _verified_flat_success(domain, records):
    """Return True only for a complete, evidence-bearing perfect domain."""
    expected_ids = VERIFIED_FLAT_SCENARIOS.get(domain)
    if not expected_ids or {r.get("id") for r in records} != expected_ids:
        return False
    if not all(round(float(r.get("score", -1)), 6) == 1.0
               and _all_repeats_exact(r, 1.0) for r in records):
        return False

    if domain == "structured":
        bad = ("no parseable", "missing", "bad ", "wrong type", "validation failed",
               "extra keys")
        return all(not any(token in str(r.get("reason", "")).lower()
                           for token in bad) for r in records)

    if domain == "agentic":
        for rec in records:
            reason = str(rec.get("reason", ""))
            match = re.search(r"agentic\s+(\d+)/(\d+):", reason)
            if not match or match.group(1) != match.group(2):
                return False
            if "CORRECTNESS GATE FAILED" in reason or "\u2717" in reason:
                return False
        return True

    if domain == "visual":
        by_id = {r["id"]: r for r in records}
        if not all(r.get("artifact") and os.path.isfile(r["artifact"])
                   for r in records):
            return False
        race = str(by_id["VIS-04"].get("reason", ""))
        runner = str(by_id["VIS-05"].get("reason", ""))
        race_evidence = ("red-visible", "blue-visible", "red-moves",
                         "blue-moves", "overtake-event")
        runner_evidence = ("scene-structure", "peak>start",
                           "peak-not-loadflash", "settles")
        bad = ("render(", "js-errors", "too-few-frames")
        return (all(token in race for token in race_evidence)
                and all(token in runner for token in runner_evidence)
                and not any(token in race or token in runner for token in bad))

    return False


def classify_eval_integrity(res):
    """Return (blocking quarantine flags, non-blocking verified-flat facts)."""
    qflags = []
    verified_flat = []
    by_dom = {}
    for scenario in res.get("scenarios", []):
        if scenario.get("group") == "capability":
            by_dom.setdefault(scenario["domain"], []).append(scenario)

    for dname, records in sorted(by_dom.items()):
        scores = [round(float(r["score"]), 6) for r in records]
        if len(scores) >= 3 and len(set(scores)) == 1 and scores[0] in (0.0, 1.0):
            if scores[0] == 1.0 and _verified_flat_success(dname, records):
                verified_flat.append(f"{dname}=1")
            else:
                qflags.append(f"FLAT_DOMAIN:{dname}={scores[0]:g}")
        elif (len(scores) >= 5
              and sum(1 for x in scores if x == 0.0) >= 0.8 * len(scores)
              and statistics.mean(scores) < 0.05):
            qflags.append(f"DEAD_DOMAIN:{dname}")

    allcap = [round(float(r["score"]), 6)
              for records in by_dom.values() for r in records]
    if len(by_dom) >= 2 and len(allcap) >= 6 and len(set(allcap)) == 1:
        all_verified = (allcap[0] == 1.0
                        and {item.split("=", 1)[0] for item in verified_flat}
                        == set(by_dom))
        if not all_verified:
            qflags.append(f"FLAT_ALL:{allcap[0]:g}")
    if not res.get("trial_stats", {}).get("valid", True):
        qflags.append(f"ERROR_RATE:{res['trial_stats'].get('error_rate')}%")
    return qflags, verified_flat


def _abort_run(ctx, why, detail=""):
    ctx.add("eval", "provenance", "aborted", why, "", notes=detail[:120])
    ctx.flush()
    print(f"\n[gate] RUN ABORTED: {why}  {detail}", file=sys.stderr)
    sys.exit(2)


def _grader_provenance(ctx, allow_dirty=False):
    """Short git hash of the grader; refuses to run on uncommitted grader code."""
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                           capture_output=True, text=True).stdout.strip() or "unknown"
        dirty = subprocess.run(["git", "status", "--porcelain", "--"] + GRADER_FILES,
                               cwd=HERE, capture_output=True, text=True).stdout.strip()
    except Exception:
        h, dirty = "unknown", ""
    if dirty:
        if not allow_dirty:
            _abort_run(ctx, "grader_dirty",
                       "uncommitted changes in " + ", ".join(
                           ln.split()[-1] for ln in dirty.splitlines()) +
                       " — commit first (or --allow-dirty for dev runs)")
        h += "-dirty"
    return h


def _get_model_records(endpoint, timeout=10):
    url = endpoint.rstrip("/") + "/models"
    key = (os.environ.get("SPARK_BENCH_API_KEY")
           or os.environ.get("OPENROUTER_API_KEY")
           or os.environ.get("OPENAI_API_KEY") or "none")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode())
    return data.get("data", [])


def _get_model_ids(endpoint, timeout=10):
    return [m.get("id", "") for m in _get_model_records(endpoint, timeout)]


def _configure_runaway_guard(args, owner=None):
    """Enable the v6.8 uncapped degeneration guard and select abort mode."""
    if not args.uncapped:
        return "disabled"
    if args.runaway_char_window <= 0 or args.runaway_phrase_window <= 0:
        raise ValueError("v6.8 uncapped guard windows must both be positive")
    backend = args.runaway_abort_backend
    if backend == "auto":
        backend = "sglang" if "sglang" in str(owner or "").lower() else "disconnect"
    os.environ["SPARK_BENCH_RUNAWAY_CHAR_WINDOW"] = str(args.runaway_char_window)
    os.environ["SPARK_BENCH_RUNAWAY_PHRASE_WINDOW"] = str(args.runaway_phrase_window)
    os.environ["SPARK_BENCH_RUNAWAY_ABORT_BACKEND"] = backend
    return backend


def preflight_endpoint(ctx, args):
    """Abort unless the endpoint (a) serves the requested model and (b) returns
    parseable structured tool_calls. A failed tool probe means agentic scores
    would measure the serving config, not the model — the v5 disaster."""
    print("\n[gate] preflight: endpoint identity + tool-call parse probe")
    # -- (a) model identity ------------------------------------------------- #
    model_records = []
    try:
        model_records = _get_model_records(args.endpoint)
        ids = [m.get("id", "") for m in model_records]
    except Exception as e:
        ids = None
        detail = f"{type(e).__name__}: {str(e)[:60]}"
    if ids is None:
        if args.preflight_loose:
            print(f"  [warn] /models unavailable ({detail}) — continuing (--preflight-loose)")
            ctx.add("eval", "provenance", "served_model", "UNAVAILABLE", "", notes=detail)
        else:
            _abort_run(ctx, "preflight_models_unavailable", detail)
    else:
        req = args.model.lower()
        match = [i for i in ids if i.lower() == req or req in i.lower() or i.lower() in req]
        ctx.add("eval", "provenance", "served_model", ";".join(ids)[:200], "")
        if not match:
            _abort_run(ctx, "preflight_wrong_model",
                       f"requested '{args.model}' but endpoint serves: {ids}")
        print(f"  [ok ] endpoint serves requested model: {match[0]}")
        matched_record = next((m for m in model_records if m.get("id") == match[0]), {})
        _configure_runaway_guard(args, owner=matched_record.get("owned_by"))
    if ids is None:
        _configure_runaway_guard(args, owner=None)
    # -- (b) tool-call parse probe ------------------------------------------ #
    import eval_suite as ev
    # probe must run under the SAME thinking mode as the eval it gates —
    # with thinking on-by-default (e.g. Qwen3.6 on SGLang) the model can burn
    # the whole probe budget reasoning and never emit the tool call.
    probe_extra = None
    if args.thinking in ("on", "off"):
        probe_extra = {"chat_template_kwargs": {
            "enable_thinking": args.thinking == "on",
            "thinking_mode": "enabled" if args.thinking == "on" else "disabled",
        }}
    calls, last = [], None
    probe_max_tokens = None if args.uncapped else 512
    probe_timeout = None if args.timeout <= 0 else min(args.timeout, 180)
    for attempt in (1, 2):
        try:
            last = chat_stream(args.endpoint, args.model,
                               [{"role": "user", "content": TOOL_PROMPT}],
                               max_tokens=probe_max_tokens, temperature=0.0,
                               tools=WEATHER_TOOL, timeout=probe_timeout,
                               extra=probe_extra)
            calls = ev.assemble_tool_calls(last)
        except Exception as e:
            last = {"text": f"error {type(e).__name__}: {str(e)[:60]}"}
        if calls:
            break
    if not calls:
        ctx.add("eval", "provenance", "preflight_tool_probe", "FAIL", "",
                notes=(last or {}).get("text", "")[:100])
        _abort_run(ctx, "preflight_dead_tool_parser",
                   "endpoint never emitted structured tool_calls on an explicit "
                   "tool prompt (2 attempts) — check --tool-call-parser matches "
                   "the model family; agentic scores would be invalid")
    names = ",".join(c["name"] for c in calls)
    ctx.add("eval", "provenance", "preflight_tool_probe", "PASS", "", notes=names)
    print(f"  [ok ] tool-call probe parsed: {names}")


def _lock_path(endpoint):
    host = re.sub(r"[^\w.-]+", "_", (endpoint or "local").split("//")[-1].rstrip("/"))
    d = os.path.join(DEFAULT_OUT, ".locks")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, host + ".lock")


def _acquire_box_lock(endpoint, run_id):
    """One eval per endpoint box. Returns lock path; exits if busy."""
    p = _lock_path(endpoint)
    if os.path.exists(p):
        try:
            with open(p) as f:
                info = json.load(f)
        except Exception:
            info = {}
        pid = info.get("pid")
        if pid and os.path.exists(f"/proc/{pid}"):
            print(f"FATAL: box busy — {p} held by run "
                  f"{info.get('run_id')} (pid {pid} still alive). "
                  f"One eval per box.", file=sys.stderr)
            sys.exit(3)
        print(f"[gate] stale lock (run {info.get('run_id')}, pid {pid} dead) — replacing")
    with open(p, "w") as f:
        json.dump({"run_id": run_id, "pid": os.getpid(),
                   "started": time.strftime("%Y-%m-%dT%H:%M:%S")}, f)
    return p


def _release_box_lock(path):
    try:
        with open(path) as f:
            if json.load(f).get("pid") == os.getpid():
                os.remove(path)
    except Exception:
        pass


class _RunMarker:
    """On-disk liveness: <run_id>.STARTED written immediately and re-written
    every 30s (mtime = heartbeat); <run_id>.DONE written on completion.
    Watchers verify runs from these files, never from process names."""

    def __init__(self, run_id, out_dir):
        d = os.path.join(out_dir, "runs")
        os.makedirs(d, exist_ok=True)
        self.run_id = run_id
        self.path = os.path.join(d, run_id + ".STARTED")
        self.done_path = os.path.join(d, run_id + ".DONE")
        self.n_done = 0
        self._t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._stop = threading.Event()

    def _write(self, path, **extra):
        with open(path, "w") as f:
            json.dump(dict(run_id=self.run_id, pid=os.getpid(), started=self._t0,
                           last_beat=time.strftime("%Y-%m-%dT%H:%M:%S"),
                           scenarios_done=self.n_done, **extra), f)

    def start(self):
        self._write(self.path)
        threading.Thread(target=self._beat, daemon=True).start()
        print(f"  [gate] run marker: {self.path}")

    def _beat(self):
        while not self._stop.wait(30):
            self._write(self.path)

    def tick(self):
        self.n_done += 1

    def done(self, summary=""):
        self._stop.set()
        self._write(self.done_path, finished=time.strftime("%Y-%m-%dT%H:%M:%S"),
                    summary=summary)


# --------------------------------------------------------------------------- #
# Eval : deep graded multi-domain score (see eval_suite.py)
# --------------------------------------------------------------------------- #
def _record_eval_trial_stats(ctx, trial_stats):
    """Persist the validity and methodology contract beside score rows."""
    if not trial_stats:
        return
    ctx.add("eval", "provenance", "methodology",
            trial_stats.get("methodology", "unknown"), "")
    ctx.add("eval", "provenance", "run_valid",
            "PASS" if trial_stats.get("valid", False) else "FAIL", "")
    for metric, unit in (
            ("error_rate", "percent"),
            ("repeats", "count"),
            ("pass_at_1", "percent"),
            ("pass_at_k", "percent"),
            ("reliability_gap", "percent"),
            ("score_stddev", "frac"),
            ("mean_scenario_stddev", "frac")):
        if trial_stats.get(metric) is not None:
            ctx.add("eval", "provenance", metric, trial_stats[metric], unit)


def run_eval(ctx, args):
    import eval_suite as ev

    # ---- gate 1: golden gate — grader proves itself on known transcripts ----
    gate_note = "SKIPPED (--skip-golden-gate)"
    if not args.skip_golden_gate:
        from golden_gate import run_gate
        print("\n[gate] golden gate: grader self-check on canned transcripts")
        gate_ok, gate_note = run_gate(verbose=True)
        if not gate_ok:
            ctx.add("eval", "provenance", "golden_gate", "FAIL", "", notes=gate_note)
            _abort_run(ctx, "golden_gate_failed",
                       "grader does not reproduce known scores — fix the grader "
                       "before grading any model")
    ctx.add("eval", "provenance", "golden_gate",
            "PASS" if not args.skip_golden_gate else "SKIPPED", "", notes=gate_note)

    # ---- gate 2: provenance — stamp grader version, refuse dirty tree ----
    grader_git = _grader_provenance(ctx, allow_dirty=args.allow_dirty)
    ctx.add("eval", "provenance", "grader_git", grader_git, "")
    print(f"[gate] grader version: {grader_git}")

    # ---- gate 4: preflight — right model, working tool-call parse ----
    if not args.skip_preflight:
        preflight_endpoint(ctx, args)
    else:
        _configure_runaway_guard(args, owner=None)
        ctx.add("eval", "provenance", "preflight_tool_probe",
                "SKIPPED (--skip-preflight)", "")

    # ---- gate 5: on-disk run marker + heartbeat ----
    marker = _RunMarker(ctx.run_id, args.out_dir)
    marker.start()

    ctx.mdln(f"# Deep Eval ({ctx.run_id})\n")
    request_policy = "uncapped" if args.uncapped else "scenario-capped"
    request_timeout = None if args.timeout <= 0 else args.timeout
    ctx.mdln(f"- model `{ctx.model}` @ `{ctx.endpoint}`  thinking `{args.thinking}` "
             f"repeats `{args.repeats}` temp `{args.temperature}` "
             f"request policy `{request_policy}` timeout "
             f"`{'none' if request_timeout is None else request_timeout}`\n")
    ctx.add("eval", "provenance", "request_policy", request_policy, "")
    ctx.add("eval", "provenance", "request_timeout",
            "none" if request_timeout is None else request_timeout, "s")
    if args.uncapped:
        ctx.add("eval", "provenance", "runaway_char_window",
                args.runaway_char_window, "characters")
        ctx.add("eval", "provenance", "runaway_phrase_window",
                args.runaway_phrase_window, "characters")
        ctx.add("eval", "provenance", "runaway_abort_backend",
                os.environ.get("SPARK_BENCH_RUNAWAY_ABORT_BACKEND", "unknown"), "")
    ctx.mdln(f"- grader `{grader_git}` · golden gate {gate_note} · "
             f"preflight {'skipped' if args.skip_preflight else 'passed'}\n")

    def chat_fn(messages, max_tokens, temperature, tools, extra):
        return chat_stream(ctx.endpoint, ctx.model, messages, max_tokens,
                           temperature=temperature, tools=tools,
                           timeout=request_timeout, extra=extra)

    weights = {}
    for kv in (args.weights or "").split(","):
        if "=" in kv:
            k, v = kv.split("=")
            weights[k.strip()] = float(v)

    def progress(rec):
        marker.tick()
        print(f"  [eval] {rec['id']:<6} {rec['domain']:<14} "
              f"score={rec['score']:.2f} cons={rec['consistency']:.2f} "
              f"({rec['reason'][:48]})")

    challenge = args.tier == "challenge"
    tiers = None if args.tier in ("all", "challenge") else [args.tier]
    scenario_ids = ev.CHALLENGE_SCENARIO_IDS if challenge else None
    if args.scenario_ids:
        if challenge:
            raise ValueError("--scenario-ids cannot be combined with --tier challenge")
        scenario_ids = {x.strip() for x in args.scenario_ids.split(",") if x.strip()}
    repeat_indices = ({int(x) for x in args.repeat_indices.split(",") if x.strip()}
                      if args.repeat_indices else None)
    artifact_dir = os.path.join(args.out_dir, "artifacts", ctx.run_id)
    res = ev.run_suite(chat_fn, repeats=args.repeats, temperature=args.temperature,
                       domains=(args.domains.split(",") if args.domains else None),
                       tiers=tiers, scenario_ids=scenario_ids,
                       repeat_indices=repeat_indices,
                       thinking=args.thinking, timeout=request_timeout,
                       uncapped=args.uncapped,
                       weights=weights or None, artifact_dir=artifact_dir,
                       progress=progress)
    ov = res["overall"]
    grade, stars, label = ov["rating"]

    # ---- quarantine gate: degenerate score patterns never auto-publish ----
    # The v6.1 auto-pass signature was a capability domain flat at exactly
    # 100.0; the v5 dead-parser signature was agentic flat at ~0. Either way,
    # a domain where every scenario scores identically at an extreme is a
    # harness symptom until a human clears it.
    qflags, verified_flat = classify_eval_integrity(res)
    ctx.add("eval", "provenance", "quarantine",
            ";".join(qflags) if qflags else "clean", "")
    ctx.add("eval", "provenance", "verified_flat",
            ";".join(verified_flat) if verified_flat else "none", "")
    if verified_flat:
        detail = ";".join(verified_flat)
        print(f"\n  [integrity] verified perfect domain(s): {detail}")
        ctx.mdln(f"> **Verified perfect domains** - `{detail}` passed complete "
                 "scenario-set and domain-evidence checks.\n")
    if qflags:
        print(f"\n  *** QUARANTINED: {';'.join(qflags)} — degenerate score "
              f"pattern; leaderboard will exclude this run until a human "
              f"verifies it is real model behaviour. ***", file=sys.stderr)
        ctx.mdln(f"> ⚠️ **QUARANTINED** — `{';'.join(qflags)}`: degenerate score "
                 f"pattern (harness symptom until verified).\n")

    # ---- CSV rows ---- #
    _record_eval_trial_stats(ctx, res.get("trial_stats", {}))
    for k in ("truescore", "capability_score", "operational_score", "quality",
              "calibration", "reliability", "efficiency", "responsiveness"):
        if ov.get(k) is None:
            continue  # component had no scenarios (e.g. filtered domains)
        ctx.add("eval", "overall", k, round(ov[k], 1), "score0-100",
                notes=f"thinking={args.thinking}")
    ctx.add("eval", "overall", "median_latency", round(ov["median_latency_s"], 2), "s")
    total_toks = sum(s.get("output_tokens", 0) for s in res["scenarios"])
    ctx.add("eval", "overall", "total_output_tokens", total_toks, "tok",
            notes=f"{ov.get('n_scenarios','?')} scenarios")
    for d in res["domains"]:
        ctx.add("eval", d["domain"], "domain_quality", round(d["quality"], 1),
                "score0-100", notes=f"{d['group']} n={d['n']}")
        ctx.add("eval", d["domain"], "domain_reliability", round(d["reliability"], 1),
                "score0-100", notes=d["group"])
    for s in res["scenarios"]:
        ctx.add("eval", s["id"], "score", round(s["score"], 3), "frac",
                notes=f"{s['domain']}:{s['reason'][:48]}")
        ctx.add("eval", s["id"], "output_tokens", s.get("output_tokens", 0), "tok",
                notes=s["domain"])

    # ---- markdown ---- #
    def score_text(k):
        return "n/a" if ov.get(k) is None else f"{ov[k]:.1f}"

    ctx.mdln(f"## TrueScore {ov['truescore']:.1f}/100  —  {'⭐' * stars} "
             f"{label} (grade {grade})\n")
    ctx.mdln("| headline score | value | meaning |")
    ctx.mdln("|----------------|------:|---------|")
    ctx.mdln(f"| Capability Score | {score_text('capability_score')} | quality/correctness without speed penalty |")
    ctx.mdln(f"| Operational Score | {score_text('operational_score')} | efficiency + latency/responsiveness |")
    ctx.mdln(f"| **TrueScore** | **{ov['truescore']:.1f}** | combined deployment score |")
    ctx.mdln("\n| component | score | TrueScore weight |")
    ctx.mdln("|-----------|------:|-----------------:|")
    w = res["meta"]["weights"]
    wsum = sum(w[k] for k in w if ov.get(k) is not None) or 1.0
    for k in ("quality", "calibration", "reliability", "efficiency", "responsiveness"):
        if ov.get(k) is None:
            ctx.mdln(f"| {k} | n/a | — |")
        else:
            ctx.mdln(f"| {k} | {ov[k]:.1f} | {w[k] / wsum:.0%} |")
    ctx.mdln(f"\nMedian turn latency {ov['median_latency_s']:.2f}s · "
             f"{ov['n_scenarios']} scenarios · thinking {args.thinking}\n")

    # Trial statistics
    ts = res.get("trial_stats", {})
    if ts:
        ctx.mdln("## Trial Statistics\n")
        ctx.mdln("| metric | value | meaning |")
        ctx.mdln("|--------|------:|---------|")
        ctx.mdln(f"| Methodology | {ts.get('methodology','?')} | scenario and grader contract |")
        ctx.mdln(f"| Run Valid | {'yes' if ts.get('valid') else 'no'} | transport error rate {ts.get('error_rate','?')}% |")
        ctx.mdln(f"| Pass@1 | {ts.get('pass_at_1','?')}% | scenarios passing (≥50%) on at least 1 repeat |")
        ctx.mdln(f"| Pass@K | {ts.get('pass_at_k','?')}% | scenarios passing on ALL repeats |")
        ctx.mdln(f"| Reliability Gap | {ts.get('reliability_gap','?')}% | Pass@1 − Pass@K (flakiness cost) |")
        ctx.mdln(f"| Score StdDev | {ts.get('score_stddev','?')} | cross-scenario score spread |")
        ctx.mdln(f"| Scenario StdDev | {ts.get('mean_scenario_stddev','?')} | mean per-scenario repeat variance |\n")

    ctx.mdln("## Domain breakdown\n")
    ctx.mdln("| domain | group | n | quality | reliability |")
    ctx.mdln("|--------|-------|--:|--------:|------------:|")
    for d in res["domains"]:
        ctx.mdln(f"| {d['domain']} | {d['group']} | {d['n']} | "
                 f"{d['quality']:.1f} | {d['reliability']:.1f} |")
    ctx.mdln("\n## Per-scenario\n")
    ctx.mdln("| id | domain | tier | score | cons | latency | reason |")
    ctx.mdln("|----|--------|------|------:|-----:|--------:|--------|")
    for s in res["scenarios"]:
        ctx.mdln(f"| {s['id']} | {s['domain']} | {s.get('tier','base')} | "
                 f"{s['score']:.2f} | {s['consistency']:.2f} | {s['latency']:.1f}s | "
                 f"{s['reason'][:60]} |")
    ctx.mdln()
    if res.get("artifacts"):
        ctx.mdln("## Saved artifacts (open / post these)\n")
        for a in res["artifacts"]:
            ctx.mdln(f"- `{a['id']}` ({a['domain']}, score {a['score']:.2f}): "
                     f"`{a['path']}`")
            ctx.add("eval", a["id"], "artifact", a["path"], "file", notes=a["domain"])
        ctx.mdln()
        print(f"  -> {len(res['artifacts'])} artifact(s) saved under {artifact_dir}")
    def _f(k):
        return "n/a" if ov.get(k) is None else f"{ov[k]:.0f}"
    print(f"\n  === TrueScore {ov['truescore']:.1f}/100  {'⭐' * stars} {label} "
          f"(Cap{_f('capability_score')} Ops{_f('operational_score')} "
          f"Q{_f('quality')} Cal{_f('calibration')} Rel{_f('reliability')} "
          f"Eff{_f('efficiency')} Resp{_f('responsiveness')}) ===")

    # Trial statistics
    ts = res.get("trial_stats", {})
    if ts:
        print(f"  --- Trial Stats: Method={ts.get('methodology','?')} "
              f"Valid={'yes' if ts.get('valid') else 'no'} "
              f"ErrorRate={ts.get('error_rate','?')}% "
              f"Pass@1={ts.get('pass_at_1','?')}% "
              f"Pass@K={ts.get('pass_at_k','?')}% "
              f"RelGap={ts.get('reliability_gap','?')}% "
              f"ScoreStdDev={ts.get('score_stddev','?')} "
              f"ScenStdDev={ts.get('mean_scenario_stddev','?')} ---")

    if args.skip_throughput:
        ctx.mdln("## Serving Throughput Sweep\n")
        ctx.mdln("Skipped by `--skip-throughput`.\n")
        marker.done(f"truescore={ov['truescore']:.1f} "
                    f"quarantine={';'.join(qflags) if qflags else 'clean'}")
        return

    ctx.mdln("## Serving Throughput Sweep\n")
    ctx.mdln("Automatic v5c add-on: single-stream decode at multiple prompt contexts "
             "plus aggregate throughput under concurrent requests. These rows are "
             "stored as `tier2` metrics under the same run id as the deep eval.\n")
    sweep_args = argparse.Namespace(
        contexts=args.throughput_contexts,
        concurrency=args.throughput_concurrency,
        conc_context=args.throughput_conc_context,
        gen_tokens=args.throughput_gen_tokens,
        timeout=args.timeout,
    )
    run_tier2(ctx, sweep_args, title="Serving throughput detail", heading_level=3)
    marker.done(f"truescore={ov['truescore']:.1f} "
                f"quarantine={';'.join(qflags) if qflags else 'clean'}")


# --------------------------------------------------------------------------- #
# helpers / CLI
# --------------------------------------------------------------------------- #
def _which(b):
    from shutil import which
    return which(b) is not None


def build_ctx(args):
    return Ctx(label=args.label, model=getattr(args, "model", "") or "",
               endpoint=getattr(args, "endpoint", "") or "",
               topology=args.topology, parallelism=getattr(args, "parallelism", "1"),
               spec_decode=getattr(args, "spec_decode", "na"), out_dir=args.out_dir,
               run_kind=getattr(args, "run_kind", "auto") or "auto",
               notes=getattr(args, "notes", "") or "")


def main():
    p = argparse.ArgumentParser(description="spark-bench harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, infer=True):
        sp.add_argument("--label", required=True)
        sp.add_argument("--topology", default="unknown")
        sp.add_argument("--out-dir", default=DEFAULT_OUT)
        sp.add_argument("--run-kind", choices=["auto", "benchmark", "diagnostic"],
                        default="auto",
                        help="report classification; diagnostics are not comparable benchmark runs")
        sp.add_argument("--notes", default="",
                        help="free-form report note explaining this run's purpose")
        if infer:
            sp.add_argument("--endpoint", required=True)
            sp.add_argument("--model", required=True)
            sp.add_argument("--parallelism", default="1")
            sp.add_argument("--spec-decode", dest="spec_decode", default="na")
            sp.add_argument("--timeout", type=int, default=900)
            sp.add_argument("--gen-tokens", type=int, default=256)

    s2 = sub.add_parser("tier2"); common(s2)
    s2.add_argument("--contexts", default="4096")
    s2.add_argument("--concurrency", default="1,8")
    s2.add_argument("--conc-context", type=int, default=1024)

    s3 = sub.add_parser("tier3"); common(s3)
    s3.add_argument("--retrieval-context", type=int, default=8192)

    sa = sub.add_parser("all"); common(sa)
    sa.add_argument("--contexts", default="4096,32768")
    sa.add_argument("--concurrency", default="1,8")
    sa.add_argument("--conc-context", type=int, default=1024)
    sa.add_argument("--retrieval-context", type=int, default=8192)

    se = sub.add_parser("eval"); common(se)
    se.add_argument("--repeats", type=int, default=2,
                    help="runs per scenario (>=2 needed for reliability signal)")
    se.add_argument("--temperature", type=float, default=0.3)
    se.add_argument("--thinking", choices=["auto", "on", "off"], default="auto",
                    help="inject chat_template_kwargs.enable_thinking")
    se.add_argument("--uncapped", action="store_true",
                    help="omit max_tokens on every eval and agentic request so "
                         "reasoning models may use the endpoint's full remaining context")
    se.add_argument("--runaway-char-window", type=int, default=4096,
                    help="v6.8 uncapped guard: identical-character window (default 4096)")
    se.add_argument("--runaway-phrase-window", type=int, default=8192,
                    help="v6.8 uncapped guard: repeated-phrase window (default 8192)")
    se.add_argument("--runaway-abort-backend",
                    choices=("auto", "sglang", "disconnect"), default="auto",
                    help="abort mode; auto uses /models owned_by metadata")
    se.add_argument("--tier", choices=["base", "hard", "challenge", "all"],
                    default="all", help="base = original suite, hard = "
                    "adversarial+visual, challenge = v6.8.1 diagnostic subset, "
                    "all = complete v6.8.1 suite")
    se.add_argument("--domains", default="",
                    help="comma filter e.g. tool_use,coding,safety,visual")
    se.add_argument("--scenario-ids", default="",
                    help="exact comma-separated scenario subset, e.g. AG-11,AG-12")
    se.add_argument("--repeat-indices", default="",
                    help="exact 1-based repeat numbers to run and preserve in filenames")
    se.add_argument("--weights", default="",
                    help="override composite weights e.g. quality=0.5,responsiveness=0.1")
    se.add_argument("--skip-throughput", action="store_true",
                    help="skip the automatic v5c serving throughput sweep")
    se.add_argument("--skip-golden-gate", action="store_true",
                    help="DEV ONLY: skip the grader self-test gate")
    se.add_argument("--skip-preflight", action="store_true",
                    help="DEV ONLY: skip endpoint identity + tool-parse preflight")
    se.add_argument("--preflight-loose", action="store_true",
                    help="downgrade a missing /models endpoint to a warning")
    se.add_argument("--allow-dirty", action="store_true",
                    help="DEV ONLY: run with uncommitted grader changes "
                         "(stamps grader_git as <hash>-dirty)")
    se.add_argument("--throughput-contexts", default="1024,8192,32768",
                    help="prompt contexts for automatic eval throughput sweep")
    se.add_argument("--throughput-concurrency", default="1,2,4,8",
                    help="concurrency levels for automatic eval throughput sweep")
    se.add_argument("--throughput-conc-context", type=int, default=1024,
                    help="prompt context used for automatic concurrency sweep")
    se.add_argument("--throughput-gen-tokens", type=int, default=512,
                    help="requested output tokens for automatic throughput sweep")

    s1 = sub.add_parser("tier1"); common(s1, infer=False)
    s1.add_argument("--peer-ssh", required=True, help="ssh host for remote ib server")
    s1.add_argument("--links", required=True,
                    help="comma list of dev:peer_ip e.g. rocep1s0f0:192.168.2.2")
    s1.add_argument("--gid", type=int, default=3, help="RoCEv2 GID index")
    s1.add_argument("--ib-size", type=int, default=1048576)
    s1.add_argument("--ib-dur", type=int, default=8)
    s1.add_argument("--ib-qp", type=int, default=4)
    s1.add_argument("--ib-mtu", type=int, default=4096)

    args = p.parse_args()
    ctx = build_ctx(args)
    print(f"\n=== spark-bench run {ctx.run_id} ===")
    if args.cmd == "tier1":
        run_tier1(ctx, args)
    elif args.cmd == "tier2":
        run_tier2(ctx, args)
    elif args.cmd == "tier3":
        run_tier3(ctx, args)
    elif args.cmd == "all":
        run_tier2(ctx, args)
        run_tier3(ctx, args)
    elif args.cmd == "eval":
        # gate 3: one eval per endpoint box, enforced on disk
        lock = _acquire_box_lock(args.endpoint, ctx.run_id)
        try:
            run_eval(ctx, args)
        finally:
            _release_box_lock(lock)
    ctx.flush()


if __name__ == "__main__":
    main()
