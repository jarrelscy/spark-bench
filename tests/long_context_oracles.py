"""Hand-written LC-03 answer and defective outputs; NOT model-run evidence.

Do not import the production EXPECTED table: the golden gate must be capable
of detecting a corrupted production expectation as well as an auto-pass grader.
"""
import copy
import json

REFERENCE = '''{
  "as_of": "2026-09-10T12:00:00Z",
  "answers": [
    {"ticket_id":"T-417","account_id":"c-0721","policy_id":"pol-eu",
     "status":"resolved","revision":"r2","route":"route-K27","retention_days":45,
     "evidence":["D007","D082","D029","D063","D096"]},
    {"ticket_id":"T-418","account_id":"c-072I","policy_id":"pol-us",
     "status":"resolved","revision":"r2","route":"route-H41","retention_days":30,
     "evidence":["D101","D019","D070","D042","D009","D091","D058"]},
    {"ticket_id":"T-419","account_id":"c-0930","policy_id":"pol-finch",
     "status":"conflict","revision":null,"route":null,"retention_days":null,
     "evidence":["D047","D109","D012","D031","D088","D076","D024"]},
    {"ticket_id":"T-420","account_id":"c-0940","policy_id":"pol-ap",
     "status":"insufficient_evidence","revision":null,"route":null,"retention_days":null,
     "evidence":["D066","D003","D099"]}
  ]
}'''


def defective_answers():
    reference = json.loads(REFERENCE)
    mutants = {}

    def change(name, index, **changes):
        answer = copy.deepcopy(reference)
        answer['answers'][index].update(changes)
        mutants[name] = json.dumps(answer)

    change('wrong-scope-approval', 0, revision='r3', route='route-P63', retention_days=7,
           evidence=['D007','D082','D029','D107','D021'])
    change('future-effective-revision', 0, revision='r4', route='route-D19', retention_days=14,
           evidence=['D007','D082','D029','D034','D055'])
    change('approval-after-cutoff', 0, revision='r5', route='route-Q52', retention_days=21,
           evidence=['D007','D082','D029','D078','D111'])
    change('inclusive-expiry', 0, revision='r6', route='route-M84', retention_days=90,
           evidence=['D007','D082','D029','D015','D093'])
    change('withdrawal-ignored', 1, revision='r4', route='route-Z08', retention_days=3,
           evidence=['D101','D019','D070','D091','D036'])
    change('latest-approval-or-highest-label', 1, revision='r9', route='route-B76', retention_days=120,
           evidence=['D101','D019','D070','D004','D104','D091','D058'])
    change('same-name-wrong-identity', 1, account_id='c-0721', policy_id='pol-eu',
           route='route-K27', retention_days=45, evidence=['D101','D082','D029','D063','D096'])
    change('normalize-literal-id', 1, account_id='c-0721')
    change('break-conflict-by-label', 2, status='resolved', revision='v9', route='route-N92',
           retention_days=15, evidence=['D047','D109','D012','D076','D024'])
    change('omit-conflicting-evidence', 2, evidence=['D047','D109','D012','D031','D088'])
    change('conflict-treated-as-missing', 2, status='insufficient_evidence')
    change('invent-missing-policy', 3, status='resolved', revision='r1', route='route-A11', retention_days=30)
    change('missing-treated-as-conflict', 3, status='conflict')
    change('unsupported-route-on-conflict', 2, route='route-C35')
    change('no-citations', 0, evidence=[])
    change('right-answer-wrong-citations', 0, evidence=['D007','D082','D029','D107','D021'])
    change('missing-withdrawal-proof', 1, evidence=['D101','D019','D070','D042','D009'])
    change('fabricated-citation', 0, evidence=['D007','D082','D029','D063','D999'])
    change('duplicate-citation', 0, evidence=['D007','D082','D029','D063','D096','D096'])
    change('citation-dump', 0, evidence=[f'D{i:03d}' for i in range(1,113)])
    change('retention-as-string', 0, retention_days='45')
    change('retention-as-float', 0, retention_days=45.0)
    change('bool-not-int', 0, retention_days=True)
    change('wrong-retention-only', 0, retention_days=46)
    change('extra-answer-key', 0, confidence=1)
    abstain = copy.deepcopy(reference)
    for answer in abstain['answers']:
        answer.update(status='insufficient_evidence', revision=None, route=None, retention_days=None)
    mutants['abstain-on-everything'] = json.dumps(abstain)
    duplicate = copy.deepcopy(reference)
    duplicate['answers'][1] = duplicate['answers'][0]
    mutants['duplicate-ticket'] = json.dumps(duplicate)
    reordered = copy.deepcopy(reference)
    reordered['answers'].reverse()
    mutants['wrong-request-order'] = json.dumps(reordered)
    mutants['old-passcode'] = 'VESPER-3318'
    mutants['fenced-json'] = '```json\n' + REFERENCE + '\n```'
    mutants['contradictory-prose-after-answer'] = REFERENCE + '\nActually use route-P63.'
    mutants['duplicate-json-key'] = REFERENCE.replace('"as_of":', '"as_of":"wrong","as_of":', 1)
    mutants['nonfinite-json'] = REFERENCE.replace('"retention_days":45', '"retention_days":NaN')
    mutants['missing-ticket'] = json.dumps(dict(reference, answers=reference['answers'][:-1]))
    mutants['wrong-cutoff'] = json.dumps(dict(reference, as_of='2026-09-11T12:00:00Z'))
    return mutants


