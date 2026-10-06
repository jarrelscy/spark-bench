"""LG-04 grader oracle: reference order ledger written to the LG04_PROMPT spec.
Not model evidence; used to validate the grader."""
import json
import sys
from fractions import Fraction

STATES = ("NEW", "AWAITING_PAYMENT", "PARTIALLY_PAID", "PAID", "SHIPPED", "DELIVERED", "CANCELLED", "CLOSED")


def cents(s):
    if not isinstance(s, str) or "." not in s: raise ValueError(s)
    a, b = s.split(".")
    if len(b) != 2 or not a.lstrip("-").isdigit() or not b.isdigit(): raise ValueError(s)
    v = int(a.lstrip("-")) * 100 + int(b)
    return -v if a.startswith("-") else v


def rnd(x):
    x = Fraction(x)
    n, d = x.numerator, x.denominator
    q, r = divmod(abs(n), d)
    if 2 * r >= d: q += 1
    return q if n >= 0 else -q


class Ledger:
    def __init__(self, order):
        self.lines = [dict(sku=l["sku"], qty=int(l["qty"]), amount=int(l["qty"]) * cents(l["price"])) for l in order.get("lines", [])]
        self.subtotal = sum(l["amount"] for l in self.lines)
        c = order.get("coupon")
        disc = 0
        if c and self.subtotal > 0:
            disc = min(rnd(Fraction(self.subtotal * c["percent"], 100)), cents(c["cap"]))
        self.discount = disc
        self.total = self.subtotal - disc
        shares, acc = [], 0
        for i, l in enumerate(self.lines):
            if self.subtotal == 0: sh = 0
            elif i < len(self.lines) - 1: sh = rnd(Fraction(disc * l["amount"], self.subtotal))
            else: sh = disc - acc
            acc += sh; shares.append(sh)
        for l, sh in zip(self.lines, shares):
            l["net"] = l["amount"] - sh; l["returned"] = 0; l["refunded"] = 0
        self.by_sku = {l["sku"]: l for l in self.lines}
        self.state = "NEW"; self.paid = 0; self.refunded = 0; self.delivered_ts = None

    def apply(self, e):
        t, s, ts = e.get("type"), self.state, e.get("ts")
        if t == "place" and s == "NEW":
            if not self.lines: return False
            self.state = "PAID" if self.total == 0 else "AWAITING_PAYMENT"; return True
        if t == "pay" and s in ("AWAITING_PAYMENT", "PARTIALLY_PAID"):
            if self.total == 0: return False
            try: a = cents(e.get("amount"))
            except Exception: return False
            if a <= 0 or self.paid + a > self.total: return False
            self.paid += a; self.state = "PAID" if self.paid == self.total else "PARTIALLY_PAID"; return True
        if t == "ship" and s == "PAID": self.state = "SHIPPED"; return True
        if t == "deliver" and s == "SHIPPED": self.state = "DELIVERED"; self.delivered_ts = ts; return True
        if t == "cancel":
            if s in ("NEW", "AWAITING_PAYMENT"): self.state = "CANCELLED"; return True
            if s in ("PARTIALLY_PAID", "PAID"):
                self.refunded += self.paid - self.refunded; self.state = "CANCELLED"; return True
            return False
        if t == "return" and s == "DELIVERED":
            if ts - self.delivered_ts > 30: return False
            l = self.by_sku.get(e.get("sku")); q = e.get("qty")
            if l is None or not isinstance(q, int) or q < 1 or l["returned"] + q > l["qty"]: return False
            l["returned"] += q
            if l["returned"] == l["qty"]: ref = l["net"] - l["refunded"]
            else: ref = min(rnd(Fraction(q * l["net"], l["qty"])), l["net"] - l["refunded"])
            l["refunded"] += ref; self.refunded += ref
            if all(x["returned"] == x["qty"] for x in self.lines): self.state = "CLOSED"
            return True
        if t == "close" and s == "DELIVERED": self.state = "CLOSED"; return True
        return False


def _run(order, events):
    L = Ledger(order); seen = set(); audit = []; a = r = dup = 0
    ordered = [ev for _, ev in sorted(enumerate(events), key=lambda p: (p[1]["ts"], p[0]))]
    for ev in ordered:
        if ev["id"] in seen: dup += 1; continue
        seen.add(ev["id"])
        ok = L.apply(ev)
        if ok: a += 1
        else: r += 1
        audit.append({"id": ev["id"], "type": ev["type"], "ts": ev["ts"], "result": "applied" if ok else "rejected", "state_after": L.state, "_ev": ev})
    return L, audit, a, r, dup


def run_trace(order, events):
    L, audit, a, r, dup = _run(order, events)
    L2 = Ledger(order); rej2 = 0
    for x in audit:
        if x["result"] == "applied":
            if not L2.apply(x["_ev"]): rej2 += 1
    replay_ok = rej2 == 0 and (L2.state, L2.paid, L2.refunded) == (L.state, L.paid, L.refunded)
    return {"state": L.state, "subtotal": L.subtotal, "discount": L.discount, "total": L.total, "paid": L.paid,
            "refunded": L.refunded, "applied": a, "rejected": r, "duplicates": dup,
            "returned": {l["sku"]: l["returned"] for l in L.lines if l["returned"] > 0},
            "audit_len": len(audit), "replay_ok": replay_ok}


if __name__ == "__main__":
    d = json.load(sys.stdin); print(json.dumps(run_trace(d["order"], d["events"])))
