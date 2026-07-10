#!/bin/bash
# night3_spec.sh — spec-decode round pulled forward from tomorrow (user-approved).
# FP8 checkpoint, tier2-only (quality spot-checks tomorrow per goal), fail-fast per config.
# Configs: atlas-MTP, atlas-DFlash, vllm-MTP, sglang-MTP-NEXTN. (vllm-DFlash = bonus leg, done.)
set -u
NODE=10.0.0.183
BENCH=/home/raulwesche/projects/spark-bench
SCRATCH=/tmp/claude-1000/-home-raulwesche/4dd56934-849c-4930-b8cf-ae2f3b995666/scratchpad
RES=$SCRATCH/matrix-night; LOG=$RES/driver.log
FP8_SNAP=/root/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B-FP8/snapshots/95a723d08a9490559dae23d0cff1d9466213d989
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'
log(){ echo "[$(date +%H:%M:%S)] $*" >> $LOG; }
S(){ timeout 25 ssh -o BatchMode=yes $NODE "$@"; }

while ps -p ${1:?night2 pid} >/dev/null 2>&1; do sleep 120; done
CUT=$(date -d "06:30" +%s); [ $(date +%s) -gt $CUT ] && CUT=$(date -d "tomorrow 06:30" +%s)
log "=== NIGHT3: spec round (early start, user-approved) ==="

prep(){ S 'docker ps -aq | xargs -r docker rm -f >/dev/null 2>&1; sleep 5; sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'; }
ready(){ # port cap name
  local t0=$(date +%s) c
  while [ $(( $(date +%s) - t0 )) -lt $2 ]; do
    c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 http://$NODE:$1/v1/models 2>/dev/null)
    [ "$c" = "200" ] && { log "$3 ready $(( $(date +%s) - t0 ))s"; return 0; }
    st=$(S "docker inspect -f '{{.State.Status}}' spec-$3 2>/dev/null")
    [ "$st" != "running" ] && [ -n "$st" ] && { log "$3 died (fail-fast)"; S "docker logs --tail 6 spec-$3 2>&1 | tail -4" >> $LOG; return 1; }
    sleep 5
  done
  log "$3 timeout"; return 1
}
t2(){ # port label
  timeout 1800 python3 $BENCH/spark_bench.py tier2 --label "$2" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-fp8 \
    --contexts 1024,8192 --concurrency 1,8,16 --conc-context 1024 --gen-tokens 512 \
    --topology single --notes "spec round FP8; tier2-only, quality spot-check pending" >> $LOG 2>&1
  log "$2 tier2 rc=$?"
}

# 1. Atlas MTP (in-checkpoint; watch for silent auto-disable)
if [ $(date +%s) -lt $CUT ]; then prep
  S "docker run -d --name spec-atlasmtp --gpus all --network host --memory 110g --memory-swap 110g \
     -e HF_HUB_OFFLINE=1 -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     avarok/atlas-gb10:latest serve --model-from-path $FP8_SNAP \
     --model-name qwen36-35b-fp8 --port 8890 --bind 0.0.0.0 --max-seq-len 32768 \
     --kv-cache-dtype bf16 --lm-head-dtype bf16 --gpu-memory-utilization 0.6 \
     --max-num-seqs 16 --max-batch-size 16 --speculative \
     --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
  if ready 8890 900 atlasmtp; then
    S 'docker logs spec-atlasmtp 2>&1 | grep -iE "mtp|speculat" | head -4' >> $LOG
    t2 8890 "Qwen3.6-35B-FP8-atlas-MTP-throughput"
    S 'docker logs spec-atlasmtp 2>&1 | grep -iE "mtp.*disab|disab.*mtp|accept" | tail -3' >> $LOG
  fi
  S 'docker rm -f spec-atlasmtp' >/dev/null 2>&1
fi

