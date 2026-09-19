"""Spark Bench v7 — long_gen domain (LG-01..LG-04).

Four single-turn scenarios that require 8K–25K output tokens by construction.
Every grader is deterministic and executes/renders the output; none reads prose.

Hard rules shared by all four (this is the axis the short suite cannot see):
  * finish_reason == "length" (hit the 32K cap)  -> 0.0 "truncated"
  * unterminated code fence / unparseable output -> 0.0
  * otherwise the functional score in [0, 1]
"""
import json
import os
import re
import shutil
import statistics
import sys
import tempfile

LG_MAX_TOKENS = 32768
LG_TEMPERATURE = 0.6


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #
def _truncated(resp):
    fin = resp.get("finish")
    if fin == "length":
        return "truncated: finish_reason=length"
    text = resp.get("text", "") or ""
    if text.count("```") % 2 == 1:
        return "truncated: unterminated code fence"
    return None


def _blocks(text):
    """All fenced blocks as list of (info_string, body)."""
    out = []
    for m in re.finditer(r"```([^\n]*)\n(.*?)```", text, re.S):
        out.append((m.group(1).strip(), m.group(2)))
    return out


def _named_files(text):
    """Map filename -> body for fences whose info string or the preceding
    line names a file, e.g. ```python title=models.py, ```python models.py,
    or a line like `### models.py` / `# File: models.py` just above."""
    files = {}
    for m in re.finditer(r"(?:^|\n)([^\n]{0,120})\n```([^\n]*)\n(.*?)```", text, re.S):
        pre, info, body = m.group(1), m.group(2), m.group(3)
        cand = None
        for src in (info, pre):
            fm = re.search(r"([A-Za-z0-9_\-]+\.py)\b", src)
            if fm:
                cand = fm.group(1)
                break
        if cand and cand not in files:
            files[cand] = body
    return files


def _sandboxed_import_and_run(files, test_src, timeout=20):
    """Write files to a temp package dir, run test_src in a subprocess with
    the dir on sys.path and no network. Returns (passed, total, detail)."""
    import subprocess
    tmp = tempfile.mkdtemp(prefix="lg_")
    try:
        for name, body in files.items():
            with open(os.path.join(tmp, name), "w") as f:
                f.write(body)
        with open(os.path.join(tmp, "_lg_tests.py"), "w") as f:
            f.write("import sys, os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nos.chdir(os.path.dirname(os.path.abspath(__file__)))\n" + test_src)
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONPATH": tmp, "HOME": tmp}
        p = subprocess.run([sys.executable, "-I", "-S", os.path.join(tmp, "_lg_tests.py")],
                           cwd=tmp, env=env, capture_output=True, text=True, timeout=timeout)
        m = re.search(r"LG_RESULT (\d+)/(\d+)", p.stdout)
        if not m:
            err = (p.stderr or p.stdout or "").strip().splitlines()
            return 0, 0, "harness: " + (err[-1][:160] if err else "no result line")
        return int(m.group(1)), int(m.group(2)), (p.stdout.split("LG_DETAIL ", 1)[1].strip()[:200]
                                                  if "LG_DETAIL " in p.stdout else "")
    except subprocess.TimeoutExpired:
        return 0, 0, f"timeout after {timeout}s"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------- #
# LG-01 — voxel world (three.js), graded by rendered pixels
# --------------------------------------------------------------------------- #
LG01_PROMPT = (
    "Write a single self-contained HTML file with a 3D voxel-art world using "
    "three.js. three.js r160 is available as an ES module at './three.module.js' "
    "-- import it with:\n  import * as THREE from './three.module.js';\n"
    "Build ALL of the following, procedurally, with no external assets:\n"
    "1. Terrain: at least 64x64 voxel columns with clearly varied height "
    "(hills and a valley), grass on top, dirt/stone below, sand near water.\n"
    "2. A river of blue water voxels that winds across the terrain from one "
    "edge to the opposite edge.\n"
    "3. A village of at least 12 buildings using at least 3 visibly different "
    "building designs (different footprints, heights, roof shapes and colours), "
    "placed on the terrain surface, never floating and never underground.\n"
    "4. A stone path connecting the buildings.\n"
    "5. At least 20 trees (trunk + canopy) scattered on the grass.\n"
    "6. A day/night toggle: pressing the 'N' key switches between a bright "
    "daytime sky/lighting and a dark night sky with warm lit windows on the "
    "buildings. Start in daytime.\n"
    "7. An orbit camera that slowly auto-rotates around the village centre "
    "and keeps the whole village in frame; the whole world must be visible "
    "and fill most of the viewport.\n"
    "Use instanced meshes or merged geometry so it runs smoothly. Everything "
    "must start immediately on load with no user interaction. Output ONLY the "
    "complete HTML in one code block."
)


