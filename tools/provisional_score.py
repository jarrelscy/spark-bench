"""Offline v7 component reconstruction. No server requests or transcript uploads."""
import argparse
import collections
import json
import math
from pathlib import Path
import statistics
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_suite as ev


def aggregate(records, repeats=2):
    groups = collections.defaultdict(list)
    for r in records:
        groups[r['scenario_id']].append(r)
    scenarios = []
    for sid, rows in groups.items():
        if len({r['repeat'] for r in rows}) != len(rows):
            raise ValueError(f'Duplicate repeat: {sid}')
        if {r['repeat'] for r in rows} != set(range(1, repeats+1)):
            continue
        scores = [r['score'] for r in rows]
        m = rows[0]
        group = ('informational' if sid in ev.CONTENT_REFUSAL_SCENARIOS else
                 'calibration' if m['domain'] == 'safety' else m['group'])
        scenarios.append(dict(id=sid, group=group, difficulty=m['difficulty'],
            score=statistics.mean(scores), consistency=max(0., 1-2*statistics.pstdev(scores)),
            passed=any(s >= .5 for s in scores), error=any(r['error'] for r in rows),
            latency=statistics.median(r['latency_s'] for r in rows),
            eff=statistics.mean(r['efficiency'] for r in rows)))
    if not scenarios:
        raise ValueError('No complete scenarios')
    def weighted(group):
        rs=[r for r in scenarios if r['group']==group]
        den=sum(r['difficulty'] for r in rs)
        return 100*sum(r['score']*r['difficulty'] for r in rs)/den if den else None
    # Match run_suite: reliability excludes scenarios whose LAST reason is error.
    last={k:max(v,key=lambda r:r['repeat']) for k,v in groups.items()}
    rel=[r['consistency'] for r in scenarios if r['passed'] and not last[r['id']]['error']]
    med=statistics.median(r['latency'] for r in scenarios)
    comp=dict(quality=weighted('capability'), calibration=weighted('calibration'),
        reliability=100*statistics.mean(rel) if rel else 0.,
        efficiency=100*statistics.mean(r['eff'] for r in scenarios),
        responsiveness=100/(1+med/20))
    return dict(status='provisional_completed_scenarios_only', n_scenarios=len(scenarios),
        components=comp, median_latency_s=med,
        truescore=ev.weighted_component_average(comp,ev.DEFAULT_WEIGHTS,tuple(ev.DEFAULT_WEIGHTS)),
        weights=ev.DEFAULT_WEIGHTS)


def extract(directory, timeout=7200):
    meta={s['id']:s for s in ev.SCENARIOS}
    records=[]
    for p in sorted(Path(directory).glob('*.json')):
        d=json.loads(p.read_text()); m=meta[d['scenario_id']];resp=d['response']
        error=d['reason'].startswith('error:')
        if error:
            latency,eff=timeout,0.
        else:
            if resp is None or resp.get('total_seconds') is None:
                raise ValueError(f'Missing latency: {p.name}')
            latency=resp['total_seconds']
            if m.get('agentic'):
                eff=1.  # Preserve _run_agentic's existing scoring rule.
            else:
                a=ev._est_tokens(resp.get('text'));r=ev._est_tokens(resp.get('reasoning'))
                eff=a/(a+r) if a+r else 1.
        if not math.isfinite(latency) or latency < 0:
            raise ValueError(f'Invalid latency: {p.name}')
        records.append(dict(scenario_id=d['scenario_id'],repeat=d['repeat'],score=d['score'],
            domain=m['domain'],group=m['group'],difficulty=m['difficulty'],
            latency_s=latency,efficiency=eff,error=error))
    return records

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    src=p.add_mutually_exclusive_group(required=True)
    src.add_argument('--transcripts');src.add_argument('--records')
    p.add_argument('--output',required=True)
    args=p.parse_args()
    records=extract(args.transcripts) if args.transcripts else json.loads(Path(args.records).read_text())['records']
    Path(args.output).write_text(json.dumps(dict(overall=aggregate(records),records=records),indent=2)+'\n')
