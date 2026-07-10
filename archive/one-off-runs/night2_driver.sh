#!/bin/bash
# night2_driver.sh — recovery + extension: Atlas FP8 leg (bind fix) then NVFP4 x3.
# Fixes vs matrix_driver: Atlas --bind 0.0.0.0; parity probe reads response from file arg.
set -u
NODE=10.0.0.183
BENCH=/home/raulwesche/projects/spark-bench
SCRATCH=/tmp/claude-1000/-home-raulwesche/4dd56934-849c-4930-b8cf-ae2f3b995666/scratchpad
RES=$SCRATCH/matrix-night; LOG=$RES/driver.log
HSHA=462e6cf
FP8_SNAP=/root/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B-FP8/snapshots/95a723d08a9490559dae23d0cff1d9466213d989
NVFP4_PATH=/models/qwen36-35b-nvfp4
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'

log(){ echo "[$(date +%H:%M:%S)] $*" >> $LOG; }
S(){ timeout 25 ssh -o BatchMode=yes $NODE "$@"; }
DEADLINE=$(date -d "08:15" +%s); [ $(date +%s) -gt $DEADLINE ] && DEADLINE=$(date -d "tomorrow 08:15" +%s)

# wait for bonus leg to finish
while pgrep -f bonus_dflash.sh >/dev/null 2>&1; do sleep 60; done
log "=== NIGHT2: Atlas FP8 (bind fix) + NVFP4 x3 ==="

