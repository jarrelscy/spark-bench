"""Mutation check for LG-04 (v7.1 ledger): plausible model mistakes applied to the reference."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/projects/spark-bench-development"))
import long_gen as lg, lg04_ledger as L

REF = open(os.path.expanduser("~/projects/spark-bench-development/tests/fixtures/lg04_ledger_ref.py")).read()

def mut(src, pairs):
    for a, b in pairs:
        assert a in src, a[:70]
        src = src.replace(a, b, 1)
    return src

MUTANTS = {
    "float-money": [("    v = int(a.lstrip(\"-\")) * 100 + int(b)\n    return -v if a.startswith(\"-\") else v",
                     "    return int(round(float(s) * 100))"),
                    ("    x = Fraction(x)\n    n, d = x.numerator, x.denominator",
                     "    return int(round(float(x)))\n    n, d = 0, 1")],
    "bankers-rounding": [("    if 2 * r >= d: q += 1", "    if 2 * r > d or (2 * r == d and q % 2): q += 1")],
    "no-cap": [("            disc = min(rnd(Fraction(self.subtotal * c[\"percent\"], 100)), cents(c[\"cap\"]))",
                "            disc = rnd(Fraction(self.subtotal * c[\"percent\"], 100))")],
    "no-remainder-to-last": [("            elif i < len(self.lines) - 1: sh = rnd(Fraction(disc * l[\"amount\"], self.subtotal))\n            else: sh = disc - acc",
                              "            else: sh = rnd(Fraction(disc * l[\"amount\"], self.subtotal))")],
    "no-final-return-remainder": [("            if l[\"returned\"] == l[\"qty\"]: ref = l[\"net\"] - l[\"refunded\"]\n            else: ref",
                                   "            ref")],
    "no-ts-sort": [("    ordered = [ev for _, ev in sorted(enumerate(events), key=lambda p: (p[1][\"ts\"], p[0]))]",
                    "    ordered = list(events)")],
    "dup-only-applied": [("        if ok: a += 1\n        else: r += 1",
                          "        if ok: a += 1\n        else: r += 1; seen.discard(ev[\"id\"])")],
    "cancel-no-refund": [("                self.refunded += self.paid - self.refunded; self.state = \"CANCELLED\"; return True",
                          "                self.state = \"CANCELLED\"; return True")],
    "return-window-from-order": [("            if ts - self.delivered_ts > 30: return False", "            if ts > 30: return False")],
    "free-order-not-paid": [("            self.state = \"PAID\" if self.total == 0 else \"AWAITING_PAYMENT\"; return True",
                             "            self.state = \"AWAITING_PAYMENT\"; return True")],
    "no-close-on-full-return": [("            if all(x[\"returned\"] == x[\"qty\"] for x in self.lines): self.state = \"CLOSED\"\n", "")],
}

for name, pairs in MUTANTS.items():
    src = mut(REF, pairs)
    p, t, d = lg._sandboxed_import_and_run({"ledger.py": src}, L.LG04_TESTS, timeout=60)
    print(f"{name:28} {p}/{t}  {d[:110]}")
