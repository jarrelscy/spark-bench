import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import eval_suite as ev
import spark_bench as sb


class TailRecoveryTests(unittest.TestCase):
    def test_uncapped_guard_auto_detects_sglang(self):
        args = SimpleNamespace(
            uncapped=True,
            runaway_char_window=4096,
            runaway_phrase_window=8192,
            runaway_abort_backend="auto",
        )
        with mock.patch.dict(os.environ, {}, clear=True):
            backend = sb._configure_runaway_guard(args, owner="sglang")
            self.assertEqual(backend, "sglang")
            self.assertEqual(os.environ["SPARK_BENCH_RUNAWAY_CHAR_WINDOW"], "4096")
            self.assertEqual(os.environ["SPARK_BENCH_RUNAWAY_PHRASE_WINDOW"], "8192")
            self.assertEqual(os.environ["SPARK_BENCH_RUNAWAY_ABORT_BACKEND"], "sglang")

    def test_uncapped_guard_uses_disconnect_for_vllm(self):
        args = SimpleNamespace(
            uncapped=True,
            runaway_char_window=4096,
            runaway_phrase_window=8192,
            runaway_abort_backend="auto",
        )
        with mock.patch.dict(os.environ, {}, clear=True):
            backend = sb._configure_runaway_guard(args, owner="vllm")
            self.assertEqual(backend, "disconnect")
            self.assertEqual(os.environ["SPARK_BENCH_RUNAWAY_ABORT_BACKEND"], "disconnect")

    def test_single_character_runaway_detector(self):
        self.assertTrue(sb._is_single_char_runaway("!" * 4096, 4096))
        self.assertFalse(sb._is_single_char_runaway("!" * 4095, 4096))
        self.assertFalse(sb._is_single_char_runaway("const x = 1;\n" * 400, 4096))

    def test_repeated_phrase_runaway_detector(self):
        sentence = "The event exists but is not returned. Trying again. "
        self.assertTrue(sb._is_repeated_phrase_runaway(sentence * 300, 8192))
        normal = "\n".join(
            f"step {i}: verify item {i * 7919 % 104729} and record result {i * i}"
            for i in range(500)
        )
        self.assertFalse(sb._is_repeated_phrase_runaway(normal, 8192))

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
                ev.UNCAPPED_METHODOLOGY_VERSION.replace("-uncapped", "-subset-uncapped"),
            )

    def test_runaway_without_native_usage_is_not_reported_as_estimated_tokens(self):
        def chat_fn(messages, max_tokens, temperature, tools, extra):
            return {
                "text": "!" * 4096,
                "reasoning": "",
                "tool_calls": [],
                "finish": "runaway",
                "completion_tokens": 0,
                "total": 2.0,
                "runaway": {"kind": "single_character", "window_chars": 4096},
            }

        result = ev.run_suite(
            chat_fn,
            repeats=2,
            scenario_ids={"AG-11"},
            repeat_indices={2},
            thinking="off",
            uncapped=True,
        )
        self.assertEqual(result["scenarios"][0]["output_tokens"], 0)

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
            self.assertEqual(record["score"], 0.0)
            self.assertEqual(record["response"]["finish"], "length")
            self.assertEqual(record["response"]["completion_tokens"], 32)
            self.assertIn("model_failure:length", record["reason"])

    def test_capped_run_records_refreshed_methodology(self):
        def chat_fn(messages, max_tokens, temperature, tools, extra):
            return {
                "text": "PONG", "reasoning": "", "tool_calls": [],
                "finish": "stop", "completion_tokens": 2, "total": 0.1,
            }

        result = ev.run_suite(
            chat_fn,
            repeats=2,
            scenario_ids={"IF-01"},
            repeat_indices={1},
            thinking="off",
            uncapped=False,
        )
        self.assertEqual(
            result["trial_stats"]["methodology"],
            ev.METHODOLOGY_VERSION + "-subset",
        )

    def test_nonagentic_length_finish_is_model_failure_zero(self):
        def chat_fn(messages, max_tokens, temperature, tools, extra):
            return {
                "text": "PONG", "reasoning": "", "tool_calls": [],
                "finish": "length", "completion_tokens": 262038, "total": 10.0,
            }

        result = ev.run_suite(
            chat_fn,
            repeats=2,
            scenario_ids={"IF-01"},
            repeat_indices={1},
            thinking="off",
            uncapped=True,
        )
        row = result["scenarios"][0]
        self.assertEqual(row["score"], 0.0)
        self.assertTrue(row["reason"].startswith("model_failure:length"))


if __name__ == "__main__":
    unittest.main()
