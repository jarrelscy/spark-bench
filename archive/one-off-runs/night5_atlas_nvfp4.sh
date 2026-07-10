#!/bin/bash
# night5 — Atlas NVFP4 eval retry with TIGHT per-request timeout (stalls -> scored failures).
set -u
NODE=10.0.0.183; BENCH=/home/raulwesche/projects/spark-bench
SCRATCH=/tmp/claude-1000/-home-raulwesche/4dd56934-849c-4930-b8cf-ae2f3b995666/scratchpad
RES=$SCRATCH/matrix-night; LOG=$RES/driver.log
NVFP4_PATH=/models/qwen36-35b-nvfp4
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'
export SPARK_BENCH_DUMP_DIR=$RES/dump_NVFP4-atlas-retry; mkdir -p $SPARK_BENCH_DUMP_DIR
log(){ echo "[$(date +%H:%M:%S)] $*" >> $LOG; }
S(){ timeout 25 ssh -o BatchMode=yes $NODE "$@"; }
CUT=$(date -d "07:30" +%s); [ $(date +%s) -gt $CUT ] && CUT=$(date -d "tomorrow 07:30" +%s)
[ $(date +%s) -gt $CUT ] && { log "night5 no time"; exit 0; }
S 'docker ps -aq | xargs -r docker rm -f >/dev/null 2>&1; sleep 5; sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'
log "=== NIGHT5: Atlas NVFP4 eval retry (timeout 180) ==="
S "docker run -d --name n5-atlas --gpus all --network host --memory 110g --memory-swap 110g \
   -e HF_HUB_OFFLINE=1 -v /home/raulwesche/models:/models:ro \
   avarok/atlas-gb10:latest serve --model-from-path $NVFP4_PATH \
   --model-name qwen36-35b-nvfp4 --port 8890 --bind 0.0.0.0 --max-seq-len 32768 \
   --kv-cache-dtype bf16 --lm-head-dtype bf16 --gpu-memory-utilization 0.68 \
   --max-num-seqs 16 --max-batch-size 16 --tool-call-parser qwen3_coder --disable-tool-grammar true" >/dev/null 2>&1
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt 600 ]; do
  [ "$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 http://$NODE:8890/v1/models 2>/dev/null)" = "200" ] && break
  sleep 5
done
log "n5 atlas ready $(( $(date +%s) - t0 ))s — eval timeout180"
timeout 9000 python3 $BENCH/spark_bench.py eval --label "Qwen3.6-35B-NVFP4-atlas-t180-thinkOFF-64scen-v6.1-1Spark" \
  --endpoint http://$NODE:8890/v1 --model qwen36-35b-nvfp4 --thinking off --repeats 2 \
  --skip-throughput --timeout 180 --topology single \
  --notes "Atlas NVFP4 util0.68; per-req timeout 180s — long-gen stalls (137s watchdog) score as failures; SEE atlas-nvfp4-finding.md; compare vs FP8 81.9" >> $LOG 2>&1
log "n5 eval rc=$?"
S 'docker rm -f n5-atlas >/dev/null 2>&1'
log "=== NIGHT5 COMPLETE ==="
