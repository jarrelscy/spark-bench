#!/bin/bash
# Runs AFTER matrix_driver exits: if before 06:15, one bonus tier2 leg — vLLM+DFlash.
set -u
NODE=10.0.0.183
BENCH=/home/raulwesche/projects/spark-bench
SCRATCH=/tmp/claude-1000/-home-raulwesche/4dd56934-849c-4930-b8cf-ae2f3b995666/scratchpad
LOG=$SCRATCH/matrix-night/driver.log
export SPARK_BENCH_EXTRA_BODY='{"top_p":0.95,"top_k":20}'

while ps -p ${1:?driver pid} >/dev/null 2>&1; do sleep 60; done
CUTOFF=$(date -d "06:15" +%s); [ $(date +%s) -gt $CUTOFF ] && CUTOFF=$(date -d "tomorrow 06:15" +%s)
if [ $(date +%s) -gt $CUTOFF ]; then echo "[bonus] no slack — skipped" >> $LOG; exit 0; fi
grep -q "NIGHT COMPLETE" $LOG || { echo "[bonus] driver did not complete cleanly — skipping bonus" >> $LOG; exit 0; }

echo "[bonus $(date +%H:%M)] launching vLLM+DFlash tier2 taste" >> $LOG
timeout 25 ssh -o BatchMode=yes $NODE 'docker ps -aq | xargs -r docker rm -f >/dev/null 2>&1; sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'
scp -q $SCRATCH/serve_vllm_dflash.sh $NODE:/tmp/serve_vllm_dflash.sh
timeout 25 ssh -o BatchMode=yes $NODE "docker run -d --name bonus-dflash --gpus all --network host --ipc host --shm-size 8gb \
  --memory 110g --memory-swap 110g --entrypoint /bin/bash \
  -e NVIDIA_DISABLE_REQUIRE=1 \
  -v /home/raulwesche/.cache/huggingface:/root/.cache/huggingface:ro \
  -v /tmp/patch_kv.py:/patch_kv.py:ro -v /tmp/serve_vllm_dflash.sh:/serve.sh:ro \
  ghcr.io/aeon-7/aeon-vllm-ultimate:latest /serve.sh" >/dev/null 2>&1
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt 2400 ]; do
  c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 http://$NODE:8891/v1/models 2>/dev/null)
  [ "$c" = "200" ] && break
  st=$(timeout 15 ssh -o BatchMode=yes $NODE 'docker inspect -f "{{.State.Status}}" bonus-dflash 2>/dev/null')
  [ "$st" != "running" ] && [ -n "$st" ] && { echo "[bonus] dflash serve died" >> $LOG; exit 0; }
  sleep 10
done
[ "$c" != "200" ] && { echo "[bonus] dflash never ready" >> $LOG; timeout 20 ssh -o BatchMode=yes $NODE 'docker rm -f bonus-dflash' >/dev/null 2>&1; exit 0; }
echo "[bonus] dflash ready in $(( $(date +%s) - t0 ))s — tier2" >> $LOG
timeout 1800 python3 $BENCH/spark_bench.py tier2 --label "Qwen3.6-35B-FP8-vllm-DFlashK10-throughput" \
  --endpoint http://$NODE:8891/v1 --model qwen36-35b-fp8 \
  --contexts 1024,8192 --concurrency 1,8,16 --conc-context 1024 --gen-tokens 512 \
  --topology single --notes "BONUS spec-taste: z-lab DFlash K10 on matrix vLLM config; quality NOT yet spot-checked" >> $LOG 2>&1
echo "[bonus] tier2 done rc=$? — teardown" >> $LOG
timeout 25 ssh -o BatchMode=yes $NODE 'docker rm -f bonus-dflash >/dev/null 2>&1'
echo "[bonus] BONUS COMPLETE" >> $LOG
