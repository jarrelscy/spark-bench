#!/bin/bash
# matrix_driver.sh — overnight FP8 3-engine matrix on .183 (Fable-reviewed design, 2026-07-03)
# Legs: vLLM(aeon023) -> SGLang(0.5.12) -> Atlas. Same snapshot, same node, sequential.
# Every Fable MUST: qwen3_coder parser everywhere; Atlas lm-head+KV bf16 + util 0.6;
# KV bf16 parity; sampling pin via SPARK_BENCH_EXTRA_BODY; prefix caching off; seqs 16;
# drop_caches per leg; caps via timeout(1); provenance (SHA 462e6cf + digests) in notes.
set -u
NODE=10.0.0.183
BENCH=/home/raulwesche/projects/spark-bench
SCRATCH=/tmp/claude-1000/-home-raulwesche/4dd56934-849c-4930-b8cf-ae2f3b995666/scratchpad
RES=$SCRATCH/matrix-night; mkdir -p $RES
LOG=$RES/driver.log
HSHA=462e6cf
SNAP_HOST=/home/raulwesche/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B-FP8/snapshots/95a723d08a9490559dae23d0cff1d9466213d989
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'

log(){ echo "[$(date +%H:%M:%S)] $*" >> $LOG; echo "[$(date +%H:%M:%S)] $*"; }
S(){ timeout 25 ssh -o BatchMode=yes $NODE "$@"; }

DEADLINE=$(date -d "08:15" +%s); [ $(date +%s) -gt $DEADLINE ] && DEADLINE=$(date -d "tomorrow 08:15" +%s)

# record image digests (provenance)
S 'docker images --digests --format "{{.Repository}}:{{.Tag}} {{.Digest}}" | grep -E "atlas-gb10|aeon-vllm-ultimate:latest|dgx-spark-sglang"' > $RES/image_digests.txt 2>&1
log "digests: $(cat $RES/image_digests.txt | tr '\n' ' | ')"

teardown_verify(){
  S 'docker ps -aq | xargs -r docker rm -f >/dev/null 2>&1; sleep 5; free -g | awk "/Mem/{print \$7}"' > /tmp/avail.$$ 2>/dev/null
  AV=$(cat /tmp/avail.$$; rm -f /tmp/avail.$$)
  log "teardown-verify: ${AV}GB available (baseline 116)"
  if [ -z "$AV" ] || [ "$AV" -lt 105 ]; then log "ABORT NIGHT: memory not returning (${AV}GB) — leak/hang precursor"; return 1; fi
  S 'sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null' && log "page cache dropped"
  return 0
}

wait_ready(){ # $1=port $2=cap_seconds $3=name -> sets T_API T_FIRST
  local t0=$(date +%s) c
  T_API=""; T_FIRST=""
  while [ $(( $(date +%s) - t0 )) -lt $2 ]; do
    c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 http://$NODE:$1/v1/models 2>/dev/null)
    if [ "$c" = "200" ]; then T_API=$(( $(date +%s) - t0 )); break; fi
    st=$(S "docker inspect -f '{{.State.Status}}' matrix-$3 2>/dev/null")
    [ "$st" != "running" ] && [ -n "$st" ] && { log "$3 container died during load"; return 1; }
    sleep 5
  done
  [ -z "$T_API" ] && { log "$3 readiness TIMEOUT (${2}s)"; return 1; }
  local ok=$(curl -s http://$NODE:$1/v1/chat/completions -H 'Content-Type: application/json' \
    -d '{"model":"qwen36-35b-fp8","messages":[{"role":"user","content":"hi"}],"max_tokens":8,"temperature":0}' \
    --max-time 120 | python3 -c "import sys,json;print('ok' if json.load(sys.stdin).get('choices') else 'bad')" 2>/dev/null)
  [ "$ok" != "ok" ] && { log "$3 first completion failed"; return 1; }
  T_FIRST=$(( $(date +%s) - t0 ))
  log "$3 READY: api=${T_API}s first_completion=${T_FIRST}s"
  return 0
}

