#!/usr/bin/env bash
CN=vllm_mimo_tp2
MODEL=/root/.cache/huggingface/hub/models--lukealonso--MiMo-V2.5-NVFP4/snapshots/a147dd04d6cf861e43b2d783dcde23b53ab7ee68
log(){ echo "[$(date -Is)] $*"; }
log "flip launch.sh -> enable_thinking:true"
ssh -o BatchMode=yes 10.0.0.120 "sed -i '/enable_thinking/s/false/true/' ~/mimo-recipe/recipe/launch.sh && grep -n enable_thinking ~/mimo-recipe/recipe/launch.sh"
log "kill current vLLM engine in container (Ray cluster stays up)"
ssh -o BatchMode=yes 10.0.0.120 "docker exec $CN bash -lc 'pkill -9 -f \"vllm serve\" 2>/dev/null; sleep 12; echo killed'"
log "relaunch vLLM think-ON"
ssh -o BatchMode=yes 10.0.0.120 "docker exec -d $CN bash -lc 'cd /workspace/recipe && source env.sh && export MODEL_PATH=$MODEL SERVED_MODEL_NAME=MiMo-V2.5-NVFP4 HEAD_ROCE_IP=10.10.10.7 VLLM_HOST_IP=10.10.10.7 TENSOR_PARALLEL_SIZE=2 MAX_MODEL_LEN=200000 NCCL_IB_DISABLE=1 NCCL_NET=Socket NCCL_SOCKET_IFNAME=enp1s0f0np0 GLOO_SOCKET_IFNAME=enp1s0f0np0 && bash launch.sh > /workspace/vllm_thinkON.log 2>&1'"
log "MIMO_THINKON_RELAUNCH_INITIATED (loading; poll http://10.10.10.7:8000/v1/models)"
