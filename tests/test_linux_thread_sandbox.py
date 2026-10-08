import sys
import unittest
import eval_suite
from golden_gate import _sc
from tests.code_hardening_oracles import SOLUTIONS

@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux seccomp')
class ThreadSandboxTests(unittest.TestCase):
    def test_threads_allowed_processes_blocked(self):
        def probe():
            import os, subprocess, threading
            result=[]
            for fn in (os.fork, lambda: subprocess.run(['/bin/true'])):
                try:
                    fn()
                    result.append('unexpected')
                except PermissionError:
                    result.append('blocked')
            t=threading.Thread(target=lambda: result.append('thread-ok'))
            t.start(); t.join()
            return result
        self.assertEqual(eval_suite._sandboxed(probe), ['blocked','blocked','thread-ok'])
    def test_counter_reference(self):
        score, detail = _sc('CODE-12')['grade']({'text': SOLUTIONS['CODE-12']})
        self.assertEqual(score, 1.0, detail)

if __name__ == '__main__': unittest.main()