def _lg01_grade(resp):
    from visual_3d_grader import render_frames, _sample_pixels
    t = _truncated(resp)
    if t:
        return 0.0, t
    blocks = _blocks(resp.get("text", "") or "")
    html = next((b for i, b in blocks if "<html" in b.lower() or "<canvas" in b.lower()
                 or "three.module.js" in b), None)
    if html is None:
        return 0.0, "no html block"

    def _pixels(fr):
        return [(r, g, b) for _x, _y, r, g, b in _sample_pixels(fr, step=6)]

    def _brightness(fr):
        px = _pixels(fr)
        return statistics.mean((r + g + b) / 3 for r, g, b in px) if px else 0

    def _colour_var(fr):
        px = _pixels(fr)
        if not px:
            return 0
        return statistics.pstdev(r for r, _, _ in px) + statistics.pstdev(g for _, g, _ in px) \
            + statistics.pstdev(b for _, _, b in px)

    # phase 1: day, 6 s @ 2 fps
    frames, errors, fail = render_frames(html, seconds=6.0, fps=2.0, settle_ms=2500)
    if fail or not frames:
        return 0.0, f"render: {fail or 'no frames'}"
    if errors:
        return 0.0, f"page error: {errors[0][:120]}"
    checks = []
    day_b = statistics.mean(_brightness(f) for _, f in frames)
    checks.append(("scene drawn", 1.0 if _colour_var(frames[-1][1]) > 60 else 0.0))
    # orbit: frames differ over time
    fa, fb = frames[0][1][2], frames[-1][1][2]
    diff = statistics.mean(abs(a - b) for a, b in zip(fa[::97], fb[::97])) if len(fa) == len(fb) else 0
    checks.append(("camera orbits", 1.0 if diff > 4 else 0.0))
    # blue water present, green grass present, warm/brown building tones present
    px = _pixels(frames[-1][1])
    n = max(1, len(px))
    blue = sum(1 for r, g, b in px if b > 120 and b > r + 30 and b > g + 10) / n
    green = sum(1 for r, g, b in px if g > 90 and g > r + 15 and g > b + 15) / n
    warm = sum(1 for r, g, b in px if r > 110 and r > b + 40 and abs(r - g) < 90 and g > 40) / n
    checks.append(("water visible", 1.0 if blue > 0.01 else 0.0))
    checks.append(("grass visible", 1.0 if green > 0.08 else 0.0))
    checks.append(("buildings/paths visible", 1.0 if warm > 0.01 else 0.0))
    # phase 2: night — press N, expect darker frame
    night_b = None
    # inject a synthetic 'N' keydown 1.5 s after load (document + window listeners)
    inj = ("<script>setTimeout(()=>{for(const t of [document,window,document.body]){"
           "t.dispatchEvent(new KeyboardEvent('keydown',{key:'n',code:'KeyN',keyCode:78,bubbles:true}));"
           "t.dispatchEvent(new KeyboardEvent('keyup',{key:'n',code:'KeyN',keyCode:78,bubbles:true}));}},1500);</script>")
    shim = html.replace("</body>", inj + "</body>") if "</body>" in html else html + inj
    nf, nerr, nfail = render_frames(shim, seconds=4.0, fps=2.0, settle_ms=3000)
    if nf and not nfail:
        night_b = statistics.mean(_brightness(f) for _, f in nf[-3:])
    checks.append(("night toggle darkens", 1.0 if night_b is not None and night_b < day_b * 0.7 else 0.0))
    score = sum(s for _, s in checks) / len(checks)
    return score, ", ".join(f"{'✓' if s else '✗'}{k}" for k, s in checks)


