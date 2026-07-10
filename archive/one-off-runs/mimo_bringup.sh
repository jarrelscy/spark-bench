#!/usr/bin/env bash
set -uo pipefail
RSRC=/home/raulwesche/projects/MiMo-V2.5-TP2-1M-NVFP4-KV-2xDGX-Spark
IMG=ghcr.io/tonyd2wild/mimo-v2.5-tp2-1m-nvfp4kv:20260620
CN=vllm_mimo_tp2
MODEL=/root/.cache/huggingface/hub/models--lukealonso--MiMo-V2.5-NVFP4/snapshots/a147dd04d6cf861e43b2d783dcde23b53ab7ee68
HEAD=10.10.10.7; WORK=10.10.10.5
SOCK="-e NCCL_IB_DISABLE=1 -e NCCL_NET=Socket -e NCCL_SOCKET_IFNAME=enp1s0f0np0 -e GLOO_SOCKET_IFNAME=enp1s0f0np0"
log(){ echo "[$(date -Is)] $*"; }

log "[1] copy recipe -> .120/.183"
rsync -a "$RSRC/" 10.10.10.7:~/mimo-recipe/ && rsync -a "$RSRC/" 10.10.10.5:~/mimo-recipe/ && echo "  ok"

log "[2] start containers (clean first)"
for h in 10.0.0.120 10.0.0.183; do ssh -o BatchMode=yes $h "docker rm -f $CN 2>/dev/null" >/dev/null 2>&1; done
ssh -o BatchMode=yes 10.0.0.120 "docker run -d --name $CN --gpus all --network host --ipc host --shm-size 16g --ulimit memlock=-1 -e VLLM_HOST_IP=$HEAD $SOCK -v \$HOME/.cache/huggingface:/root/.cache/huggingface -v \$HOME/mimo-recipe/recipe:/workspace/recipe $IMG sleep infinity" && echo "  .120 up"
ssh -o BatchMode=yes 10.0.0.183 "docker run -d --name $CN --gpus all --network host --ipc host --shm-size 16g --ulimit memlock=-1 -e VLLM_HOST_IP=$WORK $SOCK -v \$HOME/.cache/huggingface:/root/.cache/huggingface -v \$HOME/mimo-recipe/recipe:/workspace/recipe $IMG sleep infinity" && echo "  .183 up"

log "[3] apply-mods on both"
ssh -o BatchMode=yes 10.0.0.120 "cd ~/mimo-recipe/recipe && bash apply-mods.sh $CN" 2>&1 | tail -2
ssh -o BatchMode=yes 10.0.0.183 "cd ~/mimo-recipe/recipe && bash apply-mods.sh $CN" 2>&1 | tail -2

log "[4] ray head .120 / worker .183"
ssh -o BatchMode=yes 10.0.0.120 "docker exec $CN bash -lc 'ray stop --force >/dev/null 2>&1; ray start --head --port=6379 --node-ip-address=$HEAD --num-gpus=1 --object-store-memory=1073741824'" 2>&1 | tail -1
ssh -o BatchMode=yes 10.0.0.183 "docker exec $CN bash -lc 'ray stop --force >/dev/null 2>&1; ray start --address=$HEAD:6379 --node-ip-address=$WORK --num-gpus=1 --object-store-memory=1073741824'" 2>&1 | tail -1
log "[5] ray status"; ssh -o BatchMode=yes 10.0.0.120 "docker exec $CN ray status 2>&1 | grep -iE 'GPU' | head -2"

log "[6] launch vLLM MiMo TP2 (thinkOFF default) on head .120, 200K ctx"
ssh -o BatchMode=yes 10.0.0.120 "docker exec -d $CN bash -lc 'cd /workspace/recipe && source env.sh && export MODEL_PATH=$MODEL SERVED_MODEL_NAME=MiMo-V2.5-NVFP4 HEAD_ROCE_IP=$HEAD VLLM_HOST_IP=$HEAD TENSOR_PARALLEL_SIZE=2 MAX_MODEL_LEN=200000 && export NCCL_IB_DISABLE=1 NCCL_NET=Socket NCCL_SOCKET_IFNAME=enp1s0f0np0 GLOO_SOCKET_IFNAME=enp1s0f0np0 && bash launch.sh > /workspace/vllm.log 2>&1'"
log "MIMO_LAUNCH_INITIATED (head loading ~15-25min; poll http://$HEAD:8000/v1/models)"
