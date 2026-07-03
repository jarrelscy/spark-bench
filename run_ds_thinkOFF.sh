#!/usr/bin/env bash
cd /home/raulwesche/projects/spark-bench
echo "[$(date -Is)] START DeepSeek think-OFF v6 eval"
PYTHONUNBUFFERED=1 python3 spark_bench.py eval \
  --label "DeepSeek-V4-Flash-DSpark-thinkOFF-64scen-v6-2Spark" \
  --endpoint http://10.10.10.1:8888/v1 --model deepseek-v4-flash-dspark \
  --thinking off --repeats 2 --tier all --timeout 900 \
  --topology "2x DGX Spark" --parallelism 2 --spec-decode mtp5 --skip-throughput \
  --notes "DeepSeek-V4-Flash-DSpark 2-Spark b12x/MTP5/nvfp4_ds_mla, thinking OFF, v6 harness. (think-ON hung twice at structured-hard.)"
echo "[$(date -Is)] EVAL_EXIT=$?"
