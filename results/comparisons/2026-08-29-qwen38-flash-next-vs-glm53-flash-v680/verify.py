#!/usr/bin/env python3
"""Verify the published SparkBench v6.8.0 comparison package."""
import csv
import hashlib
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEIGHTS = {
    'quality': 0.55, 'calibration': 0.25, 'reliability': 0.15,
    'efficiency': 0.015, 'responsiveness': 0.035,
}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def weighted_average(values, keys):
    active = {k: WEIGHTS[k] for k in keys if values.get(k) is not None}
    total = sum(active.values())
    return sum(values[k] * active[k] for k in active) / total


def recompute(rows):
    by_scenario = {}
    for row in rows:
        by_scenario.setdefault(row['scenario_id'], []).append(row)
    scenarios = []
    for scenario_id, repeats in by_scenario.items():
        scores = [float(r['score']) for r in repeats]
        consistency = max(0.0, 1 - 2 * statistics.pstdev(scores))
        scenarios.append({
            'id': scenario_id,
            'group': repeats[0]['group'],
            'difficulty': float(repeats[0]['difficulty']),
            'score': statistics.mean(scores),
            'consistency': consistency,
            'pass_rate': sum(s >= 0.5 for s in scores) / len(scores),
            'latency': statistics.median(float(r['latency_seconds']) for r in repeats),
            'efficiency': statistics.mean(float(r['efficiency_ratio']) for r in repeats),
        })

    def quality_for(group):
        selected = [r for r in scenarios if r['group'] == group]
        weight = sum(r['difficulty'] for r in selected)
        return 100 * sum(r['score'] * r['difficulty'] for r in selected) / weight

    quality = quality_for('capability')
    calibration = quality_for('calibration')
    rel_pool = [r for r in scenarios if r['pass_rate'] > 0]
    reliability = 100 * statistics.mean(r['consistency'] for r in rel_pool)
    efficiency = 100 * statistics.mean(r['efficiency'] for r in scenarios)
    median_latency = statistics.median(r['latency'] for r in scenarios)
    responsiveness = 100 / (1 + median_latency / 20)
    components = {
        'quality': quality, 'calibration': calibration,
        'reliability': reliability, 'efficiency': efficiency,
        'responsiveness': responsiveness,
    }
    components['capability_score'] = quality
    components['operational_score'] = weighted_average(
        components, ('efficiency', 'responsiveness'))
    components['truescore'] = weighted_average(components, tuple(WEIGHTS))
    components['median_scenario_latency_seconds'] = median_latency
    return components


def main():
    checksum_rows = []
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split(None, 1)
        name = name.strip()
        actual = sha256(HERE / name)
        if actual != digest:
            raise SystemExit(f'checksum mismatch: {name}')
        checksum_rows.append(name)

    scorecard = json.loads((HERE / 'scorecard.json').read_text())
    failures = json.loads((HERE / 'failures.json').read_text())
    hashes = json.loads((HERE / 'transcript-hashes.json').read_text())
    methodology = json.loads((HERE / 'methodology.json').read_text())

    if scorecard['methodology'] != 'v6.8.0-full-uncapped':
        raise SystemExit('wrong scorecard methodology')
    if methodology['version'] != 'v6.8.0-full-uncapped':
        raise SystemExit('wrong methodology version')

    with (HERE / 'scenario-scores.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 304:
        raise SystemExit(f'expected 304 per-repeat rows, got {len(rows)}')
    for deployment in ('qwen-spec-off', 'glm-dflash2-k7'):
        selected = [r for r in rows if r['deployment'] == deployment]
        identities = {(r['scenario_id'], r['repeat']) for r in selected}
        if len(selected) != 152 or len(identities) != 152:
            raise SystemExit(f'invalid coverage for {deployment}')

    qwen_hashes = hashes['deployments']['qwen-spec-off']
    glm_hashes = hashes['deployments']['glm-dflash2-k7']
    if len(qwen_hashes) != 152 or len(glm_hashes) != 152:
        raise SystemExit('transcript hash coverage mismatch')

    glm_failures = failures['glm_validated_model_failures']
    if len(glm_failures) != 4:
        raise SystemExit('expected four GLM corrections')
    failed_names = {x['transcript'].removesuffix('.json') for x in glm_failures}
    corrected_rows = [r for r in rows if r['corrected_model_failure'] == 'true']
    corrected_names = {f"{r['scenario_id']}-repeat-{r['repeat']}" for r in corrected_rows}
    if corrected_names != failed_names:
        raise SystemExit('corrected row identities do not match failure manifest')
    if any(float(r['score']) != 0.0 for r in corrected_rows):
        raise SystemExit('corrected model failure has a non-zero score')

    qwen = scorecard['deployments']['qwen3.8-flash-next-spec-off']
    glm = scorecard['deployments']['glm-5.3-flash-dflash2-k7']
    if not qwen['valid'] or not glm['valid'] or qwen['truescore'] <= glm['truescore']:
        raise SystemExit('scorecard validity/winner invariant failed')

    for deployment, expected in [('qwen-spec-off', qwen), ('glm-dflash2-k7', glm)]:
        calculated = recompute([r for r in rows if r['deployment'] == deployment])
        for metric, value in calculated.items():
            if abs(value - expected[metric]) > 1e-8:
                raise SystemExit(
                    f'recomputed {deployment} {metric} mismatch: {value} != {expected[metric]}')

    print(json.dumps({
        'status': 'PASS',
        'checksummed_files': len(checksum_rows),
        'per_repeat_rows': len(rows),
        'transcript_hashes': len(qwen_hashes) + len(glm_hashes),
        'glm_corrected_model_failures': len(glm_failures),
        'scores_recomputed_from_public_rows': True,
        'qwen_truescore': qwen['truescore'],
        'glm_truescore': glm['truescore'],
    }, indent=2))


if __name__ == '__main__':
    main()
