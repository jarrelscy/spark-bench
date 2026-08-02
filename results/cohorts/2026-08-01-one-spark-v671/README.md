# One-Spark v6.7.1 Qualification Sweep

This archive preserves the single-DGX-Spark sweep run on 2026-08-01 and
2026-08-02. The live leaderboard publishes only qualified rows from this
cohort; older suite versions remain in Git history and the master CSV.

## Fixed contract

- SparkBench: `11d21bf`
- Methodology: `v6.7.1-challenge`
- Workload: 20 discriminating scenarios across 10 domains
- Repeats: 3
- Temperature: 0.3
- Thinking: off where supported
- Topology: one physical DGX Spark, TP1
- Throughput sweep: skipped
- Qualification: 12/12 golden gate, tool preflight, zero transport errors,
  complete scenario scores and visual artifacts, clean quarantine status

## Outcome

- 40 attempted run configurations
- 29 qualified and ranked
- 2 quarantined for flat-domain score patterns
- 9 aborted during model or tool-parser preflight

`results-qualified.tsv` is the website input. `results-all.tsv` and
`results-manifest.json` preserve every attempt and its rejection reason.
`SHA256SUMS` binds all archived evidence files.

## Contents

| Path | Purpose |
|---|---|
| `results-qualified.tsv` | Qualified ranking used by the live site |
| `results-all.tsv` | Qualified, quarantined, and aborted attempts |
| `results-manifest.json` | Machine-readable qualification record |
| `matrix.tsv` | Planned model/configuration matrix and terminal status |
| `queue-status.tsv` | Serialized execution log |
| `raw/` | Original CSVs, reports, transcripts, visuals, and markers |
| `logs/` | Launch, staging, benchmark, and failure logs |
| `build-results.py` | Qualification gate that produced the tables |
| `SHA256SUMS` | File-integrity manifest |

Scores from earlier SparkBench methodologies are not numerically comparable
with this cohort.
