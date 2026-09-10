"""Stateful agentic grading contracts; all model callbacks are scripted oracles."""
import unittest
import eval_suite as suite

IDS = {'AG-01', 'AG-02', 'AG-10', 'AG-11', 'AG-12'}

class IntegrationTests(unittest.TestCase):
    def test_exact_five_have_new_revision(self):
        upgraded = {s['id'] for s in suite.SCENARIOS
                    if s.get('scenario_revision') == 'agentic-hardening-1'}
        self.assertEqual(upgraded, IDS)

    def test_reports_include_authoritative_final_state(self):
        sc = next(s for s in suite.SCENARIOS if s['id']=='AG-01')
        def stopped(*args):
            return {'text':'Done.', 'tool_calls':[], 'finish':'stop'}
        result = suite._run_agentic(sc, stopped, {}, 0, timeout=0, capture_trace=True, uncapped=True)
        self.assertIn('environment', result[-1])
        self.assertIn('outcome', result[-1])
        self.assertLess(result[0], .5)

    def test_existing_eight_coding_revisions_remain(self):
        self.assertEqual(sum(s.get('scenario_revision')=='coding-2026-09-v1'
                             for s in suite.SCENARIOS), 8)
        self.assertEqual(len(suite.SCENARIOS), 76)

DEFECTS = {
    'AG-01': ['wrong_contact','first_page_only','wrong_slot','skip_verification','extra_email','dishonest_report'],
    'AG-02': ['wrong_duration','wrong_revision','no_refresh','skip_verification','extra_email'],
    'AG-10': ['duplicate_event','duplicate_email','skip_verification','extra_email','dishonest_report'],
    'AG-11': ['wrong_target','wrong_time','skip_verification','extra_email','dishonest_report'],
    'AG-12': ['guess_currency','guess_correct_currency','superseded_amount','skip_verification','extra_email'],
}


def run_oracle(sid, defect=None, variant=0, currency='GBP', recovery='lookup'):
    from tests.agentic_hardening_oracles import ScriptedAgent
    sc=dict(next(s for s in suite.SCENARIOS if s['id']==sid),
            agentic_variant=variant,agentic_user_currency=currency)
    agent=ScriptedAgent(sid,defect,recovery)
    return suite._run_agentic(sc,agent,{},0,0,capture_trace=True,uncapped=True),agent


