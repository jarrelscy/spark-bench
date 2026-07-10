#!/usr/bin/env bash
CN=vllm_mimo_tp2
MODEL=/root/.cache/huggingface/hub/models--lukealonso--MiMo-V2.5-NVFP4/snapshots/a147dd04d6cf861e43b2d783dcde23b53ab7ee68
HEAD=10.10.10.7; WORK=10.10.10.5
log(){ echo "[$(date -Is)] $*"; }
log "launch.sh think flag: $(ssh -o BatchMode=yes 10.0.0.120 "grep enable_thinking ~/mimo-recipe/recipe/launch.sh | grep -oE 'enable_thinking\":(true|false)' | head -1")"
log "kill stale vLLM + ray stop on BOTH nodes (clears placement groups holding GPUs)"
ssh -o BatchMode=yes 10.0.0.120 "docker exec $CN bash -lc 'pkill -9 -f \"vllm serve\" 2>/dev/null; ray stop --force 2>/dev/null; sleep 4'"
ssh -o BatchMode=yes 10.0.0.183 "docker exec $CN bash -lc 'pkill -9 -f \"vllm serve\" 2>/dev/null; ray stop --force 2>/dev/null; sleep 4'"
sleep 6
log "restart Ray head .120"
ssh -o BatchMode=yes 10.0.0.120 "docker exec $CN bash -lc 'ray start --head --port=6379 --node-ip-address=$HEAD --num-gpus=1 --object-store-memory=1073741824'" 2>&1 | tail -1
sleep 6
log "restart Ray worker .183"
ssh -o BatchMode=yes 10.0.0.183 "docker exec $CN bash -lc 'ray start --address=$HEAD:6379 --node-ip-address=$WORK --num-gpus=1 --object-store-memory=1073741824'" 2>&1 | tail -1
sleep 6
log "ray status: $(ssh -o BatchMode=yes 10.0.0.120 "docker exec $CN ray status 2>&1 | grep -iE 'GPU' | head -1")"
log "launch vLLM think-ON"
ssh -o BatchMode=yes 10.0.0.120 "docker exec -d $CN bash -lc 'cd /workspace/recipe && source env.sh && export MODEL_PATH=$MODEL SERVED_MODEL_NAME=MiMo-V2.5-NVFP4 HEAD_ROCE_IP=$HEAD VLLM_HOST_IP=$HEAD TENSOR_PARALLEL_SIZE=2 MAX_MODEL_LEN=200000 NCCL_IB_DISABLE=1 NCCL_NET=Socket NCCL_SOCKET_IFNAME=enp1s0f0np0 GLOO_SOCKET_IFNAME=enp1s0f0np0 && bash launch.sh > /workspace/vllm_thinkON.log 2>&1'"
log "MIMO_THINKON_RAYRESET_DONE (loading; poll http://$HEAD:8000/v1/models)"
