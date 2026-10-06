"""LG-04 (v7.1, hard): order ledger state machine.

The v7.0 LG-04 (11-state happy path) was saturated: every model 25/25 in
~1-3K tokens. v7.1 keeps the shape (spec -> run_trace -> hidden traces) but adds
the parts real order systems get wrong: partial payments, per-line partial
returns, money in integer cents with half-up rounding, idempotent event ids,
out-of-order timestamps, an event-sourced audit with a replay invariant, and
coupon caps. Every rule tested is in the prompt; traces and answers are grader-side.
"""
import json

LG04_PROMPT = r'''Implement, in Python 3.11 with the standard library only, an order ledger exactly as specified below. Output ONE fenced python code block with the complete module (it will be saved as ledger.py). Write every part completely.

MONEY
- All money is integer cents. Inputs give prices as decimal strings like "19.99" (exactly two decimals, may be "0.00"). Convert exactly (no float math).
- Whenever a rule says "round", round half up to whole cents (e.g. 1234.5 cents -> 1235, 1234.4999 -> 1234), using exact arithmetic (fractions or Decimal).

ORDER
- run_trace(order: dict, events: list[dict]) -> dict. order = {"id": str, "lines": [{"sku": str, "qty": int>=1, "price": "D.DD"}, ...], "coupon": None | {"percent": int 1..100, "cap": "D.DD"}}.
- Subtotal = sum(qty * price). Discount = round(subtotal * percent / 100), but never more than the cap, and 0 without a coupon. Total = subtotal - discount.
- Each line's share of the discount is allocated in proportion to the line amount (qty*price): line_discount = round(discount * line_amount / subtotal) for every line EXCEPT the last line, which gets discount minus the sum of the others (so shares always sum exactly to the discount). Unit net price of a line = (line_amount - line_discount) / qty as an exact fraction (not rounded).
- If subtotal is 0, discount and all shares are 0.

STATES: NEW, AWAITING_PAYMENT, PARTIALLY_PAID, PAID, SHIPPED, DELIVERED, CANCELLED, CLOSED.

EVENTS — each is {"id": str, "type": str, "ts": int, ...}. Process events in ascending ts; ties keep their input order. An event whose id was already seen (applied OR rejected) is a DUPLICATE: it is ignored completely (not applied, not counted as rejected, no audit entry). Otherwise an event is either APPLIED or REJECTED (state unchanged, nothing else changes, audit records it as rejected with a reason string of your choice).
- "place": NEW -> AWAITING_PAYMENT. Rejected if the order has no lines.
- "pay" {"amount": "D.DD"}: allowed in AWAITING_PAYMENT or PARTIALLY_PAID. amount must be > 0 and must not make paid exceed total (else rejected). paid += amount. Then state = PAID if paid == total, else PARTIALLY_PAID. If total is 0, "pay" is always rejected.
- "place" on an order with total 0 goes straight to PAID (paid 0).
- "ship": PAID -> SHIPPED.
- "deliver": SHIPPED -> DELIVERED; records delivered_ts = event ts.
- "cancel": from NEW or AWAITING_PAYMENT -> CANCELLED (no refund). From PARTIALLY_PAID or PAID -> CANCELLED and refunds everything paid so far (refund amount = paid - already refunded). From SHIPPED, DELIVERED, CANCELLED, CLOSED: rejected.
- "return" {"sku": str, "qty": int}: allowed only in DELIVERED and only if ts - delivered_ts <= 30. qty must be >= 1 and the sku must exist; total returned qty of that sku may not exceed its ordered qty (else rejected). Refund = round(qty * unit net price of that line). But the refunds of one line across all its returns must never exceed that line's net amount (line_amount - line_discount): when the line becomes fully returned, its final return refunds exactly the remainder of the line net amount. If every unit of every line is now returned, state becomes CLOSED (a refund still happens for this event).
- "close": DELIVERED -> CLOSED.
- Any other type, or a type not allowed in the current state: rejected.

AUDIT AND REPLAY
- Keep an audit list of {"id", "type", "ts", "result": "applied"|"rejected", "state_after"} for every non-duplicate event, in processing order.
- replay_ok: build a fresh order from the same order dict and re-apply ONLY the audit entries with result "applied", in audit order (same event dicts). replay_ok is True if this second run ends in the same state with the same paid and refunded totals and rejects nothing.

RESULT — run_trace returns exactly these keys:
{"state": str, "subtotal": int, "discount": int, "total": int, "paid": int, "refunded": int, "applied": int, "rejected": int, "duplicates": int, "returned": {sku: qty returned so far, only skus with qty>0}, "audit_len": int, "replay_ok": bool}
All money values are integer cents.

Also include `if __name__ == "__main__":` that reads {"order":..., "events":[...]} JSON from stdin and prints run_trace's result as JSON.
'''


