# Laguna XS 2.1 (Poolside) — NVFP4 on 1× DGX Spark (GB10)

Serve **Poolside Laguna XS 2.1** (33B total / 3B active MoE coding model) on a single NVIDIA DGX Spark (GB10 Grace-Blackwell, 121 GB unified, aarch64/sm_121a). Model + weights by [Poolside](https://huggingface.co/poolside/Laguna-XS-2.1) (OpenMDW-1.1 license). This recipe is the deployment config we validated for SparkBench.

## TL;DR

- **Image:** `ghcr.io/aeon-7/aeon-vllm-ultimate:latest` (vLLM `0.23.0+aeon.sm121a.dflash`). *Why this image:* official `vllm/vllm-openai` ships no GB10/sm_121a/aarch64 build; this one carries the `laguna` arch + parsers.
- **Weights:** `poolside/Laguna-XS-2.1-NVFP4` (~22 GB, Blackwell-native FP4).
- **Score:** SparkBench v6.1 = **65.1** (think-OFF). Single-stream ~**33-42 tok/s**, ~**720 tok/s** aggregate @ concurrency 32.
- **⚠️ Two gotchas below are load-bearing:** (1) patch the `poolside_v1` tool parser or tool-calls silently fail on NVFP4; (2) do NOT enable CUDA graphs / `--async-scheduling` on this model — they drop ~19 quality points.

## Serve (validated config)

```bash
vllm serve poolside/Laguna-XS-2.1-NVFP4 \
  --served-model-name laguna \
  --trust-remote-code \
  --quantization compressed-tensors \
  --gpu-memory-utilization 0.5 \
  --enforce-eager \
  --max-model-len 32768 \
  --max-num-seqs 8 --max-num-batched-tokens 16384 \
  --enable-auto-tool-choice \
  --tool-call-parser poolside_v1 \
  --reasoning-parser poolside_v1 \
  --host 0.0.0.0 --port 8003
```

Run the container with `--memory 110g --memory-swap 110g` as a cgroup backstop. `gpu-util 0.5` on a 22 GB model leaves ~60 GB headroom — it **cannot** exhaust the unified pool (the failure mode that hard-hangs a GB10 node when big models over-commit at `util 0.85`).

Thinking is **off by default**; enable per-request with `"chat_template_kwargs":{"enable_thinking":true}`.

## ⚠️ Gotcha 1 — patch the `poolside_v1` tool parser (required for tools on NVFP4)

The shipped parser (`vllm/tool_parsers/poolside_v1_tool_parser.py`) expects `<tool_call>NAME\n<arg_key>…`, but the **NVFP4 build emits the name inline** (`<tool_call>get_weather<arg_key>city</arg_key>…`, no newline), so `tool_calls` come back empty and the raw markup leaks into `content`. Apply at container start (before `vllm serve`):

```python
# patch_poolside.py
import glob
old = r'r"<tool_call>([^\n]*)\n(.*)</tool_call>"'
new = r'r"<tool_call>([^\n<]*)\s*(.*?)</tool_call>"'  # name stops at first '<', newline optional
for p in glob.glob('/usr/local/lib/python3.12/*-packages/vllm/tool_parsers/poolside_v1_tool_parser.py'):
    s = open(p).read()
    if old in s: open(p,'w').write(s.replace(old, new)); print('PATCHED', p)
```

Verified: after the patch, tool-calls parse in both `auto` and `required` modes. **Report upstream** — the model + shipped parser disagree on format for the NVFP4 quant.

## ⚠️ Gotcha 2 — keep `--enforce-eager` (do NOT "optimize" with graphs/async)

We A/B-tested a throughput-tuned config (`--compilation-config cudagraph_capture_sizes … --async-scheduling --max-num-seqs 32 --max-num-batched-tokens 8192 --gpu-memory-utilization 0.6`). It hit **723 tok/s aggregate** but **tanked quality to 46.3** (−19 pts; code 86→43, structured 80→27, 10 dropped/empty responses). On this MoE the graph-capture + async path corrupts long generations. **Stay eager for correctness.** For lower latency, use **DFlash** instead (see below) — it's distribution-lossless.

## Benchmark (SparkBench v6.1, think-OFF, 64 scen)

**TrueScore 65.1** (Cap 56 · Cal 74 · Rel 80). A narrow coding specialist: **code 86.2 · visual 98.6 · structured 79.8** strong; tool_use/agentic/planning ~35 weak (3B-active limits general breadth). RelGap 20% (inconsistent). Real coding/terminal ability is under-represented by a general suite.

## Optional: DFlash speculative decoding (Phase 2 — not yet applied)

Poolside ships a 5-layer DFlash drafter (`poolside/Laguna-XS-2.1-DFlash-NVFP4`, 0.9 GB, ≤7 tokens/step, ~70% accept on coding, arch `DFlashLagunaForCausalLM`). vLLM support = [PR #46853](https://github.com/vllm-project/vllm/pull/46853) (open — ~420 lines / 5 prod files; the aeon image already has most of the `laguna.py` DFlash side). Cherry-pick it into the container like the parser patch, then add `--speculative-config '{"model":"poolside/Laguna-XS-2.1-DFlash-NVFP4","num_speculative_tokens":7,"method":"dflash"}'` (and **drop** `--async-scheduling`). Expect ~1.5-2× single-stream, quality unchanged. Note the two dead paths: aeon `--speculative-config` as-is loads the wrong (Qwen3-shaped) drafter; scitrera SGLang 0.5.12 predates the SGLang DFlash PR.

Credit: **Poolside** (model, weights, DFlash drafter, `poolside_v1` parsers). Full analysis: SparkBench results + `2026-07-02-Laguna-XS-2.1-v6.1` note.
