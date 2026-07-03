#!/usr/bin/env bash
cd /home/raulwesche/projects/spark-bench
echo "[$(date -Is)] START Step-3.7-Flash native v6 eval"
PYTHONUNBUFFERED=1 python3 spark_bench.py eval --label "Step-3.7-Flash-NVFP4-MTP-vLLM-native-64scen-v6-2Spark" --endpoint http://10.0.0.229:8888/v1 --model Step-3.7-Flash-NVFP4-MTP --parallelism 2 --spec-decode mtp3 --timeout 900 --repeats 2 --temperature 0.3 --thinking auto --tier all --skip-throughput --topology "2x DGX Spark" --notes "Step-3.7-Flash-NVFP4 2-Spark TP2 MTP3 (MiaAI-Lab no-Ray recipe), native thinking auto, v6 harness."
echo "[$(date -Is)] EVAL_EXIT=$?"
