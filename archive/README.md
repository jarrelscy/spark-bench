# archive/

Historical / one-off material kept for reference. **Nothing here is required to run a normal v6.4c eval.**

| Folder | What it is |
|--------|------------|
| `one-off-runs/` | Night drivers, model-specific relaunch scripts, matrix jobs |
| `probes/` | DFlash/MTP/category/stream probes used during tuning |
| `lab/` | MOA proxies, rescoring, agentic watchers, artifact generators |
| `internal/` | Site export, Hermes packaging, private notes (often gitignored) |

To run the benchmark:

```bash
python3 spark_bench.py eval --label ... --endpoint ... --model ...
python3 golden_gate.py
```

Deploy / bringup logs from early multi-node work live under `results/archive/deploy-logs/` (not the board CSV).
