#!/usr/bin/env bash
cd /home/raulwesche/projects/spark-bench
echo "[$(date -Is)] START MiMo think-OFF v6 eval"
PYTHONUNBUFFERED=1 python3 spark_bench.py eval \
  --label "MiMo-V2.5-NVFP4-vLLM-thinkOFF-64scen-v6-2Spark" \
  --endpoint http://10.10.10.7:8000/v1 --model MiMo-V2.5-NVFP4 \
  --thinking off --repeats 2 --tier all --timeout 900 \
  --topology "2x DGX Spark" --parallelism 2 --spec-decode mtp1 --skip-throughput \
  --notes "MiMo-V2.5-NVFP4 2-Spark TP2 MTP1, thinking OFF, idle-pair .120/.183, v6 harness."
echo "[$(date -Is)] EVAL_EXIT=$?"
