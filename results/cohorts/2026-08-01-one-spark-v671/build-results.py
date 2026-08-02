#!/usr/bin/env python3
"""Build a qualification-aware leaderboard from SparkBench CSV evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


EXPECTED_GRADER = "11d21bf"
EXPECTED_METHOD = "v6.7.1-challenge"
EXPECTED_REPEATS = "3"


def metric(rows: list[dict[str, str]], workload: str, name: str) -> str:
    values = [r["value"] for r in rows if r["workload"] == workload and r["metric"] == name]
    return values[-1] if values else ""


def parse_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def classify(rows: list[dict[str, str]], csv_path: Path) -> dict[str, object]:
    first = rows[0]
    done_marker = csv_path.parent / "runs" / f"{first['run_id']}.DONE"
    aborted = metric(rows, "provenance", "aborted")
    golden = metric(rows, "provenance", "golden_gate")
    grader = metric(rows, "provenance", "grader_git")
    preflight = metric(rows, "provenance", "preflight_tool_probe")
    quarantine = metric(rows, "provenance", "quarantine")
    methodology = metric(rows, "provenance", "methodology")
    run_valid = metric(rows, "provenance", "run_valid")
    repeats = metric(rows, "provenance", "repeats")
    error_rate = metric(rows, "provenance", "error_rate")
    score = metric(rows, "overall", "truescore")
    score_rows = [r for r in rows if r["metric"] == "score" and r["unit"] == "frac"]
    artifacts = [Path(r["value"]) for r in rows if r["metric"] == "artifact"]
    missing_artifacts = [str(p) for p in artifacts if not p.is_file()]

    reasons: list[str] = []
    if aborted:
        reasons.append(f"aborted:{aborted}")
    if golden != "PASS":
        reasons.append(f"golden_gate:{golden or 'missing'}")
    if grader != EXPECTED_GRADER:
        reasons.append(f"grader_git:{grader or 'missing'}")
    if preflight != "PASS":
        reasons.append(f"tool_preflight:{preflight or 'missing'}")
    if methodology != EXPECTED_METHOD:
        reasons.append(f"methodology:{methodology or 'missing'}")
    if run_valid != "PASS":
        reasons.append(f"run_valid:{run_valid or 'missing'}")
    if repeats != EXPECTED_REPEATS:
        reasons.append(f"repeats:{repeats or 'missing'}")
    if error_rate != "0.0":
        reasons.append(f"error_rate:{error_rate or 'missing'}")
    if quarantine != "clean":
        reasons.append(f"quarantine:{quarantine or 'missing'}")
    if not score:
        reasons.append("truescore:missing")
    if first["topology"] != "single-spark" or first["parallelism"] != "TP1":
        reasons.append(f"topology:{first['topology']}/{first['parallelism']}")
    if len(score_rows) != 20:
        reasons.append(f"scenario_scores:{len(score_rows)}")
    if missing_artifacts:
        reasons.append(f"missing_artifacts:{len(missing_artifacts)}")
    if not done_marker.is_file():
        reasons.append("done_marker:missing")

    timestamps = [t for t in (parse_time(r["timestamp"]) for r in rows) if t]
    duration = (max(timestamps) - min(timestamps)).total_seconds() if timestamps else None
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    return {
        "run_id": first["run_id"],
        "model": first["model"],
        "label": first["label"],
        "endpoint": first["endpoint"],
        "spec_decode": first["spec_decode"],
        "score": float(score) if score else None,
        "quality": metric(rows, "overall", "quality"),
        "calibration": metric(rows, "overall", "calibration"),
        "reliability": metric(rows, "overall", "reliability"),
        "median_latency_s": metric(rows, "overall", "median_latency"),
        "duration_s": duration,
        "scenario_scores": len(score_rows),
        "artifact_count": len(artifacts),
        "missing_artifacts": missing_artifacts,
        "done_marker": str(done_marker),
        "status": "qualified" if not reasons else ";".join(reasons),
        "csv": str(csv_path),
        "csv_sha256": digest,
    }


def write_tsv(path: Path, records: list[dict[str, object]]) -> None:
    fields = [
        "rank", "status", "score", "quality", "calibration", "reliability",
        "median_latency_s", "duration_s", "model", "spec_decode", "label",
        "endpoint", "scenario_scores", "artifact_count", "run_id", "csv_sha256", "csv",
        "done_marker",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, dialect="excel-tab", extrasaction="ignore")
        writer.writeheader()
        for index, record in enumerate(records, 1):
            writer.writerow({"rank": index, **record})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("/Users/wesche/projects/spark-bench-v671-runs/2026-08-01-one-spark-sweep"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    grouped: dict[tuple[Path, str], list[dict[str, str]]] = defaultdict(list)
    for csv_path in sorted(args.run_root.rglob("spark_bench.csv")):
        with csv_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                grouped[(csv_path, row["run_id"])].append(row)

    records = [classify(rows, path) for (path, _), rows in grouped.items()]
    records.sort(key=lambda item: (item["score"] is not None, item["score"] or -1), reverse=True)
    qualified = [record for record in records if record["status"] == "qualified"]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(args.out_dir / "results-all.tsv", records)
    write_tsv(args.out_dir / "results-qualified.tsv", qualified)
    (args.out_dir / "results-manifest.json").write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"qualified={len(qualified)} total_runs={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