# 2. Atlas DFlash (z-lab drafter, cached)
if [ $(date +%s) -lt $CUT ]; then prep
  S "docker run -d --name spec-atlasdflash --gpus all --network host --memory 110g --memory-swap 110g \
     -e HF_HUB_OFFLINE=1 -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     avarok/atlas-gb10:latest serve --model-from-path $FP8_SNAP \
     --model-name qwen36-35b-fp8 --port 8890 --bind 0.0.0.0 --max-seq-len 32768 \
     --kv-cache-dtype bf16 --lm-head-dtype bf16 --gpu-memory-utilization 0.6 \
     --max-num-seqs 16 --max-batch-size 16 \
     --dflash --draft-model z-lab/Qwen3.6-35B-A3B-DFlash \
     --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
  if ready 8890 900 atlasdflash; then
    t2 8890 "Qwen3.6-35B-FP8-atlas-DFlash-throughput"
    S 'docker logs spec-atlasdflash 2>&1 | grep -iE "dflash|accept|draft" | tail -3' >> $LOG
  fi
  S 'docker rm -f spec-atlasdflash' >/dev/null 2>&1
fi

# 3. vLLM MTP (self-drafter from checkpoint mtp.* tensors — unverified, fail-fast)
if [ $(date +%s) -lt $CUT ]; then prep
  cat > /tmp/serve_vllm_mtp.sh <<EOF
#!/bin/bash
OUT=\$(python3 /patch_kv.py 2>&1); echo "\$OUT"
echo "\$OUT" | grep -qE "PATCHED|already patched" || exit 1
exec vllm serve $FP8_SNAP --served-model-name qwen36-35b-fp8 \
  --gpu-memory-utilization 0.6 --max-model-len 32768 --max-num-seqs 16 \
  --no-enable-prefix-caching \
  --speculative-config '{"method":"mtp","num_speculative_tokens":2}' \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 \
  --host 0.0.0.0 --port 8891
EOF
  scp -q /tmp/serve_vllm_mtp.sh $NODE:/tmp/serve_vllm_mtp.sh
  S "docker run -d --name spec-vllmmtp --gpus all --network host --ipc host --shm-size 8gb \
     --memory 110g --memory-swap 110g --entrypoint /bin/bash -e HF_HUB_OFFLINE=1 -e NVIDIA_DISABLE_REQUIRE=1 \
     -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     -v /tmp/patch_kv.py:/patch_kv.py:ro -v /tmp/serve_vllm_mtp.sh:/serve.sh:ro \
     ghcr.io/aeon-7/aeon-vllm-ultimate:latest /serve.sh" >/dev/null 2>&1
  ready 8891 1500 vllmmtp && t2 8891 "Qwen3.6-35B-FP8-vllm-MTP2-throughput"
  S 'docker rm -f spec-vllmmtp' >/dev/null 2>&1
fi

# 4. SGLang MTP (NEXTN algo — unverified for qwen3_5, fail-fast)
if [ $(date +%s) -lt $CUT ]; then prep
  cat > /tmp/serve_sglang_mtp.sh <<EOF
#!/bin/bash
exec python3 -m sglang.launch_server --model-path $FP8_SNAP \
  --served-model-name qwen36-35b-fp8 --context-length 32768 \
  --mem-fraction-static 0.6 --max-running-requests 16 --disable-radix-cache \
  --speculative-algorithm NEXTN --speculative-num-steps 2 --speculative-num-draft-tokens 3 \
  --tool-call-parser qwen3_coder --reasoning-parser qwen3 --host 0.0.0.0 --port 8892
EOF
  scp -q /tmp/serve_sglang_mtp.sh $NODE:/tmp/serve_sglang_mtp.sh
  S "docker run -d --name spec-sglangmtp --gpus all --network host --ipc host --shm-size 8gb \
     --memory 110g --memory-swap 110g --entrypoint /bin/bash -e HF_HUB_OFFLINE=1 \
     -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
     -v /tmp/serve_sglang_mtp.sh:/serve.sh:ro scitrera/dgx-spark-sglang:0.5.12 /serve.sh" >/dev/null 2>&1
  ready 8892 1500 sglangmtp && t2 8892 "Qwen3.6-35B-FP8-sglang-MTP-NEXTN-throughput"
  S 'docker rm -f spec-sglangmtp' >/dev/null 2>&1
fi

prep
log "=== NIGHT3 SPEC ROUND COMPLETE ==="