class OutcomeTests(unittest.TestCase):
    def test_every_reference_resolves_all_requirements(self):
        for sid in sorted(IDS):
            with self.subTest(scenario=sid):
                r,agent=run_oracle(sid)
                self.assertEqual(r[0],1,r[1])
                self.assertTrue(r[-1]['outcome']['strict_success'])
                self.assertTrue(all(a['max_tokens'] is None for a in agent.requests))

    def test_every_broken_policy_fails_task_pass_threshold(self):
        for sid,defects in DEFECTS.items():
            for defect in defects:
                with self.subTest(scenario=sid,defect=defect):
                    r,_=run_oracle(sid,defect)
                    self.assertLess(r[0],.5,r[1])
                    self.assertFalse(r[-1]['outcome']['strict_success'])

    def test_changed_facts_and_nonsevere_branch(self):
        for sid in sorted(IDS):
            with self.subTest(scenario=sid):
                r,_=run_oracle(sid,variant=1,currency='EUR')
                self.assertEqual(r[0],1,r[1])
                if sid=='AG-10': self.assertEqual(r[-1]['environment']['mutations'],[])

    def test_no_user_answer_requires_honest_stop_and_no_writes(self):
        r,_=run_oracle('AG-12',currency=None)
        self.assertEqual(r[0],1,r[1])
        self.assertEqual(r[-1]['environment']['mutations'],[])
        for defect in ['proceed_when_waiting','false_success']:
            r,_=run_oracle('AG-12',defect,currency=None)
            self.assertLess(r[0],.5,r[1])

    def test_safe_retry_and_lookup_both_work_after_real_commit(self):
        for strategy in ['retry','lookup']:
            r,_=run_oracle('AG-10',recovery=strategy)
            w=r[-1]['environment']
            self.assertEqual(r[0],1,r[1])
            self.assertEqual(len(w['lost']),2)
            self.assertEqual(len(w['emails']),4)
            self.assertEqual(sum(m['tool']=='create_event' for m in w['mutations']),2)
            for lost in w['lost']:
                self.assertTrue(any(m['sequence']==lost['sequence'] for m in w['mutations']))

    def test_stale_revision_and_idempotency_conflict_do_not_mutate(self):
        import agentic_hardening as h
        import json
        w=h.make_world('AG-11')
        args=dict(id='evt-73',expected_version=0,patch={'start':'13:00'},request_id='u1')
        self.assertEqual(json.loads(h.simulate(w,'update_event',args))['error'],'VERSION_CONFLICT')
        self.assertEqual(w['mutations'],[])
        args['expected_version']=1
        h.simulate(w,'update_event',args)
        h.simulate(w,'update_event',args)
        self.assertEqual(len(w['mutations']),1)
        args['patch']={'start':'14:00'}
        self.assertEqual(json.loads(h.simulate(w,'update_event',args))['error'],'IDEMPOTENCY_CONFLICT')
        self.assertEqual(len(w['mutations']),1)

    def test_wrong_then_repaired_update_still_fails_safety(self):
        import json
        import agentic_hardening as h
        from agentic_outcome_grading import assess
        r,_=run_oracle('AG-11'); w=r[-1]['environment']; e=w['events']['evt-73']
        bad=dict(id=e['id'],expected_version=e['version'],patch={'title':'Wrong meeting'},request_id='bad')
        h.simulate(w,'update_event',bad)
        fix=dict(id=e['id'],expected_version=e['version']+1,patch={'title':e['title']},request_id='repair')
        h.simulate(w,'update_event',fix); h.simulate(w,'get_event',{'id':e['id']})
        score,reason,outcome=assess(w,[r[3]])
        self.assertTrue(outcome['checks']['exact_events'],reason)
        self.assertFalse(outcome['checks']['no_unsafe_effects'],reason)
        self.assertLess(score,.5)

    def test_unlisted_tools_cannot_bypass_isolated_world(self):
        import json
        import agentic_hardening as h
        w=h.make_world('AG-11')
        for name in ['create_event','cancel_event','delete_event','email']:
            self.assertEqual(json.loads(h.simulate(w,name,{}))['error'],'TOOL_NOT_AVAILABLE')
        self.assertEqual(w['mutations'],[])

    def test_all_runtime_modules_in_dirty_tree_provenance(self):
        import spark_bench as bench
        self.assertTrue({'agentic_hardening.py','agentic_outcome_grading.py',
                         'code_python_hardening.py','code_sql_hardening.py'} <= set(bench.GRADER_FILES))

    def test_malformed_tool_arguments_are_recoverable(self):
        import json
        import agentic_hardening as h
        for sid in IDS:
            w=h.make_world(sid)
            for name in h.NAMES[sid]:
                for args in [None,[],{'unexpected':True}]:
                    self.assertIn('error',json.loads(h.simulate(w,name,args)))
            self.assertEqual(w['mutations'],[])

    def test_malformed_event_reference_fails_without_harness_error(self):
        import json
        import agentic_hardening as h
        from agentic_outcome_grading import assess
        r,_=run_oracle('AG-01'); w=r[-1]['environment']
        h.simulate(w,'send_email',{'to':'john.nyc@corp.com','subject':'Trip Confirmed',
                                 'details':{'event_id':[]},'request_id':'malformed'})
        try:
            score,reason,outcome=assess(w,[r[3]])
        except Exception as exc:
            self.fail('Malformed model payload crashed grader: '+repr(exc))
        self.assertLess(score,.5,reason)

    def test_full_runner_persists_ten_stateful_trial_receipts(self):
        import json
        import tempfile
        from pathlib import Path
        from tests.agentic_hardening_oracles import ScriptedAgent
        by_prompt={s['messages'][0]['content']:s['id'] for s in suite.SCENARIOS if s['id'] in IDS}
        active=[None]; agents=[]
        def router(messages,max_tokens,temperature,tools,extra):
            if len(messages)==2:
                active[0]=ScriptedAgent(by_prompt[messages[1]['content']]); agents.append(active[0])
            return active[0](messages,max_tokens,temperature,tools,extra)
        with tempfile.TemporaryDirectory() as tmp:
            result=suite.run_suite(router,repeats=2,scenario_ids=sorted(IDS),thinking='off',
                                   uncapped=True,timeout=0,artifact_dir=tmp)
            files=list((Path(tmp)/'transcripts').glob('AG-*-repeat-*.json'))
            rows=[json.loads(f.read_text()) for f in files]
            self.assertEqual({(r['scenario_id'],r['repeat']) for r in rows},
                             {(sid,n) for sid in IDS for n in (1,2)})
            self.assertEqual(len(rows),10)
            for row in rows:
                self.assertEqual(row['score'],1)
                self.assertEqual(row['scenario_revision'],'agentic-hardening-1')
                self.assertTrue(row['response']['agentic_trace']['outcome']['strict_success'])
                self.assertIn('mutations',row['response']['agentic_trace']['environment'])
            self.assertTrue(all(a['max_tokens'] is None and
                                a['extra']['chat_template_kwargs']['enable_thinking'] is False
                                for agent in agents for a in agent.requests))

    def test_nonterminal_finish_never_qualifies_success(self):
        from tests.agentic_hardening_oracles import ScriptedAgent
        sc=next(s for s in suite.SCENARIOS if s['id']=='AG-01')
        for finish in ['length','runaway','tool_calls',None]:
            agent=ScriptedAgent('AG-01')
            def wrapper(*args):
                r=agent(*args)
                if r['finish']=='stop': r['finish']=finish
                return r
            r=suite._run_agentic(sc,wrapper,{},0,0,capture_trace=True,uncapped=True)
            self.assertEqual(r[0],0)
            self.assertFalse(r[-1]['outcome']['strict_success'])

    def test_pagination_tokens_are_bound_to_query(self):
        import json
        import agentic_hardening as h
        w=h.make_world('AG-11')
        page=json.loads(h.simulate(w,'list_events',{}))
        bad=json.loads(h.simulate(w,'list_events',{'day':'next_monday','cursor':page['next_cursor']}))
        self.assertEqual(bad['error'],'INVALID_CURSOR')

    def test_gate_catches_agentic_grader_sabotage(self):
        # Fault-injection UNIT test: rendering is explicitly mocked here only.
        # The standalone golden gate separately exercises the real browser.
        from unittest.mock import patch
        import golden_gate as gate
        def race(html,**kwargs):
            return (1.0 if html==gate.V3D_RACE_PASS else 0.0,'mock render for fault-injection unit test')
        def runner(html,**kwargs):
            return (1.0 if html==gate.V3D_RUN_PASS else 0.0,'mock render for fault-injection unit test')
        with patch('visual_3d_grader.grade_race_render',race), patch('visual_3d_grader.grade_runner_render',runner):
            self.assertTrue(gate.prove_gate_catches_sabotage())

    def test_worlds_do_not_leak_mutations_between_repeats(self):
        for sid in IDS:
            a,_=run_oracle(sid); b,_=run_oracle(sid)
            self.assertEqual(a[-1]['environment'],b[-1]['environment'])


if __name__ == '__main__': unittest.main()
