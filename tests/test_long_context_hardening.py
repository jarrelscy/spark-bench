"""LC-03 refresh contracts; fixtures are scripted, not model measurements."""
import unittest
import eval_suite as suite


class LongContextHardeningTests(unittest.TestCase):
    def test_lc03_is_revised_in_place(self):
        sc = next(s for s in suite.SCENARIOS if s['id'] == 'LC-03')
        self.assertEqual(sc.get('scenario_revision'), 'long-context-reconciliation-1')
        self.assertEqual(len(suite.SCENARIOS), 76)
        self.assertEqual(sc['difficulty'], 1.4)
        self.assertEqual(sc['domain'], 'long_context')

    def test_old_passcode_no_longer_passes(self):
        sc = next(s for s in suite.SCENARIOS if s['id'] == 'LC-03')
        score, _ = sc['grade']({'text': 'VESPER-3318'})
        self.assertEqual(score, 0)

    def test_reference_and_independent_document_resolver(self):
        import json
        import long_context_hardening as h
        from tests.long_context_oracles import REFERENCE, resolve_documents
        for text in [REFERENCE, json.dumps(resolve_documents(h.build_documents()))]:
            self.assertEqual(h.grade({'text': text})[0], 1)

    def test_all_deliberate_defects_fail_task_threshold(self):
        import long_context_hardening as h
        from tests.long_context_oracles import defective_answers
        self.assertEqual(len(defective_answers()), 35)
        for name, text in defective_answers().items():
            with self.subTest(name=name):
                score, reason = h.grade({'text': text})
                self.assertLess(score, .5, reason)

    def test_each_individual_relationship_and_citation_is_required(self):
        import copy
        import json
        import long_context_hardening as h
        from tests.long_context_oracles import REFERENCE
        base = json.loads(REFERENCE)
        for index, answer in enumerate(base['answers']):
            for key in answer:
                bad = copy.deepcopy(base)
                bad['answers'][index][key] = [] if key == 'evidence' else 'wrong'
                with self.subTest(index=index, field=key):
                    self.assertLess(h.grade({'text': json.dumps(bad)})[0], .5)
            for citation in answer['evidence']:
                bad = copy.deepcopy(base)
                bad['answers'][index]['evidence'].remove(citation)
                with self.subTest(index=index, citation=citation):
                    self.assertLess(h.grade({'text': json.dumps(bad)})[0], .5)

    def test_whitespace_key_order_and_citation_order_are_not_semantics(self):
        import json
        import long_context_hardening as h
        from tests.long_context_oracles import REFERENCE
        obj = json.loads(REFERENCE)
        for answer in obj['answers']:
            answer['evidence'].reverse()
        self.assertEqual(h.grade({'text': '\n' + json.dumps(obj, sort_keys=True) + '\n'})[0], 1)

    def test_malformed_inputs_fail_safely(self):
        import long_context_hardening as h
        malformed = [None, [], 1, {}, {'text': None}, {'text': 17}, {'text': []},
                     {'text': '[' * 2000 + ']' * 2000}]
        for text in ['null', '[]', 'true', '1', '{}', '"answer"', '', '{',
                     '{"as_of":"2026-09-10T12:00:00Z","answers":[null,null,null,null]}']:
            malformed.append({'text': text})
        for response in malformed:
            with self.subTest(response=str(response)[:80]):
                self.assertEqual(h.grade(response)[0], 0)

    def test_nonterminal_responses_never_pass(self):
        import long_context_hardening as h
        from tests.long_context_oracles import REFERENCE
        for finish in ['length', 'runaway', 'tool_calls', None]:
            self.assertEqual(h.grade({'text': REFERENCE, 'finish': finish})[0], 0)

    def test_corpus_is_bounded_unique_deterministic_and_not_answer_leaked(self):
        import json
        import long_context_hardening as h
        docs = h.build_documents()
        self.assertEqual(len(docs), 112)
        self.assertEqual(len({d['id'] for d in docs}), len(docs))
        self.assertEqual(h.build_prompt(), h.PROMPT)
        self.assertLessEqual(len(h.PROMPT.encode()), h.MAX_PROMPT_UTF8_BYTES)
        self.assertGreater(len(h.PROMPT.encode()), 16000)
        self.assertEqual(h.CONTEXT_REQUIREMENT_TOKENS, 32768)
        self.assertNotIn('"answers": [', h.PROMPT)
        # Parse precisely the export that the model sees, not a separate fixture.
        export = h.PROMPT.split('BEGIN DOCUMENT EXPORT\n')[1].split('\nEND DOCUMENT EXPORT')[0]
        self.assertEqual([json.loads(line) for line in export.splitlines()], docs)
        # Complete supporting chains cross separated sections, not one local block.
        for answer in h.EXPECTED:
            positions = [int(c[1:]) for c in answer['evidence']]
            self.assertGreater(max(positions) - min(positions), 60)

    def test_export_order_and_unrelated_record_variants_do_not_change_outcome(self):
        import copy
        import json
        import random
        import long_context_hardening as h
        from tests.long_context_oracles import resolve_documents
        for seed in range(5):
            docs = copy.deepcopy(h.build_documents())
            for doc in docs:
                if int(doc['id'][1:]) not in h.SPECIAL_DOCUMENTS:
                    if 'display_name' in doc:
                        doc['display_name'] = 'Orion Labs'
                    if 'route' in doc:
                        doc['route'] = f'noise-route-{seed}'
            random.Random(seed).shuffle(docs)
            self.assertEqual(h.grade({'text': json.dumps(resolve_documents(docs))})[0], 1)

    def test_temporal_and_authority_rules_are_causally_necessary(self):
        import copy
        import long_context_hardening as h
        from tests.long_context_oracles import resolve_documents
        # Changing one source fact makes each formerly excluded revision win.
        changes = [('D015', 'effective_until', '2026-09-10T12:00:01Z', 0, 'r6'),
                   ('D021', 'region', 'eu-west', 0, 'r3'),
                   ('D034', 'effective_from', '2026-09-10T00:00:00Z', 0, 'r4'),
                   ('D111', 'issued_at', '2026-09-10T12:00:00Z', 0, 'r5'),
                   ('D058', 'decision', 'approved', 1, 'r4'),
                   ('D004', 'effective_from', '2026-09-02T00:00:00Z', 1, 'r9'),
                   ('D076', 'effective_from', '2026-09-06T00:00:00Z', 2, 'v9')]
        for doc_id, key, value, index, revision in changes:
            docs = copy.deepcopy(h.build_documents())
            next(d for d in docs if d['id'] == doc_id)[key] = value
            answer = resolve_documents(docs)['answers'][index]
            with self.subTest(doc=doc_id):
                self.assertEqual(answer['revision'], revision)
                self.assertEqual(answer['status'], 'resolved')

    def test_real_runner_persists_two_uncapped_receipts(self):
        import json
        import tempfile
        from pathlib import Path
        import long_context_hardening as h
        from tests.long_context_oracles import REFERENCE
        calls = []
        def scripted(messages, max_tokens, temperature, tools, extra):
            self.assertIsNone(max_tokens)
            self.assertIsNone(tools)
            self.assertFalse(extra['chat_template_kwargs']['enable_thinking'])
            self.assertEqual(messages, [{'role': 'user', 'content': h.PROMPT}])
            calls.append(messages)
            return {'text': REFERENCE, 'reasoning': '', 'tool_calls': [],
                    'finish': 'stop', 'total': .01, 'completion_tokens': 500}
        with tempfile.TemporaryDirectory() as directory:
            result = suite.run_suite(scripted, repeats=2, scenario_ids={'LC-03'},
                                     thinking='off', uncapped=True, artifact_dir=directory)
            self.assertEqual(len(calls), 2)
            self.assertEqual(result['scenarios'][0]['score'], 1)
            self.assertEqual(result['scenarios'][0]['pass_rate'], 1)
            self.assertEqual(result['trial_stats']['methodology'], 'v6.8.3-full-subset-uncapped')
            rows = [json.loads(p.read_text()) for p in Path(directory).glob('transcripts/*.json')]
            self.assertEqual({(r['scenario_id'], r['repeat']) for r in rows}, {('LC-03',1),('LC-03',2)})
            self.assertEqual(len(rows), 2)
            for row in rows:
                self.assertEqual(row['scenario_revision'], h.REVISION)
                self.assertEqual(row['context_requirement_tokens'], h.CONTEXT_REQUIREMENT_TOKENS)
                self.assertEqual(row['score'], 1)

    def test_wrong_answer_cannot_count_as_runner_pass(self):
        from tests.long_context_oracles import defective_answers
        text = defective_answers()['wrong-retention-only']
        result = suite.run_suite(lambda *a: {'text': text, 'reasoning': '', 'tool_calls': [],
                                  'finish': 'stop', 'total': .01, 'completion_tokens': 500},
                                 repeats=1, scenario_ids={'LC-03'}, thinking='off', uncapped=True)
        self.assertEqual(result['scenarios'][0]['pass_rate'], 0)
        self.assertLess(result['scenarios'][0]['score'], .5)

    def test_modular_grader_and_gate_fixtures_are_provenance_tracked(self):
        import spark_bench
        self.assertTrue({'long_context_hardening.py', 'tests/long_context_oracles.py'}
                        <= set(spark_bench.GRADER_FILES))

    def test_gate_detects_grader_and_expectation_sabotage(self):
        import copy
        import golden_gate as gate
        import long_context_hardening as h
        from unittest.mock import patch
        sc = next(s for s in suite.SCENARIOS if s['id'] == 'LC-03')
        # Unit fault injection uses explicit render mocks; run the standalone
        # golden gate separately with the real browser before release.
        def race(html, **kwargs):
            return (float(html == gate.V3D_RACE_PASS), 'unit-test render stub')
        def runner(html, **kwargs):
            return (float(html == gate.V3D_RUN_PASS), 'unit-test render stub')
        with patch('visual_3d_grader.grade_race_render', race), patch('visual_3d_grader.grade_runner_render', runner):
            self.assertTrue(gate.run_gate(verbose=False)[0])
            for grader in [lambda r: (1., 'auto-pass'), lambda r: (0., 'reject-all'),
                           lambda r: (float('route-K27' in r.get('text','')), 'substring-only')]:
                with patch.dict(sc, grade=grader):
                    self.assertFalse(gate.run_gate(verbose=False)[0])
            corrupt = copy.deepcopy(h.EXPECTED)
            corrupt[0]['route'] = 'corrupt-grader-target'
            with patch.object(h, 'EXPECTED', corrupt):
                self.assertFalse(gate.run_gate(verbose=False)[0])


if __name__ == '__main__':
    unittest.main()
