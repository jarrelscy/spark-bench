"""v7.1 hard long-gen graders: references score 1.0, every plausible mutant scores lower."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import long_gen as lg


# --------------------------------------------------------------------------- #
# v7.1 hard LG-03 (spreadsheet) / LG-04 (ledger): reference passes, mutants drop
# --------------------------------------------------------------------------- #
import importlib.util as _ilu
import pathlib as _pl

_FIX = _pl.Path(__file__).parent / "fixtures"


def _load_mutants(name):
    spec = _ilu.spec_from_file_location(name, _pl.Path(__file__).parent / f"{name}.py")
    src = (_pl.Path(__file__).parent / f"{name}.py").read_text()
    head = src.split("\nfor name, pairs in MUTANTS.items():")[0]
    ns = {"__file__": str(_pl.Path(__file__).parent / f"{name}.py")}
    exec(compile(head, name, "exec"), ns)
    return ns


def _wrap(code):
    return {"text": "Here it is.\n```python\n" + code + "\n```\n", "finish_reason": "stop"}


def test_lg03_v71_reference_scores_full():
    ref = (_FIX / "lg03_sheet_ref.py").read_text()
    score, detail = lg._lg03_grade(_wrap(ref))
    assert score == 1.0, detail


def test_lg03_v71_every_mutant_scores_lower():
    ns = _load_mutants("lg03_mutants")
    for name, pairs in ns["MUTANTS"].items():
        score, detail = lg._lg03_grade(_wrap(ns["mut"](ns["REF"], pairs)))
        assert score < 1.0, (name, detail)


def test_lg04_v71_reference_scores_full():
    ref = (_FIX / "lg04_ledger_ref.py").read_text()
    score, detail = lg._lg04_grade(_wrap(ref))
    assert score == 1.0, detail


def test_lg04_v71_every_mutant_scores_lower():
    ns = _load_mutants("lg04_mutants")
    for name, pairs in ns["MUTANTS"].items():
        score, detail = lg._lg04_grade(_wrap(ns["mut"](ns["REF"], pairs)))
        assert score < 1.0, (name, detail)


def test_lg_v71_truncated_and_missing_code_score_zero():
    for g in (lg._lg03_grade, lg._lg04_grade):
        assert g({"text": "```python\nclass Sheet: pass\n", "finish_reason": "length"})[0] == 0.0
        assert g({"text": "I cannot do that.", "finish_reason": "stop"})[0] == 0.0


def test_lg_v71_prompts_do_not_leak_hidden_cases():
    import lg03_sheet, lg04_ledger
    # distinctive hidden inputs must not appear in the prompts
    for needle in ("A3000", "J200", "say \"hi\"", "Apple"):
        assert needle not in lg03_sheet.LG03_PROMPT, needle
    for needle in ("11.50", "0.29", "1.15", "9.98", "4.01"):
        assert needle not in lg04_ledger.LG04_PROMPT, needle


def test_lg_v71_scenarios_registered():
    by_id = {s["id"]: s for s in lg.LONG_GEN_SCENARIOS}
    assert by_id["LG-03"]["scenario_revision"] == "lg03-sheet-2026-10-v2"
    assert by_id["LG-04"]["scenario_revision"] == "lg04-ledger-2026-10-v2"
    assert "class Sheet" in by_id["LG-03"]["messages"][-1]["content"]
    assert "run_trace" in by_id["LG-04"]["messages"][-1]["content"]
