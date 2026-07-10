#!/bin/bash
# night4_fix.sh — retry the two failed NVFP4 cells after night3 spec round.
# Atlas: util 0.68 (capacity fix, documented asymmetry; numerics unchanged).
# SGLang: one retry WITHOUT explicit --quantization (auto-detect), fail-fast.
set -u
NODE=10.0.0.183
BENCH=/home/raulwesche/projects/spark-bench
SCRATCH=/tmp/claude-1000/-home-raulwesche/4dd56934-849c-4930-b8cf-ae2f3b995666/scratchpad
RES=$SCRATCH/matrix-night; LOG=$RES/driver.log
NVFP4_PATH=/models/qwen36-35b-nvfp4
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'
log(){ echo "[$(date +%H:%M:%S)] $*" >> $LOG; }
S(){ timeout 25 ssh -o BatchMode=yes $NODE "$@"; }

while ps -p ${1:?night3 pid} >/dev/null 2>&1; do sleep 120; done
CUT=$(date -d "07:00" +%s); [ $(date +%s) -gt $CUT ] && CUT=$(date -d "tomorrow 07:00" +%s)
log "=== NIGHT4: NVFP4 fix round ==="
prep(){ S 'docker ps -aq | xargs -r docker rm -f >/dev/null 2>&1; sleep 5; sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'; }
ready(){ local t0=$(date +%s) c
  while [ $(( $(date +%s) - t0 )) -lt $2 ]; do
    c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 http://$NODE:$1/v1/models 2>/dev/null)
    [ "$c" = "200" ] && { log "$3 ready $(( $(date +%s) - t0 ))s"; return 0; }
    st=$(S "docker inspect -f '{{.State.Status}}' fix-$3 2>/dev/null")
    [ "$st" != "running" ] && [ -n "$st" ] && { log "$3 died"; S "docker logs --tail 8 fix-$3 2>&1 | tail -5" >> $LOG; return 1; }
    sleep 5
  done; log "$3 timeout"; return 1; }
bench(){ # port legname label
  export SPARK_BENCH_DUMP_DIR=$RES/dump_$2; mkdir -p $SPARK_BENCH_DUMP_DIR
  timeout 900 python3 $BENCH/spark_bench.py tier2 --label "warmup-discard-$2" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-nvfp4 --contexts 1024,8192 \
    --concurrency 1,8,16 --conc-context 1024 --gen-tokens 64 --topology single --notes DISCARD >> $LOG 2>&1
  timeout 1800 python3 $BENCH/spark_bench.py tier2 --label "Qwen3.6-35B-$2-throughput" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-nvfp4 --contexts 1024,8192 \
    --concurrency 1,8,16 --conc-context 1024 --gen-tokens 512 --topology single \
    --notes "matrix fix round; harness 462e6cf" >> $LOG 2>&1
  log "$2 tier2 rc=$?"
  [ $(date +%s) -gt $(( CUT - 2400 )) ] && { log "$2 SKIP eval (cutoff)"; return; }
  timeout 12600 python3 $BENCH/spark_bench.py eval --label "$3" \
    --endpoint http://$NODE:$1/v1 --model qwen36-35b-nvfp4 --thinking off --repeats 2 \
    --skip-throughput --timeout 600 --topology single \
    --notes "matrix fix; pinned sampling; qwen3_coder; NOTE Atlas leg util 0.68 (capacity, numerics-neutral)" >> $LOG 2>&1
  log "$2 eval rc=$?"
  unset SPARK_BENCH_DUMP_DIR
}

# Atlas NVFP4 @ util 0.68
if [ $(date +%s) -lt $CUT ]; then prep
  log "=== fix: Atlas NVFP4 util 0.68 ==="
  S "docker run -d --name fix-atlas --gpus all --network host --memory 110g --memory-swap 110g \
     -e HF_HUB_OFFLINE=1 -v /home/raulwesche/models:/models:ro \
     avarok/atlas-gb10:latest serve --model-from-path $NVFP4_PATH \
     --model-name qwen36-35b-nvfp4 --port 8890 --bind 0.0.0.0 --max-seq-len 32768 \
     --kv-cache-dtype bf16 --lm-head-dtype bf16 --gpu-memory-utilization 0.68 \
     --max-num-seqs 16 --max-batch-size 16 --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
  ready 8890 600 atlas && bench 8890 "NVFP4-atlas-u068" "Qwen3.6-35B-NVFP4-atlas-thinkOFF-64scen-v6.1-1Spark"
  S 'docker rm -f fix-atlas' >/dev/null 2>&1
fi
# SGLang NVFP4 auto-detect retry
if [ $(date +%s) -lt $CUT ]; then prep
  log "=== fix: SGLang NVFP4 auto-quant ==="
  cat > /tmp/serve_sglang_nvfp4b.sh <<EOF
#!/bin/bash
exec python3 -m sglang.launch_server --model-path $NVFP4_PATH \
  --served-model-name qwen36-35b-nvfp4 --context-length 32768 \
  --mem-fraction-static 0.6 --max-running-requests 16 --disable-radix-cache \
  --tool-call-parser qwen3_coder --reasoning-parser qwen3 --host 0.0.0.0 --port 8892
EOF
  scp -q /tmp/serve_sglang_nvfp4b.sh $NODE:/tmp/serve_sglang_nvfp4b.sh
  S "docker run -d --name fix-sglang --gpus all --network host --ipc host --shm-size 8gb \
     --memory 110g --memory-swap 110g --entrypoint /bin/bash -e HF_HUB_OFFLINE=1 \
     -v /home/raulwesche/models:/models:ro -v /tmp/serve_sglang_nvfp4b.sh:/serve.sh:ro \
     scitrera/dgx-spark-sglang:0.5.12 /serve.sh" >/dev/null 2>&1
  ready 8892 900 sglang && bench 8892 "NVFP4-sglang0512-autoq" "Qwen3.6-35B-NVFP4-sglang0512-thinkOFF-64scen-v6.1-1Spark"
  S 'docker rm -f fix-sglang' >/dev/null 2>&1
fi
prep
log "=== NIGHT4 COMPLETE ==="