def _cents(s):
    a, b = s.split(".")
    return int(a) * 100 + int(b)


def _cases():
    """(order, events, expected-subset). Expected values below were computed by
    the reference implementation in tests/fixtures/lg04_ledger_ref.py and are
    cross-checked by hand in tests/test_long_gen_graders.py."""
    L = lambda sku, q, p: {"sku": sku, "qty": q, "price": p}
    o1 = {"id": "o1", "lines": [L("A", 2, "10.00"), L("B", 1, "5.50")], "coupon": None}
    oc = {"id": "oc", "lines": [L("A", 3, "9.98"), L("B", 2, "4.01"), L("C", 1, "0.33")], "coupon": {"percent": 15, "cap": "50.00"}}
    ocap = {"id": "ocap", "lines": [L("A", 10, "100.00")], "coupon": {"percent": 20, "cap": "30.00"}}
    ofree = {"id": "of", "lines": [L("A", 1, "0.00")], "coupon": None}
    oempty = {"id": "oe", "lines": [], "coupon": None}
    otie = {"id": "ot", "lines": [L("A", 1, "11.50")], "coupon": {"percent": 15, "cap": "99.00"}}
    otwo = {"id": "o2", "lines": [L("A", 1, "1.00"), L("B", 1, "1.00")], "coupon": {"percent": 50, "cap": "0.01"}}
    ohalf = {"id": "oh", "lines": [L("A", 2, "0.53")], "coupon": {"percent": 1, "cap": "0.01"}}
    ofloat = {"id": "ofl", "lines": [L("A", 3, "0.29"), L("B", 7, "1.15")], "coupon": None}
    o100 = {"id": "o100", "lines": [L("A", 1, "7.00")], "coupon": {"percent": 100, "cap": "99.00"}}
    E = lambda i, t, ts, **kw: dict(id=i, type=t, ts=ts, **kw)
    pay = lambda i, ts, a: E(i, "pay", ts, amount=a)
    happy = [E("e1", "place", 1), pay("e2", 2, "25.50"), E("e3", "ship", 3), E("e4", "deliver", 4)]
    return [
        # 0 happy path, no coupon
        (o1, happy, {"state": "DELIVERED", "subtotal": 2550, "discount": 0, "total": 2550, "paid": 2550, "applied": 4, "rejected": 0}),
        # 1 partial payments then exact completion
        (o1, [E("e1", "place", 1), pay("e2", 2, "10.00"), pay("e3", 3, "15.50")], {"state": "PAID", "paid": 2550}),
        # 2 overpay rejected, state stays partial
        (o1, [E("e1", "place", 1), pay("e2", 2, "10.00"), pay("e3", 3, "15.51")], {"state": "PARTIALLY_PAID", "paid": 1000, "rejected": 1}),
        # 3 zero / negative-like pay rejected
        (o1, [E("e1", "place", 1), pay("e2", 2, "0.00")], {"state": "AWAITING_PAYMENT", "rejected": 1}),
        # 4 coupon allocation and rounding: subtotal 3829, 15% = 574.35 -> 574
        (oc, [E("e1", "place", 1)], {"subtotal": 3829, "discount": 574, "total": 3255}),
        # 5 coupon cap applies: 20% of 1000.00 = 200.00 capped to 30.00
        (ocap, [E("e1", "place", 1)], {"discount": 3000, "total": 97000}),
        # 6 events out of order by ts; ties keep input order
        (o1, [E("e4", "deliver", 4), E("e3", "ship", 3), pay("e2", 2, "25.50"), E("e1", "place", 1)], {"state": "DELIVERED", "applied": 4}),
        # 7 duplicate ids ignored entirely (even if the duplicate would be valid later)
        (o1, [E("e1", "place", 1), pay("e2", 2, "10.00"), pay("e2", 3, "10.00"), E("e1", "place", 4)], {"paid": 1000, "duplicates": 2, "applied": 2, "rejected": 0, "audit_len": 2}),
        # 8 duplicate of a REJECTED event is still a duplicate
        (o1, [E("x", "ship", 1), E("x", "ship", 2), E("e1", "place", 3)], {"rejected": 1, "duplicates": 1, "applied": 1, "state": "AWAITING_PAYMENT"}),
        # 9 cancel from partially paid refunds the paid amount
        (o1, [E("e1", "place", 1), pay("e2", 2, "7.25"), E("e3", "cancel", 3)], {"state": "CANCELLED", "paid": 725, "refunded": 725}),
        # 10 cancel after ship rejected
        (o1, happy[:3] + [E("e9", "cancel", 9)], {"state": "SHIPPED", "refunded": 0, "rejected": 1}),
        # 11 return of one unit, no coupon: refund 10.00
        (o1, happy + [E("r1", "return", 10, sku="A", qty=1)], {"state": "DELIVERED", "refunded": 1000, "returned": {"A": 1}}),
        # 12 return outside 30 days rejected; exactly 30 accepted
        (o1, happy + [E("r1", "return", 35, sku="A", qty=1), E("r2", "return", 34, sku="B", qty=1)], {"returned": {"B": 1}, "refunded": 550, "rejected": 1}),
        # 13 returning everything closes the order
        (o1, happy + [E("r1", "return", 5, sku="A", qty=2), E("r2", "return", 6, sku="B", qty=1)], {"state": "CLOSED", "refunded": 2550}),
        # 14 over-return rejected
        (o1, happy + [E("r1", "return", 5, sku="A", qty=2), E("r2", "return", 6, sku="A", qty=1)], {"returned": {"A": 2}, "rejected": 1, "refunded": 2000}),
        # 15 unknown sku / zero qty return rejected
        (o1, happy + [E("r1", "return", 5, sku="Z", qty=1), E("r2", "return", 6, sku="A", qty=0)], {"rejected": 2, "refunded": 0}),
        # 16 coupon partial returns: line A net = 2994 - round(574*2994/3829)=2994-449=2545; unit 848.33.. -> refunds 848, 848, then remainder 849
        (oc, [E("e1", "place", 1), pay("p", 2, "32.55"), E("s", "ship", 3), E("d", "deliver", 4),
              E("r1", "return", 5, sku="A", qty=1), E("r2", "return", 6, sku="A", qty=1), E("r3", "return", 7, sku="A", qty=1)],
         {"refunded": 2545, "returned": {"A": 3}, "state": "DELIVERED"}),
        # 17 last line absorbs the rounding remainder: full return of all lines refunds exactly the total
        (oc, [E("e1", "place", 1), pay("p", 2, "32.55"), E("s", "ship", 3), E("d", "deliver", 4),
              E("r1", "return", 5, sku="A", qty=3), E("r2", "return", 6, sku="B", qty=2), E("r3", "return", 7, sku="C", qty=1)],
         {"refunded": 3255, "state": "CLOSED"}),
        # 18 two-unit return of line B (net 802 - 120 = 682) refunds 682
        (oc, [E("e1", "place", 1), pay("p", 2, "32.55"), E("s", "ship", 3), E("d", "deliver", 4), E("r", "return", 5, sku="B", qty=2)],
         {"refunded": 682}),
        # 19 free order: place goes straight to PAID, pay rejected
        (ofree, [E("e1", "place", 1), pay("e2", 2, "0.01"), E("e3", "ship", 3)], {"state": "SHIPPED", "paid": 0, "rejected": 1}),
        # 20 100% coupon makes total 0
        (o100, [E("e1", "place", 1), E("e2", "ship", 2)], {"total": 0, "discount": 700, "state": "SHIPPED"}),
        # 21 empty order cannot be placed
        (oempty, [E("e1", "place", 1), pay("e2", 2, "1.00")], {"state": "NEW", "rejected": 2, "subtotal": 0}),
        # 22 unknown event type rejected
        (o1, [E("e1", "warp", 1)], {"state": "NEW", "rejected": 1, "audit_len": 1}),
        # 23 close then return rejected
        (o1, happy + [E("c", "close", 5), E("r", "return", 6, sku="A", qty=1)], {"state": "CLOSED", "rejected": 1, "refunded": 0}),
        # 24 cancel twice: second is rejected, refund not doubled
        (o1, [E("e1", "place", 1), pay("e2", 2, "25.50"), E("c1", "cancel", 3), E("c2", "cancel", 4)], {"refunded": 2550, "rejected": 1}),
        # 25 replay invariant holds on a messy trace
        (oc, [E("d", "deliver", 9), E("e1", "place", 1), E("e1", "place", 2), pay("p1", 3, "10.00"), pay("p2", 4, "30.00"),
              pay("p3", 5, "22.55"), E("s", "ship", 6), E("d2", "deliver", 7), E("r", "return", 8, sku="C", qty=1)],
         {"replay_ok": True, "duplicates": 1}),
        # 26 return exact 30-day boundary relative to delivery ts (not order ts)
        (o1, [E("e1", "place", 1), pay("e2", 2, "25.50"), E("e3", "ship", 3), E("e4", "deliver", 100), E("r", "return", 130, sku="B", qty=1)],
         {"returned": {"B": 1}}),
        # 27 audit records rejected events and state_after length
        (o1, [E("a", "ship", 1), E("b", "place", 2), E("c", "deliver", 3)], {"audit_len": 3, "applied": 1, "rejected": 2}),
        # 28 exact half-cent tie in the discount: 15% of 1150 = 172.5 -> 173 (banker's/float give 172)
        (otie, [E("e1", "place", 1)], {"discount": 173, "total": 977}),
        # 29 tie in a line share + remainder to last line: disc 1 cent over two equal lines -> shares 1 and 0
        (otwo, [E("e1", "place", 1), pay("p", 2, "1.99"), E("s", "ship", 3), E("d", "deliver", 4),
                E("r", "return", 5, sku="A", qty=1)], {"refunded": 99, "paid": 199}),
        # 30 full return over equal lines refunds exactly the total, not the independently rounded shares
        (otwo, [E("e1", "place", 1), pay("p", 2, "1.99"), E("s", "ship", 3), E("d", "deliver", 4),
                E("r", "return", 5, sku="A", qty=1), E("r2", "return", 6, sku="B", qty=1)], {"refunded": 199, "state": "CLOSED"}),
        # 31 half-cent tie in a per-unit return refund: net 105 over 2 units -> 52.5 -> 53
        (ohalf, [E("e1", "place", 1), pay("p", 2, "1.05"), E("s", "ship", 3), E("d", "deliver", 4),
                 E("r", "return", 5, sku="A", qty=1)], {"refunded": 53}),
        # 32 decimal prices that are inexact in binary float: 3 x 0.29 + 7 x 1.15 = 8.92 total
        (ofloat, [E("e1", "place", 1), pay("p", 2, "8.92")], {"subtotal": 892, "state": "PAID"}),
    ]


