"""Mutation check for LG-03: each mutant is a plausible model mistake applied to the
reference. A good grader scores the reference 40/40 and every mutant strictly lower,
spread across the range rather than all 0 or all 39."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/projects/spark-bench-development"))
import long_gen as lg, lg03_sheet as L

REF = open(os.path.expanduser("~/projects/spark-bench-development/tests/fixtures/lg03_sheet_ref.py")).read()

def mut(src, pairs):
    for a, b in pairs:
        assert a in src, a[:60]
        src = src.replace(a, b, 1)
    return src

MUTANTS = {
    # precedence: unary binds tighter than ^ (the classic -2^2 = 4 bug)
    "unary-over-power": [("        if self.isop(\"-\", \"+\"):\n            return (\"neg\" if self.take()[1] == \"-\" else \"pos\", self.unary())\n        return self.power()",
                          "        return self.power()"),
                         ("        if k in (\"num\", \"str\"): return (\"lit\", v)",
                          "        if k == \"op\" and v in (\"-\", \"+\"): return (\"neg\" if v == \"-\" else \"pos\", self.primary())\n        if k in (\"num\", \"str\"): return (\"lit\", v)")],
    # ^ left-associative
    "power-left-assoc": [("            self.take(); n = (\"bin\", \"^\", n, self.unary())",
                          "            self.take(); n = (\"bin\", \"^\", n, self.primary())")],
    # Python round() (banker's, binary) instead of exact half-up
    "python-round": [("            q = Decimal(1).scaleb(-int(d))\n            return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))",
                      "            return float(round(x, int(d)))")],
    # memoise across edits (stale values / cycles never re-evaluated)
    "stale-cache": [("        k = _key(ref)\n        self._analyse()\n        # evaluate",
                     "        k = _key(ref)\n        if not hasattr(self, '_asts') or not getattr(self, '_frozen', False): self._analyse(); self._frozen = True\n        # evaluate")],
    # naive recursion: no bottom-up pre-pass (dies on 3,000-cell chain)
    "deep-recursion": [("        for v in order: self._cell(v)\n", "")],
    # cycles detected only via direct refs, not ranges
    "cycle-ignores-ranges": [("        self._formula = set(self._asts)\n",
                              "        self._formula = set(self._asts)\n        self._rects = {k: [r for r in rs if r[0] == r[1]] for k, rs in self._rects.items()}\n")],
    # COUNT does not skip errors
    "count-propagates-errors": [("        if f in (\"SUM\", \"AVERAGE\", \"MIN\", \"MAX\", \"COUNT\"):\n            nums, cnt = [], f == \"COUNT\"",
                                 "        if f in (\"SUM\", \"AVERAGE\", \"MIN\", \"MAX\", \"COUNT\"):\n            nums, cnt = [], False")],
    # IF evaluates both branches eagerly
    "if-eager": [("            c = self._ev(args[0])\n            if isinstance(c, _Err): return c\n            if isinstance(c, str): return VAL",
                  "            c = self._ev(args[0])\n            if isinstance(c, _Err): return c\n            for _a in args[1:]:\n                _v = self._ev(_a)\n                if isinstance(_v, _Err): return _v\n            if isinstance(c, str): return VAL")],
    # text coercion uses str(float) -> "3.0"
    "text-coercion-3.0": [("    if isinstance(v, float): return fmt(v)\n    return str(v)", "    return str(v) if not isinstance(v, bool) else (\"TRUE\" if v else \"FALSE\")")],
    # no undo
    "no-undo": [("        if not self.undo_stack: return False", "        return False")],
    # CSV without quoting
    "csv-no-quoting": [("                if any(ch in s for ch in ',\"\\n'): s = '\"' + s.replace('\"', '\"\"') + '\"'\n", "")],
    # case-sensitive text comparison
    "case-sensitive-compare": [("            if isinstance(a, str): a, b = a.lower(), b.lower()\n", "")],
}

for name, pairs in MUTANTS.items():
    src = mut(REF, pairs)
    p, t, d = lg._sandboxed_import_and_run({"sheet.py": src}, L.LG03_TESTS, timeout=60)
    print(f"{name:26} {p}/{t}  {d[:110]}")
