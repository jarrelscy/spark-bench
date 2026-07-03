#!/usr/bin/env bash
# Detached DeepSeek think-ON v6 eval. Launch with:
#   setsid bash run_ds_thinkON.sh > LOG 2>&1 < /dev/null & disown
cd /home/raulwesche/projects/spark-bench
echo "[$(date -Is)] START DeepSeek think-ON v6 eval"
PYTHONUNBUFFERED=1 python3 spark_bench.py eval \
  --label "DeepSeek-V4-Flash-DSpark-thinkON-64scen-v6-2Spark" \
  --endpoint http://10.10.10.1:8888/v1 \
  --model deepseek-v4-flash-dspark \
  --thinking auto \
  --repeats 2 --tier all --timeout 900 \
  --topology "2x DGX Spark" --parallelism 2 --spec-decode mtp5 \
  --skip-throughput \
  --notes "DeepSeek-V4-Flash-DSpark 2-Spark b12x/MTP5/nvfp4_ds_mla, thinking ON, ~59 tok/s, v6 harness."
echo "[$(date -Is)] EVAL_EXIT=$?"