teardown_verify(){
  S 'docker ps -aq | xargs -r docker rm -f >/dev/null 2>&1; sleep 5; free -g | awk "/Mem/{print \$7}"' > /tmp/avail.$$ 2>/dev/null
  AV=$(cat /tmp/avail.$$; rm -f /tmp/avail.$$)
  log "teardown-verify: ${AV}GB"
  [ -z "$AV" ] || [ "$AV" -lt 105 ] && { log "ABORT: memory ${AV}GB"; return 1; }
  S 'sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'
  return 0
}
wait_ready(){ # port cap name
  local t0=$(date +%s) c st; T_API=""; T_FIRST=""
  while [ $(( $(date +%s) - t0 )) -lt $2 ]; do
    c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 http://$NODE:$1/v1/models 2>/dev/null)
    [ "$c" = "200" ] && { T_API=$(( $(date +%s) - t0 )); break; }
    st=$(S "docker inspect -f '{{.State.Status}}' matrix-$3 2>/dev/null")
    [ "$st" != "running" ] && [ -n "$st" ] && { log "$3 died"; return 1; }
    sleep 5
  done
  [ -z "$T_API" ] && { log "$3 TIMEOUT ${2}s"; return 1; }
  local ok=$(curl -s http://$NODE:$1/v1/chat/completions -H 'Content-Type: application/json' \
    -d '{"model":"'"$4"'","messages":[{"role":"user","content":"hi"}],"max_tokens":8,"temperature":0}' \
    --max-time 120 | python3 -c "import sys,json;print('ok' if json.load(sys.stdin).get('choices') else 'bad')" 2>/dev/null)
  [ "$ok" != "ok" ] && { log "$3 first-completion failed"; return 1; }
  T_FIRST=$(( $(date +%s) - t0 ))
  log "$3 READY: api=${T_API}s first=${T_FIRST}s"
}
parity_probe(){ # port name servedname
  local F=/tmp/probe.$$
  curl -s http://$NODE:$1/v1/chat/completions -H 'Content-Type: application/json' -d '{
    "model":"'"$3"'","max_tokens":200,"temperature":0.3,"top_p":0.95,"top_k":20,
    "chat_template_kwargs":{"enable_thinking":false},
    "messages":[{"role":"user","content":"What is the weather in Paris? Use the tool."}],
    "tools":[{"type":"function","function":{"name":"get_weather","description":"Get weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}],
    "tool_choice":"auto"}' --max-time 90 > $F 2>/dev/null
  python3 - "$2" "$F" >> $RES/probe_$2.txt 2>&1 <<'PY'
import sys, json
d = json.load(open(sys.argv[2]))
if "error" in d: print("PROBE HTTP ERROR:", str(d["error"])[:120]); sys.exit(1)
u = d.get("usage") or {}
m = d["choices"][0]["message"]
tc = m.get("tool_calls") or []
print(f"prompt_tokens={u.get('prompt_tokens')} usage={bool(u)} tool_parsed={'YES:'+tc[0]['function']['name'] if tc else 'NO'} think_leak={'<think>' in (m.get('content') or '')}")
PY
  rm -f $F
  log "$2 parity: $(tail -1 $RES/probe_$2.txt)"
}
run_benches(){ # port legname label servedname
  export SPARK_BENCH_DUMP_DIR=$RES/dump_$2; mkdir -p $SPARK_BENCH_DUMP_DIR
  timeout 900 python3 $BENCH/spark_bench.py tier2 --label "warmup-discard-$2" \
    --endpoint http://$NODE:$1/v1 --model $4 --contexts 1024,8192 --concurrency 1,8,16 \
    --conc-context 1024 --gen-tokens 64 --topology single --notes "warmup DISCARD" >> $LOG 2>&1
  timeout 1800 python3 $BENCH/spark_bench.py tier2 --label "Qwen3.6-35B-$2-throughput" \
    --endpoint http://$NODE:$1/v1 --model $4 --contexts 1024,8192 --concurrency 1,8,16 \
    --conc-context 1024 --gen-tokens 512 --topology single \
    --notes "matrix; harness $HSHA; parity flags" >> $LOG 2>&1
  log "$2 tier2 done rc=$?"
  [ $(date +%s) -gt $(( DEADLINE - 3600 )) ] && { log "$2 SKIP eval (deadline)"; return; }
  timeout 12600 python3 $BENCH/spark_bench.py eval --label "$3" \
    --endpoint http://$NODE:$1/v1 --model $4 --thinking off --repeats 2 \
    --skip-throughput --timeout 600 --topology single \
    --notes "matrix; harness $HSHA; pinned top_p0.95/top_k20; prefix off; seqs16; qwen3_coder" >> $LOG 2>&1
  log "$2 eval done rc=$?"
  unset SPARK_BENCH_DUMP_DIR
}

# ---- LEG: Atlas FP8 (bind fix) ----
if teardown_verify; then
  log "=== Atlas FP8 (fixed --bind) ==="
  S "docker run -d --name matrix-atlas --gpus all --network host --memory 110g --memory-swap 110g \
     -e HF_HUB_OFFLINE=1 -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     avarok/atlas-gb10:latest serve --model-from-path $FP8_SNAP \
     --model-name qwen36-35b-fp8 --port 8890 --bind 0.0.0.0 --max-seq-len 32768 \
     --kv-cache-dtype bf16 --lm-head-dtype bf16 --gpu-memory-utilization 0.6 \
     --max-num-seqs 16 --max-batch-size 16 --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
  if wait_ready 8890 600 atlas qwen36-35b-fp8; then
    S 'docker logs matrix-atlas 2>&1 | grep -iE "lm.head|lm_head|mtp=|thinking_default" | head -4' > $RES/atlas_config_lines.txt
    parity_probe 8890 atlas qwen36-35b-fp8
    run_benches 8890 "FP8-atlas" "Qwen3.6-35B-FP8-atlas-thinkOFF-64scen-v6.1-1Spark" qwen36-35b-fp8
  else S 'docker logs --tail 10 matrix-atlas 2>&1 | tail -6' >> $LOG; fi
  S 'docker rm -f matrix-atlas' >/dev/null 2>&1
fi

# ---- NVFP4 x3 ----
# vLLM
if teardown_verify; then
  log "=== NVFP4 vLLM ==="
  cat > /tmp/serve_vllm_nvfp4.sh <<EOF
#!/bin/bash
OUT=\$(python3 /patch_kv.py 2>&1); echo "\$OUT"
echo "\$OUT" | grep -qE "PATCHED|already patched" || exit 1
exec vllm serve $NVFP4_PATH --served-model-name qwen36-35b-nvfp4 \
  --gpu-memory-utilization 0.6 --max-model-len 32768 --max-num-seqs 16 \
  --no-enable-prefix-caching --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 --host 0.0.0.0 --port 8891
EOF
  scp -q /tmp/serve_vllm_nvfp4.sh $NODE:/tmp/serve_vllm_nvfp4.sh
  S "docker run -d --name matrix-vllm --gpus all --network host --ipc host --shm-size 8gb \
     --memory 110g --memory-swap 110g --entrypoint /bin/bash -e HF_HUB_OFFLINE=1 -e NVIDIA_DISABLE_REQUIRE=1 \
     -v /home/raulwesche/models:/models:ro -v /tmp/patch_kv.py:/patch_kv.py:ro \
     -v /tmp/serve_vllm_nvfp4.sh:/serve.sh:ro ghcr.io/aeon-7/aeon-vllm-ultimate:latest /serve.sh" >/dev/null 2>&1
  if wait_ready 8891 2400 vllm qwen36-35b-nvfp4; then
    parity_probe 8891 vllm-nvfp4 qwen36-35b-nvfp4
    run_benches 8891 "NVFP4-vllm-aeon023" "Qwen3.6-35B-NVFP4-vllm-aeon023-thinkOFF-64scen-v6.1-1Spark" qwen36-35b-nvfp4
  else S 'docker logs --tail 10 matrix-vllm 2>&1 | tail -6' >> $LOG; fi
  S 'docker rm -f matrix-vllm' >/dev/null 2>&1
fi
# SGLang
if teardown_verify; then
  log "=== NVFP4 SGLang ==="
  cat > /tmp/serve_sglang_nvfp4.sh <<EOF
#!/bin/bash
exec python3 -m sglang.launch_server --model-path $NVFP4_PATH \
  --served-model-name qwen36-35b-nvfp4 --context-length 32768 \
  --quantization modelopt_fp4 --mem-fraction-static 0.6 --max-running-requests 16 \
  --disable-radix-cache --tool-call-parser qwen3_coder --reasoning-parser qwen3 \
  --host 0.0.0.0 --port 8892 \${SGL_EXTRA:-}
EOF
  scp -q /tmp/serve_sglang_nvfp4.sh $NODE:/tmp/serve_sglang_nvfp4.sh
  for SGL_EXTRA in "" "--attention-backend flashinfer --disable-piecewise-cuda-graph"; do
    S "docker rm -f matrix-sglang >/dev/null 2>&1; docker run -d --name matrix-sglang --gpus all --network host --ipc host --shm-size 8gb \
       --memory 110g --memory-swap 110g --entrypoint /bin/bash -e HF_HUB_OFFLINE=1 -e \"SGL_EXTRA=$SGL_EXTRA\" \
       -v /home/raulwesche/models:/models:ro -v /tmp/serve_sglang_nvfp4.sh:/serve.sh:ro \
       scitrera/dgx-spark-sglang:0.5.12 /serve.sh" >/dev/null 2>&1
    wait_ready 8892 1800 sglang qwen36-35b-nvfp4 && { SGLOK=1; break; } || SGLOK=0
  done
  if [ "${SGLOK:-0}" = "1" ]; then
    parity_probe 8892 sglang-nvfp4 qwen36-35b-nvfp4
    run_benches 8892 "NVFP4-sglang0512" "Qwen3.6-35B-NVFP4-sglang0512-thinkOFF-64scen-v6.1-1Spark" qwen36-35b-nvfp4
  else S 'docker logs --tail 10 matrix-sglang 2>&1 | tail -6' >> $LOG; fi
  S 'docker rm -f matrix-sglang' >/dev/null 2>&1
fi
# Atlas
if teardown_verify; then
  log "=== NVFP4 Atlas ==="
  S "docker run -d --name matrix-atlas --gpus all --network host --memory 110g --memory-swap 110g \
     -e HF_HUB_OFFLINE=1 -v /home/raulwesche/models:/models:ro \
     avarok/atlas-gb10:latest serve --model-from-path $NVFP4_PATH \
     --model-name qwen36-35b-nvfp4 --port 8890 --bind 0.0.0.0 --max-seq-len 32768 \
     --kv-cache-dtype bf16 --lm-head-dtype bf16 --gpu-memory-utilization 0.6 \
     --max-num-seqs 16 --max-batch-size 16 --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
  if wait_ready 8890 600 atlas qwen36-35b-nvfp4; then
    parity_probe 8890 atlas-nvfp4 qwen36-35b-nvfp4
    run_benches 8890 "NVFP4-atlas" "Qwen3.6-35B-NVFP4-atlas-thinkOFF-64scen-v6.1-1Spark" qwen36-35b-nvfp4
  else S 'docker logs --tail 10 matrix-atlas 2>&1 | tail -6' >> $LOG; fi
  S 'docker rm -f matrix-atlas' >/dev/null 2>&1
fi

teardown_verify
log "=== NIGHT2 COMPLETE (full 6-cell matrix attempted) ==="
