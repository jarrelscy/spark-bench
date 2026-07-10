#!/usr/bin/env bash
# Detached MiMo staging to idle pair (.120 head / .183 worker).
# Resumes weights rsync (.120->.183) and loads tonyd2wild image on both.
IMG=ghcr.io/tonyd2wild/mimo-v2.5-tp2-1m-nvfp4kv:20260620
TAR=/home/raulwesche/mimo_img.tar
echo "[$(date -Is)] resume MiMo weights .120 -> .183"
ssh -o BatchMode=yes 10.0.0.120 "rsync -a ~/.cache/huggingface/hub/models--lukealonso--MiMo-V2.5-NVFP4 10.10.10.5:~/.cache/huggingface/hub/" && echo "WEIGHTS_OK" || echo "WEIGHTS_FAIL"
echo -n "[$(date -Is)] .183 weights now: "; ssh -o BatchMode=yes 10.0.0.183 "du -sh ~/.cache/huggingface/hub/models--lukealonso--MiMo-V2.5-NVFP4 2>/dev/null | cut -f1"
echo "[$(date -Is)] save + load image to .120 and .183"
docker save "$IMG" > "$TAR"
ssh -o BatchMode=yes 10.10.10.7 "docker load" < "$TAR" && echo "IMG120_OK"
ssh -o BatchMode=yes 10.10.10.5 "docker load" < "$TAR" && echo "IMG183_OK"
rm -f "$TAR"
echo "[$(date -Is)] MIMO_STAGE_DONE"