def resolve_documents(documents, as_of='2026-09-10T12:00:00Z') -> dict:
    """Independent relational oracle over actual exported passages.

Test-only: derive the result using the written rules, not production EXPECTED.
No tie-breaking by export position, revision label, or approval timestamp.
"""
    def one(kind, **filters):
        matches = [d for d in documents if d['kind'] == kind
                   and all(d.get(k) == v for k, v in filters.items())]
        assert len(matches) == 1, (kind, filters, len(matches))
        return matches[0]

    answers = []
    for ticket_id in ['T-417', 'T-418', 'T-419', 'T-420']:
        ticket = one('ticket', ticket_id=ticket_id)
        account = one('account', account_id=ticket['account_id'])
        binding = one('binding', region=account['region'], service=ticket['service'])
        evidence = [d['id'] for d in [ticket, account, binding]]
        eligible, withdrawn = [], []
        for policy in documents:
            if (policy['kind'] != 'policy_revision' or policy['policy_id'] != binding['policy_id']
                    or policy['effective_from'] > as_of
                    or (policy['effective_until'] is not None and policy['effective_until'] <= as_of)):
                continue
            decisions = [d for d in documents if d['kind'] == 'decision'
                         and d['policy_id'] == policy['policy_id'] and d['revision'] == policy['revision']
                         and d['region'] == account['region'] and d['service'] == ticket['service']
                         and d['issued_at'] <= as_of]
            if not decisions:
                continue
            latest = max(decisions, key=lambda d: d['issued_at'])
            (eligible if latest['decision'] == 'approved' else withdrawn).append((policy, latest))
        answer: dict = dict(ticket_id=ticket_id, account_id=account['account_id'],
                      policy_id=binding['policy_id'], status='insufficient_evidence',
                      revision=None, route=None, retention_days=None)
        if eligible:
            best_time = max(p['effective_from'] for p, _ in eligible)
            winners = [(p, d) for p, d in eligible if p['effective_from'] == best_time]
            for policy, decision in winners:
                evidence.extend([policy['id'], decision['id']])
            answer['status'] = 'conflict'
            if len(winners) == 1:
                winner = winners[0][0]
                answer.update(status='resolved', **{k: winner[k] for k in ['revision','route','retention_days']})
                for policy, decision in withdrawn:
                    if policy['effective_from'] > best_time:
                        evidence.extend([policy['id'], decision['id']])
        answer['evidence'] = evidence
        answers.append(answer)
    return dict(as_of=as_of, answers=answers)