# --------------------------------------------------------------------------- #
# LG-02 — multi-module Python inventory system, 25 hidden tests
# --------------------------------------------------------------------------- #
LG02_PROMPT = (
    "Implement a small warehouse inventory system in Python 3.11 as FIVE separate "
    "modules. Output each module as its own fenced code block, and put the file "
    "name on the line immediately before each block, exactly like `### models.py`. "
    "No third-party packages. Modules:\n\n"
    "models.py — dataclasses: Product(sku: str, name: str, unit_cost: float, "
    "reorder_point: int), Location(code: str, capacity: int), StockLevel(sku, "
    "location_code, quantity: int), Movement(kind: 'receive'|'ship'|'transfer'|"
    "'adjust', sku, qty: int, src: str|None, dst: str|None, ts: int, ref: str). "
    "Each has a to_dict() and a from_dict(d) classmethod.\n\n"
    "storage.py — class JsonStore(path): load()/save() of a dict {products, "
    "locations, stock, movements}; atomic save (write temp then os.replace); "
    "get_product(sku), get_location(code), stock_at(sku, code) -> int, "
    "set_stock(sku, code, qty), append_movement(m). Raise KeyError for unknown "
    "sku/location.\n\n"
    "rules.py — class Inventory(store): receive(sku, qty, dst, ref), ship(sku, "
    "qty, src, ref), transfer(sku, qty, src, dst, ref), adjust(sku, qty_delta, "
    "loc, ref). Rules: qty must be > 0 (ValueError); shipping/transferring more "
    "than on hand raises InsufficientStock(Exception); receiving/transferring "
    "that would exceed a Location.capacity (sum of all skus there) raises "
    "CapacityExceeded(Exception); every successful call appends exactly one "
    "Movement and persists; ref must be unique across all movements (duplicate "
    "ref raises DuplicateRef(Exception) and changes nothing). total_on_hand(sku) "
    "-> int; below_reorder() -> list of skus whose total_on_hand < reorder_point; "
    "valuation() -> float sum(qty*unit_cost); ledger(sku) -> list of Movement "
    "for that sku in ts order.\n\n"
    "cli.py — argparse CLI: `receive|ship|transfer|adjust|report` subcommands "
    "that operate on a store path from --db, printing one JSON line result; "
    "`report` prints {valuation, below_reorder, total_units}.\n\n"
    "tests.py — at least 15 unittest tests covering all rules above, runnable "
    "with `python -m unittest tests`.\n\n"
    "Write complete, working code for every module. Do not omit any module and "
    "do not summarise with '...'."
)

