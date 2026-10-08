"""Integration contracts for the in-place coding refresh."""
import unittest
import eval_suite as suite

IDS = {'CODE-02', 'CODE-06', 'CODE-07', 'CODE-08', 'CODE-09', 'CODE-10', 'CODE-11', 'CODE-12'}

class IntegrationTests(unittest.TestCase):
    def test_all_eight_have_revision_receipt(self):
        selected = [s for s in suite.SCENARIOS if s['id'] in IDS]
        self.assertEqual(len(selected), 8)
        self.assertTrue(all(s.get('scenario_revision') == 'coding-2026-09-v1' for s in selected))

    def test_suite_shape_unchanged(self):
        self.assertEqual(len(suite.SCENARIOS), len({s['id'] for s in suite.SCENARIOS}))
        self.assertGreaterEqual(len(suite.SCENARIOS), 76)
        self.assertEqual(sum(s['domain'] == 'code' for s in suite.SCENARIOS), 14)

    def test_all_eight_through_real_runner_with_scripted_oracles(self):
        # These are explicit hand-written fixtures, never model scores.
        import json
        import tempfile
        from pathlib import Path
        from tests.code_hardening_oracles import SOLUTIONS as py_solutions
        from tests.test_code_sql_hardening import SOLUTIONS as sql_solutions
        solutions = {**py_solutions, **sql_solutions}
        prompts = {s['messages'][0]['content']: solutions[s['id']]
                   for s in suite.SCENARIOS if s['id'] in IDS}
        calls = []
        def scripted(messages, max_tokens, temperature, tools, extra):
            self.assertIsNone(max_tokens)
            self.assertFalse(extra['chat_template_kwargs']['enable_thinking'])
            calls.append(messages[0]['content'])
            return {'text': prompts[messages[0]['content']], 'reasoning': '',
                    'tool_calls': [], 'finish': 'stop', 'total': 0.01,
                    'completion_tokens': 10}
        with tempfile.TemporaryDirectory() as directory:
            result = suite.run_suite(scripted, repeats=2, scenario_ids=IDS,
                                     thinking='off', uncapped=True, artifact_dir=directory)
            self.assertEqual(len(calls),16)
            self.assertEqual({s['id'] for s in result['scenarios']},IDS)
            self.assertTrue(all(s['score']==1 for s in result['scenarios']))
            self.assertEqual(result['trial_stats']['methodology'],suite.UNCAPPED_METHODOLOGY_VERSION.replace('-uncapped', '-subset-uncapped'))
            transcripts = [json.loads(p.read_text()) for p in Path(directory).glob('transcripts/*.json')]
            self.assertEqual({(t['scenario_id'], t['repeat']) for t in transcripts},
                             {(sid,rep) for sid in IDS for rep in (1,2)})
            self.assertTrue(all(t['scenario_revision']=='coding-2026-09-v1' for t in transcripts))

    def test_old_shallow_leaves_no_longer_perfect(self):
        sc = next(s for s in suite.SCENARIOS if s['id'] == 'CODE-07')
        old = '''def extract_leaves(value):
    if isinstance(value, dict):
        return [x for v in value.values() for x in extract_leaves(v)]
    if isinstance(value, list):
        return [x for v in value for x in extract_leaves(v)]
    return [value]
'''
        score, reason = sc['grade']({'text': old})
        self.assertLess(score, 1.0, reason)

if __name__ == '__main__':
    unittest.main()
