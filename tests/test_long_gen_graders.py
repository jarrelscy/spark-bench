"""Grader self-test for long_gen: reference answers must score high, corrupted
answers must score 0/low. Run: python3 tests/test_long_gen_graders.py"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import long_gen as lg

def resp(text, finish="stop"):
    return {"text": text, "finish": finish}

# ---------------- LG-04 reference ----------------
LG04_REF = '''
from dataclasses import dataclass, field
@dataclass
class Order:
    id: str; items: list; total: float; state: str = "DRAFT"; payment_attempts: int = 0
    delivered_day: int | None = None; refunds: list = field(default_factory=list); history: list = field(default_factory=list)
CANCEL_TO_CANCELLED = {"DRAFT","SUBMITTED","PAYMENT_PENDING"}; CANCEL_TO_REFUNDED = {"PAID","PACKING"}
class OrderStateMachine:
    def apply(self, o, ev):
        n = ev["name"]; d = ev.get("day", 0); s = o.state; new = None
        if n == "submit" and s == "DRAFT" and o.items: new = "SUBMITTED"
        elif n == "request_payment" and s == "SUBMITTED": new = "PAYMENT_PENDING"
        elif n == "payment_ok" and s == "PAYMENT_PENDING" and abs(ev.get("amount", -1) - o.total) < 1e-9: new = "PAID"
        elif n == "payment_failed" and s == "PAYMENT_PENDING":
            o.payment_attempts += 1; new = "CANCELLED" if o.payment_attempts >= 3 else "SUBMITTED"
        elif n == "start_packing" and s == "PAID": new = "PACKING"
        elif n == "ship" and s == "PACKING" and ev.get("tracking_number"): new = "SHIPPED"
        elif n == "deliver" and s == "SHIPPED": new = "DELIVERED"; o.delivered_day = d
        elif n == "cancel":
            if s in CANCEL_TO_CANCELLED: new = "CANCELLED"
            elif s in CANCEL_TO_REFUNDED: new = "REFUNDED"; o.refunds.append(o.total)
        elif n == "request_return" and s == "DELIVERED" and o.delivered_day is not None and d - o.delivered_day <= 30: new = "RETURN_REQUESTED"
        elif n == "receive_return" and s == "RETURN_REQUESTED": new = "RETURNED"
        elif n == "refund" and s == "RETURNED": new = "REFUNDED"; o.refunds.append(o.total)
        if new is None:
            o.history.append((n, s, "REJECTED", d)); return False
        o.history.append((n, s, new, d)); o.state = new; return True
def run_trace(spec, events):
    o = Order(spec["id"], list(spec.get("items", [])), float(spec.get("total", 0.0))); m = OrderStateMachine(); a = r = 0
    for e in events:
        if m.apply(o, e): a += 1
        else: r += 1
    return {"final_state": o.state, "applied": a, "rejected": r, "refunded": float(sum(o.refunds)), "payment_attempts": o.payment_attempts}
if __name__ == "__main__":
    import json, sys; d = json.load(sys.stdin); print(json.dumps(run_trace(d["order"], d["events"])))
'''
sc, why = lg._lg04_legacy_grade(resp("Here you go:\n```python\n" + LG04_REF + "\n```\n"))
print(f"LG-04 reference   {sc:.2f}  {why}"); assert sc >= 0.95, why
sc, why = lg._lg04_legacy_grade(resp("```python\n" + LG04_REF[:1500], finish="length")); print(f"LG-04 truncated   {sc:.2f}  {why}"); assert sc == 0.0
bad = LG04_REF.replace('o.payment_attempts >= 3', 'o.payment_attempts >= 2').replace('d - o.delivered_day <= 30', 'd - o.delivered_day <= 10')
sc, why = lg._lg04_legacy_grade(resp("```python\n" + bad + "\n```")); print(f"LG-04 buggy       {sc:.2f}  {why}"); assert 0.5 < sc < 0.95

# ---------------- LG-02 reference ----------------
MODELS = '''
from dataclasses import dataclass, asdict
@dataclass
class Product:
    sku: str; name: str; unit_cost: float; reorder_point: int
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, d): return cls(**d)
@dataclass
class Location:
    code: str; capacity: int
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, d): return cls(**d)
@dataclass
class StockLevel:
    sku: str; location_code: str; quantity: int
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, d): return cls(**d)
@dataclass
class Movement:
    kind: str; sku: str; qty: int; src: str | None; dst: str | None; ts: int; ref: str
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, d): return cls(**d)
'''
STORAGE = '''
import json, os, tempfile
from models import Product, Location, StockLevel, Movement
class JsonStore:
    def __init__(self, path): self.path = path; self.data = {"products": [], "locations": [], "stock": [], "movements": []}
    def load(self):
        if os.path.exists(self.path):
            with open(self.path) as f: self.data = json.load(f)
        return self.data
    def save(self):
        d = os.path.dirname(self.path) or "."
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
        with os.fdopen(fd, "w") as f: json.dump(self.data, f)
        os.replace(tmp, self.path)
    def get_product(self, sku):
        for p in self.data["products"]:
            if p["sku"] == sku: return Product.from_dict(p)
        raise KeyError(sku)
    def get_location(self, code):
        for l in self.data["locations"]:
            if l["code"] == code: return Location.from_dict(l)
        raise KeyError(code)
    def stock_at(self, sku, code):
        for s in self.data["stock"]:
            if s["sku"] == sku and s["location_code"] == code: return s["quantity"]
        return 0
    def set_stock(self, sku, code, qty):
        for s in self.data["stock"]:
            if s["sku"] == sku and s["location_code"] == code: s["quantity"] = qty; return
        self.data["stock"].append(StockLevel(sku, code, qty).to_dict())
    def append_movement(self, m): self.data["movements"].append(m.to_dict())
'''
RULES = '''
import time
from models import Movement
from storage import JsonStore
class InsufficientStock(Exception): pass
class CapacityExceeded(Exception): pass
class DuplicateRef(Exception): pass
class Inventory:
    def __init__(self, store): self.store = store
    def _check(self, sku, qty, ref):
        if qty <= 0: raise ValueError("qty")
        self.store.get_product(sku)
        if any(m["ref"] == ref for m in self.store.data["movements"]): raise DuplicateRef(ref)
    def _loc_total(self, code): return sum(s["quantity"] for s in self.store.data["stock"] if s["location_code"] == code)
    def _cap(self, code, add):
        loc = self.store.get_location(code)
        if self._loc_total(code) + add > loc.capacity: raise CapacityExceeded(code)
    def _commit(self, kind, sku, qty, src, dst, ref):
        self.store.append_movement(Movement(kind, sku, qty, src, dst, len(self.store.data["movements"]) + 1, ref)); self.store.save()
    def receive(self, sku, qty, dst, ref):
        self._check(sku, qty, ref); self._cap(dst, qty)
        self.store.set_stock(sku, dst, self.store.stock_at(sku, dst) + qty); self._commit("receive", sku, qty, None, dst, ref)
    def ship(self, sku, qty, src, ref):
        self._check(sku, qty, ref); self.store.get_location(src)
        if self.store.stock_at(sku, src) < qty: raise InsufficientStock(sku)
        self.store.set_stock(sku, src, self.store.stock_at(sku, src) - qty); self._commit("ship", sku, qty, src, None, ref)
    def transfer(self, sku, qty, src, dst, ref):
        self._check(sku, qty, ref); self.store.get_location(src)
        if src == dst: raise ValueError("same location")
        if self.store.stock_at(sku, src) < qty: raise InsufficientStock(sku)
        self._cap(dst, qty)
        self.store.set_stock(sku, src, self.store.stock_at(sku, src) - qty); self.store.set_stock(sku, dst, self.store.stock_at(sku, dst) + qty)
        self._commit("transfer", sku, qty, src, dst, ref)
    def adjust(self, sku, qty_delta, loc, ref):
        if qty_delta == 0: raise ValueError("qty")
        self.store.get_product(sku); self.store.get_location(loc)
        if any(m["ref"] == ref for m in self.store.data["movements"]): raise DuplicateRef(ref)
        cur = self.store.stock_at(sku, loc)
        if cur + qty_delta < 0: raise InsufficientStock(sku)
        if qty_delta > 0: self._cap(loc, qty_delta)
        self.store.set_stock(sku, loc, cur + qty_delta); self._commit("adjust", sku, qty_delta, loc if qty_delta < 0 else None, loc if qty_delta > 0 else None, ref)
    def total_on_hand(self, sku): return sum(s["quantity"] for s in self.store.data["stock"] if s["sku"] == sku)
    def below_reorder(self): return [p["sku"] for p in self.store.data["products"] if self.total_on_hand(p["sku"]) < p["reorder_point"]]
    def valuation(self): return float(sum(s["quantity"] * self.store.get_product(s["sku"]).unit_cost for s in self.store.data["stock"]))
    def ledger(self, sku): return sorted([Movement.from_dict(m) for m in self.store.data["movements"] if m["sku"] == sku], key=lambda m: m.ts)
'''
CLI = '''
import argparse, json
from storage import JsonStore
from rules import Inventory
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--db", required=True); sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("receive", "ship"):
        p = sub.add_parser(c); p.add_argument("sku"); p.add_argument("qty", type=int); p.add_argument("loc"); p.add_argument("ref")
    p = sub.add_parser("transfer"); p.add_argument("sku"); p.add_argument("qty", type=int); p.add_argument("src"); p.add_argument("dst"); p.add_argument("ref")
    p = sub.add_parser("adjust"); p.add_argument("sku"); p.add_argument("delta", type=int); p.add_argument("loc"); p.add_argument("ref")
    sub.add_parser("report")
    a = ap.parse_args(); st = JsonStore(a.db); st.load(); inv = Inventory(st)
    if a.cmd == "receive": inv.receive(a.sku, a.qty, a.loc, a.ref); out = {"ok": True}
    elif a.cmd == "ship": inv.ship(a.sku, a.qty, a.loc, a.ref); out = {"ok": True}
    elif a.cmd == "transfer": inv.transfer(a.sku, a.qty, a.src, a.dst, a.ref); out = {"ok": True}
    elif a.cmd == "adjust": inv.adjust(a.sku, a.delta, a.loc, a.ref); out = {"ok": True}
    else: out = {"valuation": inv.valuation(), "below_reorder": inv.below_reorder(), "total_units": sum(s["quantity"] for s in st.data["stock"])}
    print(json.dumps(out))
if __name__ == "__main__": main()
'''
TESTS = '''
import unittest
class T(unittest.TestCase):
    def test_placeholder(self): self.assertTrue(True)
''' + "\n" * 5 + "# " + "x" * 400
def files_text(**kw):
    return "".join(f"### {n}\n```python\n{b}\n```\n" for n, b in kw.items())
good = files_text(**{"models.py": MODELS, "storage.py": STORAGE, "rules.py": RULES, "cli.py": CLI, "tests.py": TESTS})
sc, why = lg._lg02_grade(resp(good)); print(f"LG-02 reference   {sc:.2f}  {why}"); assert sc >= 0.9, why
sc, why = lg._lg02_grade(resp(good, finish="length")); print(f"LG-02 truncated   {sc:.2f}  {why}"); assert sc == 0.0
sc, why = lg._lg02_grade(resp(files_text(**{"models.py": MODELS, "storage.py": STORAGE, "rules.py": RULES}))); print(f"LG-02 missing     {sc:.2f}  {why}"); assert sc == 0.0
badr = RULES.replace("if self._loc_total(code) + add > loc.capacity: raise CapacityExceeded(code)", "pass").replace("raise DuplicateRef(ref)", "pass")
sc, why = lg._lg02_grade(resp(files_text(**{"models.py": MODELS, "storage.py": STORAGE, "rules.py": badr, "cli.py": CLI, "tests.py": TESTS}))); print(f"LG-02 buggy       {sc:.2f}  {why}"); assert 0.5 < sc < 0.9

# ---------------- LG-03 reference ----------------
def body(k):
    base = (f"This section ({k}) of the scheduled webhook delivery service covers tenant-scoped behaviour. "
            "Each tenant registers endpoints with a signing secret; the scheduler enqueues deliveries; the worker "
            "signs the payload (HMAC-SHA256 signature header), POSTs it, and on failure applies exponential retry "
            "with jitter before dead-lettering after the retry budget. ") * 4
    if k == "api":
        base += "\n".join(f"{m} /v1/{p} — {d}" for m, p, d in [("POST","endpoints","register endpoint"),("GET","endpoints","list"),("DELETE","endpoints/{id}","remove"),("POST","schedules","create schedule"),("GET","schedules/{id}","get"),("PATCH","schedules/{id}","update"),("GET","deliveries","list deliveries"),("POST","deliveries/{id}/replay","replay dead-lettered"),("GET","tenants/{id}/usage","usage")])
    if k == "data_model":
        base += "\n".join(f"- {e}: id, tenant_id, created_at, {f}" for e, f in [("tenants","name"),("endpoints","url, secret"),("schedules","cron, endpoint_id"),("deliveries","status, attempt"),("attempts","code, latency_ms"),("dead_letters","reason, payload_ref"),("secrets","version, rotated_at")])
    if k == "failure_modes":
        base += "\n".join(f"{i}. Failure {i}: endpoint timeout variant {i}. Mitigation: retry with backoff and dead-letter after budget." for i in range(1, 10))
    return base
obj = {k: {"title": k.title(), "body": body(k), "refs": [r for r in lg.LG03_SECTIONS if r != k][:2]} for k in lg.LG03_SECTIONS}
sc, why = lg._lg03_legacy_grade(resp(json.dumps(obj))); print(f"LG-03 reference   {sc:.2f}  {why}"); assert sc >= 0.9, why
sc, why = lg._lg03_legacy_grade(resp(json.dumps(obj)[:5000], finish="length")); print(f"LG-03 truncated   {sc:.2f}  {why}"); assert sc == 0.0
stub = {k: {"title": k, "body": "TBD", "refs": []} for k in lg.LG03_SECTIONS}
sc, why = lg._lg03_legacy_grade(resp(json.dumps(stub))); print(f"LG-03 stubs       {sc:.2f}  {why}"); assert sc < 0.3

# ---------------- LG-01 reference (render) ----------------
LG01_REF = r'''<!DOCTYPE html><html><body style="margin:0"><script type="module">
import * as THREE from './three.module.js';
const W=64, scene=new THREE.Scene(); let night=false;
const cam=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,0.1,1000); const ren=new THREE.WebGLRenderer({antialias:true}); ren.setSize(innerWidth,innerHeight); document.body.appendChild(ren.domElement);
const sun=new THREE.DirectionalLight(0xffffff,1.2); sun.position.set(30,60,20); scene.add(sun); const amb=new THREE.AmbientLight(0xffffff,0.6); scene.add(amb);
function h(x,z){return Math.floor(3+2.5*Math.sin(x*0.18)+2.5*Math.cos(z*0.15)+1.5*Math.sin((x+z)*0.09));}
const box=new THREE.BoxGeometry(1,1,1); const cols={grass:0x4caf50,dirt:0x8d6e63,water:0x2196f3,sand:0xf1e3a1,stone:0x9e9e9e,wood:0xa0522d,roofA:0xb71c1c,roofB:0x37474f,roofC:0xff8f00,leaf:0x2e7d32};
const mats={}; for(const k in cols) mats[k]=new THREE.MeshLambertMaterial({color:cols[k]});
const counts={}; const inst={}; const lists={};
function add(k,x,y,z){(lists[k]=lists[k]||[]).push([x,y,z]);}
const riverZ=x=>Math.floor(W/2+8*Math.sin(x*0.12));
for(let x=0;x<W;x++)for(let z=0;z<W;z++){const hh=h(x,z); const rz=riverZ(x); const isRiver=Math.abs(z-rz)<=1;
  for(let y=0;y<hh;y++) add(y<hh-1?'dirt':(isRiver?'water':(Math.abs(z-rz)<=2?'sand':'grass')),x,y,z); if(isRiver) add('water',x,hh-1,z);}
const rnd=(s=>()=> (s=(s*16807)%2147483647)/2147483647)(7); let trees=0; while(trees<24){const x=Math.floor(rnd()*W),z=Math.floor(rnd()*W); if(Math.abs(z-riverZ(x))<4) continue; const y=h(x,z); for(let i=0;i<3;i++)add('wood',x,y+i,z); for(let dx=-1;dx<=1;dx++)for(let dz=-1;dz<=1;dz++)for(let dy=3;dy<=4;dy++)add('leaf',x+dx,y+dy,z+dz); trees++;}
const bl=[]; for(let i=0;i<12;i++){const x=10+Math.floor((i%4)*12), z=(i<4?8:(i<8?20:44)); const y=h(x,z); const t=i%3; const w=3+t, d=3+(t===1?2:0), ht=3+t; bl.push([x,z]);
  for(let dx=0;dx<w;dx++)for(let dz=0;dz<d;dz++)for(let dy=0;dy<ht;dy++) add('wood',x+dx,y+dy,z+dz);
  for(let dx=-1;dx<=w;dx++)for(let dz=-1;dz<=d;dz++) add(t===0?'roofA':(t===1?'roofB':'roofC'),x+dx,y+ht,z+dz); if(t===2) for(let dx=0;dx<w;dx++) add('roofC',x+dx,y+ht+1,z+1);}
for(let i=0;i<bl.length-1;i++){const [x0,z0]=bl[i],[x1,z1]=bl[i+1]; const n=Math.max(Math.abs(x1-x0),Math.abs(z1-z0)); for(let s=0;s<=n;s++){const x=Math.round(x0+(x1-x0)*s/n), z=Math.round(z0+(z1-z0)*s/n); add('stone',x,h(x,z),z);}}
const winMat=new THREE.MeshBasicMaterial({color:0x000000}); const wins=[]; for(const [x,z] of bl){const y=h(x,z)+1; const m=new THREE.Mesh(new THREE.BoxGeometry(0.3,1,1),winMat); m.position.set(x-0.2,y,z+1); scene.add(m); wins.push(m);}
for(const k in lists){const im=new THREE.InstancedMesh(box,mats[k],lists[k].length); const o=new THREE.Object3D(); lists[k].forEach(([x,y,z],i)=>{o.position.set(x-W/2,y,z-W/2); o.updateMatrix(); im.setMatrixAt(i,o.matrix);}); scene.add(im);}
function setNight(n){night=n; scene.background=new THREE.Color(n?0x0b1026:0x87ceeb); sun.intensity=n?0.15:1.2; amb.intensity=n?0.15:0.6; winMat.color.set(n?0xffd54f:0x000000);}
setNight(false); addEventListener('keydown',e=>{if(e.key==='n'||e.key==='N') setNight(!night);});
let a=0; function loop(){a+=0.006; cam.position.set(Math.sin(a)*70,45,Math.cos(a)*70); cam.lookAt(0,5,0); ren.render(scene,cam); requestAnimationFrame(loop);} loop();
</script></body></html>'''
sc, why = lg._lg01_grade(resp("```html\n" + LG01_REF + "\n```")); print(f"LG-01 reference   {sc:.2f}  {why}"); assert sc >= 0.8, why
sc, why = lg._lg01_grade(resp("```html\n" + LG01_REF[:3000], finish="length")); print(f"LG-01 truncated   {sc:.2f}  {why}"); assert sc == 0.0
sc, why = lg._lg01_grade(resp("```html\n<html><body><script type='module'>import * as THREE from './three.module.js'; const s=new THREE.Scene();</script></body></html>\n```")); print(f"LG-01 empty scene {sc:.2f}  {why}"); assert sc < 0.4
print("\nALL LONG_GEN GRADER SELF-TESTS PASSED")