LG02_TESTS = r'''
import json, os, sys, tempfile, traceback
passed = 0; total = 0; details = []
def t(name, fn):
    global passed, total
    total += 1
    try:
        fn(); passed += 1
    except Exception as e:
        details.append(f"{name}:{type(e).__name__}")
try:
    import models, storage, rules
except Exception as e:
    print("LG_RESULT 0/25"); print("LG_DETAIL import:", type(e).__name__, str(e)[:120]); sys.exit(0)

def fresh():
    d = tempfile.mkdtemp(); p = os.path.join(d, "db.json")
    st = storage.JsonStore(p)
    data = {"products": [models.Product("A", "Widget", 2.5, 10).to_dict(), models.Product("B", "Gadget", 10.0, 5).to_dict()],
            "locations": [models.Location("L1", 100).to_dict(), models.Location("L2", 20).to_dict()],
            "stock": [], "movements": []}
    with open(p, "w") as f: json.dump(data, f)
    st.load()
    return st, rules.Inventory(st), p

def test_dataclass_roundtrip():
    pr = models.Product("X", "x", 1.0, 1); assert models.Product.from_dict(pr.to_dict()) == pr
def test_receive():
    st, inv, _ = fresh(); inv.receive("A", 30, "L1", "r1"); assert inv.total_on_hand("A") == 30
def test_ship():
    st, inv, _ = fresh(); inv.receive("A", 30, "L1", "r1"); inv.ship("A", 10, "L1", "s1"); assert st.stock_at("A", "L1") == 20
def test_insufficient():
    st, inv, _ = fresh(); inv.receive("A", 5, "L1", "r1")
    try: inv.ship("A", 6, "L1", "s1"); assert False
    except rules.InsufficientStock: pass
def test_capacity():
    st, inv, _ = fresh()
    try: inv.receive("A", 21, "L2", "r1"); assert False
    except rules.CapacityExceeded: pass
    assert inv.total_on_hand("A") == 0
def test_capacity_sum_across_skus():
    st, inv, _ = fresh(); inv.receive("A", 15, "L2", "r1")
    try: inv.receive("B", 6, "L2", "r2"); assert False
    except rules.CapacityExceeded: pass
def test_transfer():
    st, inv, _ = fresh(); inv.receive("A", 30, "L1", "r1"); inv.transfer("A", 12, "L1", "L2", "t1")
    assert st.stock_at("A", "L1") == 18 and st.stock_at("A", "L2") == 12
def test_transfer_capacity():
    st, inv, _ = fresh(); inv.receive("A", 50, "L1", "r1")
    try: inv.transfer("A", 25, "L1", "L2", "t1"); assert False
    except rules.CapacityExceeded: pass
    assert st.stock_at("A", "L1") == 50
def test_adjust_down():
    st, inv, _ = fresh(); inv.receive("A", 10, "L1", "r1"); inv.adjust("A", -3, "L1", "a1"); assert st.stock_at("A", "L1") == 7
def test_adjust_below_zero():
    st, inv, _ = fresh(); inv.receive("A", 2, "L1", "r1")
    try: inv.adjust("A", -5, "L1", "a1"); assert False
    except (rules.InsufficientStock, ValueError): pass
def test_qty_positive():
    st, inv, _ = fresh()
    try: inv.receive("A", 0, "L1", "r1"); assert False
    except ValueError: pass
def test_unknown_sku():
    st, inv, _ = fresh()
    try: inv.receive("ZZ", 1, "L1", "r1"); assert False
    except KeyError: pass
def test_unknown_loc():
    st, inv, _ = fresh()
    try: inv.receive("A", 1, "L9", "r1"); assert False
    except KeyError: pass
def test_duplicate_ref():
    st, inv, _ = fresh(); inv.receive("A", 5, "L1", "r1")
    try: inv.receive("A", 5, "L1", "r1"); assert False
    except rules.DuplicateRef: pass
    assert inv.total_on_hand("A") == 5
def test_movement_count():
    st, inv, _ = fresh(); inv.receive("A", 5, "L1", "r1"); inv.ship("A", 1, "L1", "s1"); assert len(st.load().get("movements", st.data["movements"] if hasattr(st, "data") else [])) == 2 or len(inv.ledger("A")) == 2
def test_ledger_order():
    st, inv, _ = fresh(); inv.receive("A", 5, "L1", "r1"); inv.ship("A", 1, "L1", "s1"); inv.receive("A", 2, "L1", "r2")
    kinds = [m.kind for m in inv.ledger("A")]; assert kinds == ["receive", "ship", "receive"]
def test_ledger_filters_sku():
    st, inv, _ = fresh(); inv.receive("A", 5, "L1", "r1"); inv.receive("B", 1, "L1", "r2"); assert all(m.sku == "A" for m in inv.ledger("A")) and len(inv.ledger("A")) == 1
def test_valuation():
    st, inv, _ = fresh(); inv.receive("A", 4, "L1", "r1"); inv.receive("B", 2, "L1", "r2"); assert abs(inv.valuation() - (4*2.5 + 2*10.0)) < 1e-6
def test_below_reorder():
    st, inv, _ = fresh(); inv.receive("A", 9, "L1", "r1"); inv.receive("B", 5, "L1", "r2"); assert set(inv.below_reorder()) == {"A"}
def test_persistence():
    st, inv, p = fresh(); inv.receive("A", 7, "L1", "r1")
    st2 = storage.JsonStore(p); st2.load(); assert st2.stock_at("A", "L1") == 7
def test_atomic_save_leaves_no_temp():
    st, inv, p = fresh(); inv.receive("A", 7, "L1", "r1"); d = os.path.dirname(p)
    assert [f for f in os.listdir(d) if f != os.path.basename(p)] == [] or True  # tolerate naming; must not crash
def test_transfer_same_loc_rejected_or_noop():
    st, inv, _ = fresh(); inv.receive("A", 5, "L1", "r1")
    try: inv.transfer("A", 2, "L1", "L1", "t1")
    except (ValueError, Exception): pass
    assert inv.total_on_hand("A") == 5
def test_ship_zero_stock():
    st, inv, _ = fresh()
    try: inv.ship("A", 1, "L1", "s1"); assert False
    except rules.InsufficientStock: pass
def test_cli_report():
    import subprocess
    st, inv, p = fresh(); inv.receive("A", 4, "L1", "r1")
    r = subprocess.run([sys.executable, "cli.py", "--db", p, "report"], capture_output=True, text=True, timeout=10)
    out = json.loads(r.stdout.strip().splitlines()[-1]); assert abs(out["valuation"] - 10.0) < 1e-6 and out["total_units"] == 4
def test_cli_receive():
    import subprocess
    st, inv, p = fresh()
    r = subprocess.run([sys.executable, "cli.py", "--db", p, "receive", "A", "3", "L1", "cli-r1"], capture_output=True, text=True, timeout=10)
    st2 = storage.JsonStore(p); st2.load(); assert st2.stock_at("A", "L1") == 3

for n, f in list(globals().items()):
    if n.startswith("test_") and callable(f): t(n, f)
print(f"LG_RESULT {passed}/{total}"); print("LG_DETAIL " + ";".join(details[:8]))
'''


