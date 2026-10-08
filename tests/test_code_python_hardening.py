"""Grader self-tests: reference implementations and deliberate defects."""
import unittest
import eval_suite as suite
import code_python_hardening as upgrade
from tests.code_hardening_oracles import SOLUTIONS, MUTATIONS

class PythonHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graders = upgrade.build_graders(suite.expect_executable_code,
                                            suite._extract_python_code,
                                            suite._safe_counter_lock_contract)

    def test_reference_implementations_pass_all_groups(self):
        for sid, source in SOLUTIONS.items():
            with self.subTest(scenario=sid):
                score, reason = self.graders[sid]({'text': source})
                self.assertEqual(score, 1.0, reason)

    def test_every_deliberate_mutation_loses_credit(self):
        for sid, mutations in MUTATIONS.items():
            for name, old, new in mutations:
                with self.subTest(scenario=sid, defect=name):
                    self.assertIn(old, SOLUTIONS[sid])
                    source = SOLUTIONS[sid].replace(old,new)
                    compile(source, '<mutation>', 'exec')
                    score, reason = self.graders[sid]({'text': source})
                    self.assertLess(score, 1.0, reason)

    def test_empty_and_malformed_responses_fail(self):
        for sid, grade in self.graders.items():
            for text in ['', 'def broken(:', 'x = 3']:
                with self.subTest(scenario=sid,text=text):
                    self.assertEqual(grade({'text':text})[0], 0)

    def test_repeated_grading_is_deterministic(self):
        for sid, source in SOLUTIONS.items():
            with self.subTest(scenario=sid):
                a=self.graders[sid]({'text':source})
                b=self.graders[sid]({'text':source})
                self.assertEqual(a,b)

if __name__ == '__main__': unittest.main()
