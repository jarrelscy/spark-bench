import json
import tempfile
import unittest
from pathlib import Path

import eval_suite as ev
import spark_bench as sb


class TailRecoveryTests(unittest.TestCase):
    def test_single_character_runaway_detector(self):
        self.assertTrue(sb._is_single_char_runaway("!" * 4096, 4096))
        self.assertFalse(sb._is_single_char_runaway("!" * 4095, 4096))
        self.assertFalse(sb._is_single_char_runaway("const x = 1;\n" * 400, 4096))

    def test_run_suite_can_write_only_absolute_repeat_two(self):
        calls = []

        def chat_fn(messages, max_tokens, temperature, tools, extra):
            calls.append(messages)
            return {
                "text": "I could not complete the requested operations.",
                "reasoning": "",
                "tool_calls": [],
                "finish": "stop",
                "completion_tokens": 9,
                "total": 0.25,
            }

        with tempfile.TemporaryDirectory() as td:
            result = ev.run_suite(
                chat_fn,
                repeats=2,
                scenario_ids={"AG-11"},
                repeat_indices={2},
                thinking="off",
                uncapped=True,
                artifact_dir=td,
            )
            transcript_dir = Path(td) / "transcripts"
            self.assertFalse((transcript_dir / "AG-11-repeat-1.json").exists())
            path = transcript_dir / "AG-11-repeat-2.json"
            self.assertTrue(path.exists())
            record = json.loads(path.read_text())
            self.assertEqual(record["repeat"], 2)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["scenarios"][0]["reps"], 1)
            self.assertEqual(
                result["trial_stats"]["methodology"],
                "v6.7.1-full-subset-uncapped",
            )

    def test_agentic_transcript_preserves_real_length_finish(self):
        def chat_fn(messages, max_tokens, temperature, tools, extra):
            return {
                "text": "!" * 32,
                "reasoning": "",
                "tool_calls": [],
                "finish": "length",
                "completion_tokens": 32,
                "total": 1.5,
            }

        with tempfile.TemporaryDirectory() as td:
            ev.run_suite(
                chat_fn,
                repeats=2,
                scenario_ids={"AG-11"},
                repeat_indices={1},
                thinking="off",
                uncapped=True,
                artifact_dir=td,
            )
            record = json.loads(
                (Path(td) / "transcripts" / "AG-11-repeat-1.json").read_text()
            )
            self.assertEqual(record["response"]["finish"], "length")
            self.assertEqual(record["response"]["completion_tokens"], 32)
            self.assertIn("model_failure:length", record["reason"])


if __name__ == "__main__":
    unittest.main()