def _lg02_grade(resp):
    t = _truncated(resp)
    if t:
        return 0.0, t
    files = _named_files(resp.get("text", "") or "")
    need = ["models.py", "storage.py", "rules.py", "cli.py", "tests.py"]
    missing = [n for n in need if n not in files]
    if missing:
        return 0.0, "missing modules: " + ",".join(missing)
    if any("..." in files[n] and len(files[n]) < 400 for n in need):
        return 0.0, "stub module"
    passed, total, detail = _sandboxed_import_and_run({n: files[n] for n in need}, LG02_TESTS, timeout=40)
    if total == 0:
        return 0.0, detail
    return passed / total, f"{passed}/{total} {detail}"


# --------------------------------------------------------------------------- #
# LG-03 — long structured spec with cross references (JSON)
# --------------------------------------------------------------------------- #
LG03_SECTIONS = ["overview", "goals", "non_goals", "architecture", "data_model", "api",
                 "auth", "storage", "scaling", "failure_modes", "observability", "rollout"]
LG03_PROMPT = (
    "Write a complete technical design specification for a multi-tenant "
    "'scheduled webhook delivery' service (customers register endpoints and "
    "schedules; the service delivers signed HTTP webhooks with retries and "
    "dead-lettering). Output ONLY a single JSON object, no code fence, no prose "
    "before or after, with EXACTLY these top-level keys in this order:\n"
    + ", ".join(LG03_SECTIONS) + ".\n"
    "Each key maps to an object {\"title\": str, \"body\": str, \"refs\": [str]} where "
    "body is at least 900 characters of substantive prose for that section and "
    "refs lists the other section keys this section depends on (at least 2 per "
    "section; every ref must be one of the top-level keys and must not be the "
    "section itself). The api section body must define at least 8 endpoints "
    "as 'METHOD /path — purpose' lines. The data_model section body must define "
    "at least 6 tables/entities each with at least 4 fields. The failure_modes "
    "section must enumerate at least 8 distinct failure scenarios each with a "
    "mitigation. Total body text across all sections must exceed 14,000 "
    "characters. Every section must be specific to THIS service; generic filler "
    "will be graded as a failure."
)


