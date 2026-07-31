import os
import tempfile
import unittest

from spark_bench import classify_eval_integrity


STRUCTURED_IDS = ["SO-02", "SOH-01", "SOH-02", "SOH-03", "SOH-04"]
AGENTIC_IDS = [f"AG-{i:02d}" for i in range(1, 13)]
VISUAL_IDS = [f"VIS-{i:02d}" for i in range(1, 6)]


def record(scenario_id, domain, score=1.0, reason="passed", artifact=None):
    return {
        "id": scenario_id,
        "domain": domain,
        "group": "capability",
        "score": score,
        "subs": [score, score],
        "pass_rate": 1.0 if score >= 0.5 else 0.0,
        "reason": reason,
        "artifact": artifact,
    }


def result(records, valid=True, error_rate=0.0):
    return {
        "scenarios": records,
        "trial_stats": {"valid": valid, "error_rate": error_rate},
    }


class QuarantineTests(unittest.TestCase):
    def test_complete_strict_structured_domain_is_verified(self):
        rows = [record(i, "structured", reason="valid nested JSON")
                for i in STRUCTURED_IDS]
        self.assertEqual(classify_eval_integrity(result(rows)),
                         ([], ["structured=1"]))

    def test_partial_structured_domain_stays_quarantined(self):
        rows = [record(i, "structured", reason="valid JSON")
                for i in STRUCTURED_IDS[:3]]
        self.assertEqual(classify_eval_integrity(result(rows))[0],
                         ["FLAT_DOMAIN:structured=1"])

    def test_complete_agentic_domain_is_verified(self):
        rows = [record(i, "agentic", reason="agentic 6/6: all checks passed")
                for i in AGENTIC_IDS]
        self.assertEqual(classify_eval_integrity(result(rows)),
                         ([], ["agentic=1"]))

    def test_historical_six_scenario_agentic_flat_stays_quarantined(self):
        rows = [record(i, "agentic", reason="agentic 6/6: all checks passed")
                for i in AGENTIC_IDS[:6]]
        flags, verified = classify_eval_integrity(result(rows))
        self.assertEqual(flags, ["FLAT_DOMAIN:agentic=1"])
        self.assertEqual(verified, [])

    def test_agentic_failed_check_cannot_be_verified(self):
        rows = [record(i, "agentic", reason="agentic 6/6: all checks passed")
                for i in AGENTIC_IDS]
        rows[-1]["reason"] = "agentic 5/6: one check failed"
        self.assertEqual(classify_eval_integrity(result(rows))[0],
                         ["FLAT_DOMAIN:agentic=1"])

    def test_multiple_verified_domains_do_not_trip_flat_all(self):
        rows = [record(i, "structured", reason="valid nested JSON")
                for i in STRUCTURED_IDS]
        rows += [record(i, "agentic", reason="agentic 6/6: all checks passed")
                 for i in AGENTIC_IDS]
        self.assertEqual(classify_eval_integrity(result(rows)),
                         ([], ["agentic=1", "structured=1"]))

    def test_flat_calibration_domain_is_not_a_capability_quarantine(self):
        rows = [record(f"RO-{i}", "robustness") for i in range(1, 5)]
        for row in rows:
            row["group"] = "calibration"
        self.assertEqual(classify_eval_integrity(result(rows)), ([], []))

    def test_rendered_visual_domain_is_verified_with_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = []
            for scenario_id in VISUAL_IDS:
                path = os.path.join(tmp, f"{scenario_id}.html")
                with open(path, "w") as handle:
                    handle.write("<!doctype html>")
                reason = "rendered"
                if scenario_id == "VIS-04":
                    reason = ("red-visible=y, blue-visible=y, red-moves=y, "
                              "blue-moves=y, overtake-event=y")
                elif scenario_id == "VIS-05":
                    reason = ("scene-structure=y, peak>start=y, "
                              "peak-not-loadflash=y, settles=y")
                rows.append(record(scenario_id, "visual", reason=reason,
                                   artifact=path))
            self.assertEqual(classify_eval_integrity(result(rows)),
                             ([], ["visual=1"]))

    def test_visual_flat_without_render_evidence_stays_quarantined(self):
        rows = [record(i, "visual", reason="proxy checks passed")
                for i in VISUAL_IDS]
        self.assertEqual(classify_eval_integrity(result(rows))[0],
                         ["FLAT_DOMAIN:visual=1"])

    def test_all_zero_domain_stays_quarantined(self):
        rows = [record(f"X-{i}", "tool_use", score=0.0) for i in range(5)]
        self.assertEqual(classify_eval_integrity(result(rows))[0],
                         ["FLAT_DOMAIN:tool_use=0"])

    def test_near_dead_domain_stays_quarantined(self):
        scores = [0.0, 0.0, 0.0, 0.0, 0.04]
        rows = [record(f"X-{i}", "tool_use", score=score)
                for i, score in enumerate(scores)]
        self.assertEqual(classify_eval_integrity(result(rows))[0],
                         ["DEAD_DOMAIN:tool_use"])

    def test_invalid_error_rate_stays_quarantined(self):
        rows = [record(i, "structured", reason="valid JSON")
                for i in STRUCTURED_IDS]
        flags, verified = classify_eval_integrity(
            result(rows, valid=False, error_rate=6.6))
        self.assertEqual(flags, ["ERROR_RATE:6.6%"])
        self.assertEqual(verified, ["structured=1"])


if __name__ == "__main__":
    unittest.main()