parity_probe(){ # $1=port $2=name
  local P=$RES/probe_$2.txt
  # fingerprint: identical messages+tools payload -> prompt_tokens
  curl -s http://$NODE:$1/v1/chat/completions -H 'Content-Type: application/json' -d '{
    "model":"qwen36-35b-fp8","max_tokens":16,"temperature":0.3,"top_p":0.95,"top_k":20,
    "chat_template_kwargs":{"enable_thinking":false},
    "messages":[{"role":"user","content":"What is the weather in Paris? Use the tool."}],
    "tools":[{"type":"function","function":{"name":"get_weather","description":"Get weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}],
    "tool_choice":"auto"}' --max-time 90 > /tmp/probe.$$ 2>/dev/null
  python3 - "$2" < /tmp/probe.$$ >> $P 2>&1 <<'PY'
import sys, json
name = sys.argv[1]
try: d = json.load(sys.stdin)
except Exception as e: print(f"PROBE PARSE FAIL: {e}"); sys.exit(1)
if "error" in d: print(f"PROBE HTTP ERROR: {str(d['error'])[:120]}"); sys.exit(1)
u = d.get("usage", {}) or {}
m = d["choices"][0]["message"]
tc = m.get("tool_calls") or []
print(f"prompt_tokens={u.get('prompt_tokens')} usage_present={bool(u)}")
print(f"tool_parsed={'YES '+tc[0]['function']['name'] if tc else 'NO'}")
think = "<think>" in (m.get("content") or "")
print(f"think_leak={think}")
PY
  rm -f /tmp/probe.$$
  log "$2 parity: $(tr '\n' ' ' < $P)"
  grep -q "tool_parsed=YES" $P || log "WARN $2: tool parsing FAILED — tool_use/agentic will zero; reporting per-domain"
  grep -q "PROBE HTTP ERROR" $P && return 1
  return 0
}

run_benches(){ # $1=port $2=legname $3=eval_label
  export SPARK_BENCH_DUMP_DIR=$RES/dump_$2; mkdir -p $SPARK_BENCH_DUMP_DIR
  log "$2 warmup shadow pass"
  timeout 900 python3 $BENCH/spark_bench.py tier2 --label "warmup-discard-$2" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-fp8 \
    --contexts 1024,8192 --concurrency 1,8,16 --conc-context 1024 --gen-tokens 64 \
    --topology single --notes "warmup shadow — DISCARD" >> $LOG 2>&1
  log "$2 tier2 (measured)"
  timeout 1800 python3 $BENCH/spark_bench.py tier2 --label "Qwen3.6-35B-FP8-$2-throughput" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-fp8 \
    --contexts 1024,8192 --concurrency 1,8,16 --conc-context 1024 --gen-tokens 512 \
    --topology single --notes "3-engine matrix; harness $HSHA; parity per Fable review" >> $LOG 2>&1
  log "$2 tier2 done rc=$?"
  if [ $(date +%s) -gt $(( DEADLINE - 9000 )) ]; then log "$2 SKIPPING eval (deadline) — tier2-only partial leg"; return; fi
  log "$2 v6.1 eval starting"
  timeout 12600 python3 $BENCH/spark_bench.py eval --label "$3" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-fp8 \
    --thinking off --repeats 2 --skip-throughput --timeout 600 --topology single \
    --notes "3-engine matrix FP8; harness $HSHA; sampling pinned top_p0.95/top_k20; KV bf16; prefix-cache off; seqs16; parser qwen3_coder; snapshot 95a723d0" >> $LOG 2>&1
  log "$2 eval done rc=$?"
  unset SPARK_BENCH_DUMP_DIR
}

leg_snapshot(){ # $1=name
  S 'nvidia-smi -q -d TEMPERATURE,POWER 2>/dev/null | grep -E "GPU Current Temp|Power Draw" | head -2; free -g | awk "/Mem/{print \"avail:\"\$7\"GB\"}"' > $RES/snapshot_$1.txt 2>&1
  log "$1 snapshot: $(tr '\n' ' ' < $RES/snapshot_$1.txt)"
}

# ---------------- LEG B: vLLM ----------------
if teardown_verify; then
  log "=== LEG 1/3: vLLM aeon023 ==="
  scp -q $SCRATCH/serve_vllm_fp8.sh $NODE:/tmp/serve_vllm_fp8.sh
  S "docker run -d --name matrix-vllm --gpus all --network host --ipc host --shm-size 8gb \
     --memory 110g --memory-swap 110g --entrypoint /bin/bash \
     -e HF_HUB_OFFLINE=1 -e NVIDIA_DISABLE_REQUIRE=1 \
     -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     -v /tmp/patch_kv.py:/patch_kv.py:ro -v /tmp/serve_vllm_fp8.sh:/serve.sh:ro \
     ghcr.io/aeon-7/aeon-vllm-ultimate:latest /serve.sh" >/dev/null 2>&1
  if ! wait_ready 8891 2400 vllm; then
    log "vLLM retry once with --enforce-eager (label suffix -eager-fallback)"
    S 'docker logs --tail 5 matrix-vllm 2>&1 | tail -3' >> $LOG 2>&1
    S 'docker rm -f matrix-vllm' >/dev/null 2>&1
    S "docker run -d --name matrix-vllm --gpus all --network host --ipc host --shm-size 8gb \
       --memory 110g --memory-swap 110g --entrypoint /bin/bash \
       -e HF_HUB_OFFLINE=1 -e NVIDIA_DISABLE_REQUIRE=1 -e 'VLLM_EXTRA=--enforce-eager' \
       -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
       -v /tmp/patch_kv.py:/patch_kv.py:ro -v /tmp/serve_vllm_fp8.sh:/serve.sh:ro \
       ghcr.io/aeon-7/aeon-vllm-ultimate:latest /serve.sh" >/dev/null 2>&1
    wait_ready 8891 2400 vllm && VSUF="-eager-fallback" || VSUF="-FAILED"
  else VSUF=""; fi
  if [ "$VSUF" != "-FAILED" ]; then
    parity_probe 8891 vllm
    run_benches 8891 "vllm-aeon023$VSUF" "Qwen3.6-35B-FP8-vllm-aeon023$VSUF-thinkOFF-64scen-v6.1-1Spark"
    leg_snapshot vllm
  fi
  S 'docker stop -t 60 matrix-vllm >/dev/null 2>&1; docker rm -f matrix-vllm' >/dev/null 2>&1
else exit 1; fi

# ---------------- LEG C: SGLang ----------------
if teardown_verify; then
  log "=== LEG 2/3: SGLang 0.5.12 ==="
  scp -q $SCRATCH/serve_sglang_fp8.sh $NODE:/tmp/serve_sglang_fp8.sh
  SGL_TRY=1
  for SGL_EXTRA in "" "--attention-backend flashinfer --disable-piecewise-cuda-graph"; do
    S "docker rm -f matrix-sglang >/dev/null 2>&1; docker run -d --name matrix-sglang --gpus all --network host --ipc host --shm-size 8gb \
       --memory 110g --memory-swap 110g --entrypoint /bin/bash \
       -e HF_HUB_OFFLINE=1 -e \"SGL_EXTRA=$SGL_EXTRA\" \
       -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
       -v /tmp/serve_sglang_fp8.sh:/serve.sh:ro \
       scitrera/dgx-spark-sglang:0.5.12 /serve.sh" >/dev/null 2>&1
    if wait_ready 8892 1800 sglang; then SGLOK=1; break; else SGLOK=0; log "sglang attempt $SGL_TRY failed (extra='$SGL_EXTRA')"; S 'docker logs --tail 8 matrix-sglang 2>&1 | grep -iE "error|assert" | tail -4' >> $LOG 2>&1; fi
    SGL_TRY=2
  done
  if [ "${SGLOK:-0}" = "1" ]; then
    [ $SGL_TRY = 2 ] && SSUF="-hybridflags" || SSUF=""
    parity_probe 8892 sglang
    run_benches 8892 "sglang0512$SSUF" "Qwen3.6-35B-FP8-sglang0512$SSUF-thinkOFF-64scen-v6.1-1Spark"
    leg_snapshot sglang
  fi
  S 'docker stop -t 60 matrix-sglang >/dev/null 2>&1; docker rm -f matrix-sglang' >/dev/null 2>&1
fi

# ---------------- LEG A: Atlas (last — unproven) ----------------
if teardown_verify; then
  log "=== LEG 3/3: Atlas ==="
  S "docker run -d --name matrix-atlas --gpus all --network host \
     --memory 110g --memory-swap 110g \
     -e HF_HUB_OFFLINE=1 \
     -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     avarok/atlas-gb10:latest serve \
     --model-from-path /root/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B-FP8/snapshots/95a723d08a9490559dae23d0cff1d9466213d989 \
     --model-name qwen36-35b-fp8 --port 8890 --max-seq-len 32768 \
     --kv-cache-dtype bf16 --lm-head-dtype bf16 \
     --gpu-memory-utilization 0.6 --max-num-seqs 16 --max-batch-size 16 \
     --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
  if wait_ready 8890 600 atlas; then
    S 'docker logs matrix-atlas 2>&1 | grep -iE "lm.head|lm_head|mtp|speculat|MODEL.toml" | head -6' > $RES/atlas_config_lines.txt 2>&1
    log "atlas config lines: $(tr '\n' ' | ' < $RES/atlas_config_lines.txt | head -c 300)"
    parity_probe 8890 atlas
    run_benches 8890 "atlas" "Qwen3.6-35B-FP8-atlas-thinkOFF-64scen-v6.1-1Spark"
    leg_snapshot atlas
  else
    S 'docker logs --tail 15 matrix-atlas 2>&1 | tail -8' >> $LOG 2>&1
  fi
  S 'docker stop -t 60 matrix-atlas >/dev/null 2>&1; docker rm -f matrix-atlas' >/dev/null 2>&1
fi

teardown_verify
log "=== NIGHT COMPLETE === results in CSV (grep Qwen3.6-35B-FP8), raw dumps in $RES/dump_*, log $LOG"