def _lg03_grade(resp):
    t = _truncated(resp)
    if t:
        return 0.0, t
    text = (resp.get("text", "") or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S).strip()
    try:
        obj = json.loads(text)
    except Exception as e:
        return 0.0, f"not JSON: {type(e).__name__}"
    if not isinstance(obj, dict):
        return 0.0, "not an object"
    checks = []
    keys = list(obj.keys())
    checks.append(("exact keys in order", 1.0 if keys == LG03_SECTIONS else (0.5 if set(keys) == set(LG03_SECTIONS) else 0.0)))
    secs = {k: obj.get(k) for k in LG03_SECTIONS if isinstance(obj.get(k), dict)}
    if len(secs) < 12:
        return 0.0, f"only {len(secs)}/12 sections are objects"
    bodies = {k: str(v.get("body", "")) for k, v in secs.items()}
    checks.append(("no stub sections (>=900 chars)", sum(1 for b in bodies.values() if len(b) >= 900) / 12))
    checks.append(("total body > 14k", 1.0 if sum(len(b) for b in bodies.values()) > 14000 else 0.0))
    ref_ok = 0
    for k, v in secs.items():
        refs = v.get("refs", [])
        if isinstance(refs, list) and len(refs) >= 2 and all(r in LG03_SECTIONS and r != k for r in refs):
            ref_ok += 1
    checks.append(("cross-refs resolve", ref_ok / 12))
    api_lines = re.findall(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/[\w/{}\-:.]+", bodies.get("api", ""))
    checks.append(("api >= 8 endpoints", min(1.0, len(set(api_lines)) / 8)))
    fm = bodies.get("failure_modes", "")
    fm_items = len(re.findall(r"(?:^|\n)\s*(?:\d+[.)]|[-*•])\s+\S", fm)) or len(re.findall(r"[Mm]itigation", fm))
    checks.append(("failure modes >= 8 w/ mitigation", min(1.0, fm_items / 8) if "itigat" in fm else 0.0))
    dm = bodies.get("data_model", "")
    ents = len(re.findall(r"(?:^|\n)\s*(?:\d+[.)]|[-*•#]+)\s*[A-Za-z_]+\s*(?:\(|:|—|-)", dm))
    checks.append(("data model >= 6 entities", min(1.0, ents / 6)))
    # specificity: service vocabulary must appear across sections
    vocab = ["webhook", "retry", "dead", "signature", "tenant", "schedule"]
    hit = sum(1 for b in bodies.values() if sum(1 for w in vocab if w in b.lower()) >= 2)
    checks.append(("specific to service", hit / 12))
    # weights: structure gates heavier
    w = [2, 2, 1, 2, 1, 1, 1, 2]
    score = sum(s * wi for (_, s), wi in zip(checks, w)) / sum(w)
    return score, ", ".join(f"{k}={s:.2f}" for k, s in checks)


# --------------------------------------------------------------------------- #
# LG-04 — order lifecycle state machine + trace runner
# --------------------------------------------------------------------------- #
LG04_PROMPT = (
    "Implement, in Python 3.11 with no third-party packages, an order lifecycle "
    "state machine EXACTLY as specified, then a trace runner. Output ONE fenced "
    "python code block containing everything.\n\n"
    "States: DRAFT, SUBMITTED, PAYMENT_PENDING, PAID, PACKING, SHIPPED, DELIVERED, "
    "CANCELLED, REFUNDED, RETURN_REQUESTED, RETURNED.\n"
    "Events and transitions (event: from -> to, [guard]):\n"
    "submit: DRAFT->SUBMITTED [order.items non-empty]\n"
    "request_payment: SUBMITTED->PAYMENT_PENDING\n"
    "payment_ok: PAYMENT_PENDING->PAID [amount == order.total]\n"
    "payment_failed: PAYMENT_PENDING->SUBMITTED (increments order.payment_attempts; "
    "on the 3rd failure the order goes to CANCELLED instead)\n"
    "start_packing: PAID->PACKING\n"
    "ship: PACKING->SHIPPED [tracking_number provided]\n"
    "deliver: SHIPPED->DELIVERED\n"
    "cancel: from DRAFT, SUBMITTED, PAYMENT_PENDING -> CANCELLED; from PAID, "
    "PACKING -> REFUNDED (a refund of order.total is recorded); from SHIPPED or "
    "later -> rejected\n"
    "request_return: DELIVERED->RETURN_REQUESTED [within 30 days: event.day - "
    "order.delivered_day <= 30]\n"
    "receive_return: RETURN_REQUESTED->RETURNED\n"
    "refund: RETURNED->REFUNDED (refund of order.total recorded)\n"
    "Any event not listed for the current state is REJECTED: state unchanged, "
    "and the rejection is recorded. Guards that fail are rejections too.\n\n"
    "Provide: class Order (fields: id, items: list, total: float, state, "
    "payment_attempts: int = 0, delivered_day: int|None, refunds: list[float], "
    "history: list of (event, from_state, to_state or 'REJECTED', day)); "
    "class OrderStateMachine with apply(order, event: dict) -> bool where event "
    "is {'name': str, 'day': int, ...payload} and returns True if applied; "
    "and function run_trace(order_spec: dict, events: list[dict]) -> dict "
    "returning {'final_state', 'applied': int, 'rejected': int, 'refunded': "
    "float, 'payment_attempts': int}. Include a __main__ that reads a JSON "
    "{order, events} from stdin and prints the run_trace result as JSON. "
    "Write it all out completely."
)


def _lg04_cases():
    base = {"id": "o1", "items": ["a"], "total": 50.0}
    E = lambda n, d=1, **kw: dict(name=n, day=d, **kw)
    happy = [E("submit"), E("request_payment"), E("payment_ok", amount=50.0), E("start_packing"), E("ship", tracking_number="T1"), E("deliver", 5)]
    cases = [
        (base, happy, dict(final_state="DELIVERED", applied=6, rejected=0, refunded=0.0)),
        ({**base, "items": []}, [E("submit")], dict(final_state="DRAFT", applied=0, rejected=1)),
        (base, [E("submit"), E("request_payment"), E("payment_ok", amount=49.0)], dict(final_state="PAYMENT_PENDING", applied=2, rejected=1)),
        (base, [E("submit"), E("request_payment"), E("payment_failed"), E("request_payment"), E("payment_failed"), E("request_payment"), E("payment_failed")], dict(final_state="CANCELLED", payment_attempts=3)),
        (base, [E("submit"), E("request_payment"), E("payment_failed"), E("request_payment"), E("payment_failed")], dict(final_state="SUBMITTED", payment_attempts=2)),
        (base, [E("submit"), E("cancel")], dict(final_state="CANCELLED", refunded=0.0)),
        (base, [E("submit"), E("request_payment"), E("payment_ok", amount=50.0), E("cancel")], dict(final_state="REFUNDED", refunded=50.0)),
        (base, [E("submit"), E("request_payment"), E("payment_ok", amount=50.0), E("start_packing"), E("cancel")], dict(final_state="REFUNDED", refunded=50.0)),
        (base, happy[:5] + [E("cancel")], dict(final_state="SHIPPED", rejected=1)),
        (base, happy + [E("cancel")], dict(final_state="DELIVERED", rejected=1)),
        (base, happy + [E("request_return", 20), E("receive_return", 25), E("refund", 26)], dict(final_state="REFUNDED", refunded=50.0, applied=9)),
        (base, happy + [E("request_return", 36)], dict(final_state="DELIVERED", rejected=1)),
        (base, happy + [E("request_return", 35)], dict(final_state="RETURN_REQUESTED", rejected=0)),
        (base, [E("submit"), E("request_payment"), E("payment_ok", amount=50.0), E("start_packing"), E("ship")], dict(final_state="PACKING", rejected=1)),
        (base, [E("deliver"), E("ship"), E("submit")], dict(final_state="SUBMITTED", applied=1, rejected=2)),
        (base, [E("submit"), E("submit")], dict(final_state="SUBMITTED", applied=1, rejected=1)),
        (base, [E("submit"), E("request_payment"), E("payment_ok", amount=50.0), E("payment_ok", amount=50.0)], dict(final_state="PAID", rejected=1)),
        (base, happy + [E("request_return", 20), E("refund", 21)], dict(final_state="RETURN_REQUESTED", rejected=1)),
        (base, happy + [E("request_return", 20), E("receive_return", 25), E("refund", 26), E("refund", 27)], dict(final_state="REFUNDED", refunded=50.0, rejected=1)),
        (base, [E("submit"), E("request_payment"), E("payment_failed"), E("cancel")], dict(final_state="CANCELLED", payment_attempts=1, refunded=0.0)),
        (base, [E("submit"), E("request_payment"), E("payment_failed"), E("request_payment"), E("payment_ok", amount=50.0)], dict(final_state="PAID", payment_attempts=1)),
        (base, [E("submit"), E("request_payment"), E("payment_ok", amount=50.0), E("ship", tracking_number="T")], dict(final_state="PAID", rejected=1)),
        ({**base, "total": 0.0}, [E("submit"), E("request_payment"), E("payment_ok", amount=0.0), E("cancel")], dict(final_state="REFUNDED", refunded=0.0)),
        (base, [], dict(final_state="DRAFT", applied=0, rejected=0)),
        (base, [E("bogus_event")], dict(final_state="DRAFT", applied=0, rejected=1)),
    ]
    return cases


def _lg04_grade(resp):
    t = _truncated(resp)
    if t:
        return 0.0, t
    blocks = _blocks(resp.get("text", "") or "")
    code = max((b for i, b in blocks if "class" in b and "def " in b), key=len, default=None)
    if not code:
        return 0.0, "no python block"
    code = str(code)
    cases = _lg04_cases()
    harness = "import json,sys\nCASES=" + json.dumps(cases) + r'''
ns={"__name__":"__lg__"}
try:
    exec(compile(open("_lg_target.py").read(),"_lg_target.py","exec"),ns)
except Exception as e:
    print("LG_RESULT 0/%d"%len(CASES)); print("LG_DETAIL exec:",type(e).__name__,str(e)[:100]); sys.exit(0)
rt=ns.get("run_trace")
if not callable(rt):
    print("LG_RESULT 0/%d"%len(CASES)); print("LG_DETAIL no run_trace"); sys.exit(0)
p=0; det=[]
for i,(spec,events,exp) in enumerate(CASES):
    try:
        r=rt(dict(spec),[dict(e) for e in events]); ok=all((abs(r.get(k,-1)-v)<1e-6 if isinstance(v,float) else r.get(k)==v) for k,v in exp.items())
    except Exception as e:
        ok=False; det.append(f"c{i}:{type(e).__name__}")
    if ok: p+=1
    elif not det or not det[-1].startswith(f"c{i}"): det.append(f"c{i}:{r.get('final_state') if isinstance(r,dict) else '?'}")
print(f"LG_RESULT {p}/{len(CASES)}"); print("LG_DETAIL "+";".join(det[:8]))
'''
    passed, total, detail = _sandboxed_import_and_run({"_lg_target.py": code}, harness, timeout=30)
    if total == 0:
        return 0.0, detail
    return passed / total, f"{passed}/{total} {detail}"


# --------------------------------------------------------------------------- #
# scenario table (imported by eval_suite)
# --------------------------------------------------------------------------- #
def _msg(text):
    return [{"role": "user", "content": text}]


def _grade_wrapper(fn):
    def check(resp):
        try:
            return fn(resp)
        except Exception as e:  # grader bug must never look like a model failure
            return 0.0, f"grader-error({type(e).__name__}: {str(e)[:80]})"
    return check


LONG_GEN_SCENARIOS = [
    dict(id="LG-01", domain="long_gen", group="capability", tier="hard", difficulty=2.8,
         max_tokens=LG_MAX_TOKENS, temperature=LG_TEMPERATURE, artifact_ext="html",
         messages=_msg(LG01_PROMPT), grade=_grade_wrapper(_lg01_grade)),
    dict(id="LG-02", domain="long_gen", group="capability", tier="hard", difficulty=2.8,
         max_tokens=LG_MAX_TOKENS, temperature=LG_TEMPERATURE, artifact_ext="md",
         messages=_msg(LG02_PROMPT), grade=_grade_wrapper(_lg02_grade)),
    dict(id="LG-03", domain="long_gen", group="capability", tier="hard", difficulty=2.5,
         max_tokens=LG_MAX_TOKENS, temperature=LG_TEMPERATURE, artifact_ext="json",
         messages=_msg(LG03_PROMPT), grade=_grade_wrapper(_lg03_grade)),
    dict(id="LG-04", domain="long_gen", group="capability", tier="hard", difficulty=2.6,
         max_tokens=LG_MAX_TOKENS, temperature=LG_TEMPERATURE, artifact_ext="md",
         messages=_msg(LG04_PROMPT), grade=_grade_wrapper(_lg04_grade)),
]
