# Qwen3.6-35B-A3B NVIDIA NVFP4 + MTP-3 on 1× DGX Spark

Deploy NVIDIA's ModelOpt NVFP4 quantized Qwen3.6-35B-A3B with its built-in MTP speculative decoding heads on a single DGX Spark. This config measured **105 tok/s single-stream** and **450 tok/s aggregate at 16 concurrent streams** — +36% / +19% over the same stack without speculative decoding, and the fastest single-stream result we've recorded on this box for this model, ahead of our best DFlash and Atlas configs.

## Requirements

- 1× NVIDIA DGX Spark (128 GB unified memory)
- Docker
- HuggingFace access to `nvidia/Qwen3.6-35B-A3B-NVFP4`

## Models

| Role | Model | Notes |
|---|---|---|
| Target + drafter | `nvidia/Qwen3.6-35B-A3B-NVFP4` | Official NVIDIA ModelOpt NVFP4 checkpoint; the MTP draft heads ship inside the checkpoint — no external drafter model needed |

> **MTP ≠ DFlash.** This recipe uses the checkpoint's built-in multi-token-prediction heads (3-token draft, verified per step). On this hardware it beat the external z-lab DFlash drafter on the same weights: DFlash K10 measured 76.3 tok/s single-stream (roughly the no-spec baseline) with only ~19–36% draft acceptance, while MTP-3 reached 105.3 tok/s.

## Container

```
eugr/spark-vllm:latest
```

Tested at digest `sha256:1cdce378c4c32a1c26029cff8ca986525b5ec35bcdc6dab40e889d6376be3ba3` (nightly of 2026-07-06, [spark-vllm-docker](https://github.com/eugr/spark-vllm-docker) commit `95f0196`). Credit to eugr — this config is a benchmark-shaped variant of the repo's `qwen3.6-35b-a3b-nvfp4.yaml` recipe.

## Quick start

With the spark-vllm-docker repo (uses the upstream recipe — 262K context, prefix caching on):

```bash
cd spark-vllm-docker
./run-recipe.sh qwen3.6-35b-a3b-nvfp4 --solo --setup
```

Or run the exact configuration we benchmarked:

```bash
docker run -d --name qwen-mtp3 --gpus all --network host --ipc host --shm-size 8gb \
  --memory 110g --memory-swap 110g --entrypoint /bin/bash \
  -e NVIDIA_DISABLE_REQUIRE=1 \
  -v $HOME/models:/models:ro \
  -v $PWD/serve.sh:/serve.sh:ro \
  eugr/spark-vllm:latest /serve.sh
```

`serve.sh`:

```bash
#!/bin/bash
export VLLM_MARLIN_USE_ATOMIC_ADD=1
exec vllm serve /models/qwen36-35b-nvfp4 --served-model-name qwen36-35b-nvfp4 \
  --host 0.0.0.0 --port 8891 --tensor-parallel-size 1 --trust-remote-code \
  --kv-cache-dtype fp8 --attention-backend flashinfer --moe-backend marlin \
  --gpu-memory-utilization 0.6 --max-model-len 32768 --max-num-seqs 16 \
  --max-num-batched-tokens 8192 --enable-chunked-prefill --async-scheduling \
  --no-enable-prefix-caching \
  --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}' \
  --load-format fastsafetensors --reasoning-parser qwen3 --tool-call-parser qwen3_coder \
  --enable-auto-tool-choice
```

Notes on the deltas from the upstream recipe:

- `--max-model-len 32768 --max-num-seqs 16 --gpu-memory-utilization 0.6` — our benchmark shape. Upstream ships 262K context / 4 seqs / util 0.4; use that for long-context work.
- `--no-enable-prefix-caching` — disabled so benchmark numbers aren't inflated by repeated-prompt cache hits. Enable it for real serving.
- `--tool-call-parser qwen3_coder` — upstream ships `qwen3_xml`; `qwen3_coder` is what our harness verified for reliable tool-call parsing on this checkpoint.
- Cold start with `--load-format fastsafetensors`: ~242 s to first completion (dropped page caches).

## Measured results (spark-bench, single DGX Spark)

Throughput (tier2: 1K/8K-token prompts, 512-token generations, sampling top_p 0.95 / top_k 20):

| Config | Single-stream tok/s (8K / 1K ctx) | Aggregate tok/s @ c1 → c8 → c16 | run_id |
|---|---|---|---|
| **This recipe (MTP-3)** | **102.0 / 105.3** | **97 → 312 → 450** | `Qwen3.6-35B-NVFP4-vllm-eugr0706-recipe-mtp3-throughput-20260708-171225` |
| Same stack, no spec decode | 74.3 / 78.0 | 76 → 276 → 357 | `Qwen3.6-35B-NVFP4-vllm-eugr0706-parity-throughput-20260708-170657` |
| Same stack, DFlash K10 drafter | 69.1 / 76.3 | 65 → 232 → 301 | `Qwen3.6-35B-NVFP4-vllm-eugr0706-dflash-k10-throughput-20260708-183230` |

Quality: **TrueScore 86.6** on our v6.4c suite (74 scenarios × 2 repeats, thinking off, run `Qwen3.6-35B-NVFP4-eugr0706-mtp3-thinkOFF-74scen-v6.4c-1Spark-20260708-174753`) — the top score recorded on this suite version to date. The structured and visual domains scored 100%; per our integrity gates such perfect domains are auto-flagged for human review, and the raw structured outputs were verified valid against the asks. MTP speculative decoding is output-lossless by construction — draft tokens are verified against the target model's own distribution.

All numbers come from `results/spark_bench.csv` in this repo — every row carries its run_id.