LG04_TESTS = "import json,sys\nCASES=json.loads(" + repr(json.dumps(_cases())) + ")" + r'''
ns={"__name__":"__lg__"}
try:
    exec(compile(open("ledger.py").read(),"ledger.py","exec"),ns)
except Exception as e:
    print("LG_RESULT 0/10"); print("LG_DETAIL exec:",type(e).__name__,str(e)[:100]); sys.exit(0)
rt=ns.get("run_trace")
if not callable(rt):
    print("LG_RESULT 0/10"); print("LG_DETAIL no run_trace"); sys.exit(0)
import copy
GROUPS={"pricing":[4,5,28,32],"allocation":[16,17,18,29,30],"payments":[1,2,3,19,20],"ordering":[6,26],
 "idempotency":[7,8],"cancel":[9,10,24],"returns":[11,12,14,15,31],"closing":[13,23],"rejections":[21,22,27],"replay":[0,25]}
assert sorted(i for v in GROUPS.values() for i in v)==list(range(len(CASES))),"groups must cover all cases"
p=0; det=[]; failed=set()
for i,(order,events,exp) in enumerate(CASES):
    try:
        r=rt(copy.deepcopy(order),copy.deepcopy(events))
        bad=[k for k,v in exp.items() if r.get(k)!=v or type(r.get(k)) is not type(v)]
        ok=not bad
        if not ok: det.append(f"c{i}:"+",".join(f"{k}={r.get(k)!r}" for k in bad[:2]))
    except Exception as e:
        ok=False; det.append(f"c{i}:{type(e).__name__}")
    if ok: p+=1
    else: failed.add(i)
gp=sum(1 for v in GROUPS.values() if not failed.intersection(v))
bad=[g for g,v in GROUPS.items() if failed.intersection(v)]
print(f"LG_RESULT {gp}/{len(GROUPS)}"); print(f"LG_DETAIL cases {p}/{len(CASES)}; broken: "+",".join(bad)+" | "+";".join(det[:6]))
'''
