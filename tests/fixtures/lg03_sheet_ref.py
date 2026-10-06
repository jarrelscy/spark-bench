"""LG-03 grader oracle: reference spreadsheet engine written to the LG03_PROMPT spec.
Not model evidence. Used only by tests/test_long_gen_graders.py to prove the grader
gives a correct implementation >= 0.95 and plausible broken ones strictly less."""
import math
import re
from decimal import Decimal, ROUND_HALF_UP

NUM_RE = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
REF_RE = re.compile(r"([A-Za-z]{1,2})([0-9]+)")


class _Err:
    def __init__(self, code): self.code = code
    def __eq__(self, o): return isinstance(o, _Err) and o.code == self.code
    def __hash__(self): return hash(self.code)


DIV0, REF, CYC, VAL, NAME, PARSE = (_Err(c) for c in ("#DIV/0!", "#REF!", "#CYCLE!", "#VALUE!", "#NAME?", "#PARSE!"))


def _key(ref):
    m = REF_RE.fullmatch(ref.strip()) if isinstance(ref, str) else None
    if not m:
        raise ValueError(ref)
    col = 0
    for ch in m.group(1).upper():
        col = col * 26 + (ord(ch) - 64)
    row = int(m.group(2))
    if not 1 <= row <= 9999:
        raise ValueError(ref)
    return (row, col)


def _name(k):
    row, col = k
    s = ""
    while col:
        col, r = divmod(col - 1, 26)
        s = chr(65 + r) + s
    return f"{s}{row}"


def fmt(x):
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return repr(x)


def text(v):
    if v is None: return ""
    if isinstance(v, bool): return "TRUE" if v else "FALSE"
    if isinstance(v, float): return fmt(v)
    return str(v)


# ---------------------------------------------------------------- tokenizer/parser
TOK = re.compile(r'\s*(?:(?P<num>(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)|(?P<str>"(?:[^"]|"")*")|(?P<id>[A-Za-z_][A-Za-z0-9_]*)'
                 r'|(?P<op><=|>=|<>|[-+*/^&=<>(),:]))')


class _PErr(Exception): pass


def tokenize(s):
    out, i = [], 0
    while i < len(s):
        if s[i:].strip() == "": break
        m = TOK.match(s, i)
        if not m or m.end() == i: raise _PErr()
        if m.group("num"): out.append(("num", float(m.group("num"))))
        elif m.group("str"): out.append(("str", m.group("str")[1:-1].replace('""', '"')))
        elif m.group("id"): out.append(("id", m.group("id")))
        else: out.append(("op", m.group("op")))
        i = m.end()
    return out


REFLIKE = re.compile(r"[A-Za-z]+[0-9]+")


class Parser:
    def __init__(self, toks): self.t, self.i = toks, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else ("end", "")
    def take(self): tok = self.peek(); self.i += 1; return tok
    def isop(self, *ops): k, v = self.peek(); return k == "op" and v in ops
    def expect(self, op):
        if not self.isop(op): raise _PErr()
        self.i += 1
    def parse(self):
        n = self.comparison()
        if self.i != len(self.t): raise _PErr()
        return n
    def comparison(self):
        n = self.concat()
        while self.isop("=", "<>", "<", ">", "<=", ">="):
            n = ("cmp", self.take()[1], n, self.concat())
        return n
    def concat(self):
        n = self.additive()
        while self.isop("&"):
            self.take(); n = ("cat", n, self.additive())
        return n
    def additive(self):
        n = self.term()
        while self.isop("+", "-"):
            n = ("bin", self.take()[1], n, self.term())
        return n
    def term(self):
        n = self.unary()
        while self.isop("*", "/"):
            n = ("bin", self.take()[1], n, self.unary())
        return n
    def unary(self):
        if self.isop("-", "+"):
            return ("neg" if self.take()[1] == "-" else "pos", self.unary())
        return self.power()
    def power(self):
        n = self.primary()
        if self.isop("^"):
            self.take(); n = ("bin", "^", n, self.unary())
        return n
    def primary(self):
        k, v = self.take()
        if k in ("num", "str"): return ("lit", v)
        if k == "op" and v == "(":
            n = self.comparison(); self.expect(")"); return n
        if k == "id":
            if self.isop("("):
                self.take(); args = []
                if not self.isop(")"):
                    args.append(self.comparison())
                    while self.isop(","):
                        self.take(); args.append(self.comparison())
                self.expect(")")
                return ("fn", v.upper(), args)
            if v.upper() in ("TRUE", "FALSE"): return ("lit", v.upper() == "TRUE")
            if REFLIKE.fullmatch(v):
                a = self._ref(v)
                if self.isop(":"):
                    self.take(); k2, v2 = self.take()
                    if k2 != "id" or not REFLIKE.fullmatch(v2): raise _PErr()
                    return ("range", a, self._ref(v2))
                return ("ref", a)
            return ("name",)
        raise _PErr()
    @staticmethod
    def _ref(v):
        try: return _key(v)
        except ValueError: return None


def deps(node, out):
    t = node[0]
    if t == "ref" and node[1]: out.append((node[1], node[1]))
    elif t == "range" and node[1] and node[2]: out.append((node[1], node[2]))
    elif t in ("cmp", "bin"): deps(node[2], out); deps(node[3], out)
    elif t == "cat": deps(node[1], out); deps(node[2], out)
    elif t in ("neg", "pos"): deps(node[1], out)
    elif t == "fn":
        for a in node[2]: deps(a, out)
    return out


def _inrect(k, rect):
    (r1, c1), (r2, c2) = rect
    return min(r1, r2) <= k[0] <= max(r1, r2) and min(c1, c2) <= k[1] <= max(c1, c2)


def _cells(a, b):
    for r in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
        for c in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
            yield (r, c)


class Sheet:
    def __init__(self):
        self.raw = {}; self.undo_stack = []

    def set(self, ref, raw):
        k = _key(ref)
        if not isinstance(raw, str): raise TypeError("raw must be str")
        self.undo_stack.append((k, self.raw.get(k)))
        if raw == "": self.raw.pop(k, None)
        else: self.raw[k] = raw

    def get_raw(self, ref): return self.raw.get(_key(ref))

    def undo(self):
        if not self.undo_stack: return False
        k, prev = self.undo_stack.pop()
        if prev is None: self.raw.pop(k, None)
        else: self.raw[k] = prev
        return True

    # ---- analysis (rebuilt from raw on every query, so nothing can go stale)
    def _analyse(self):
        self._asts, self._rects = {}, {}
        for k, r in self.raw.items():
            if r.startswith("="):
                try: a = Parser(tokenize(r[1:])).parse()
                except _PErr: a = ("parse",)
                self._asts[k] = a
                self._rects[k] = deps(a, []) if a[0] != "parse" else []
        self._formula = set(self._asts)
        self._deps = {k: self._members(rs) for k, rs in self._rects.items()}
        self._cyc = self._tarjan()
        self._memo = {}

    def _members(self, rects):
        out = []
        for rect in rects:
            (r1, c1), (r2, c2) = rect
            area = (abs(r1 - r2) + 1) * (abs(c1 - c2) + 1)
            if area <= len(self._formula):
                out.extend(c for c in _cells(*rect) if c in self._formula)
            else:
                out.extend(f for f in self._formula if _inrect(f, rect))
        return out

    def _tarjan(self):
        index, low, on, stack, cyc, n = {}, {}, set(), [], set(), [0]
        for root in self._deps:
            if root in index: continue
            work = [(root, 0)]
            while work:
                v, i = work.pop()
                if i == 0:
                    index[v] = low[v] = n[0]; n[0] += 1; stack.append(v); on.add(v)
                ds = self._deps[v]
                if i < len(ds):
                    work.append((v, i + 1)); w = ds[i]
                    if w not in index: work.append((w, 0))
                    elif w in on: low[v] = min(low[v], index[w])
                    continue
                if low[v] == index[v]:
                    comp = []
                    while True:
                        w = stack.pop(); on.discard(w); comp.append(w)
                        if w == v: break
                    if len(comp) > 1 or v in ds: cyc.update(comp)
                if work:
                    p = work[-1][0]; low[p] = min(low[p], low[v])
        return cyc

    def get(self, ref):
        k = _key(ref)
        self._analyse()
        # evaluate dependencies bottom-up so evaluation never recurses deeply
        seen, order, work = set(), [], [(k, False)]
        while work:
            v, done = work.pop()
            if done: order.append(v); continue
            if v in seen or v not in self._formula or v in self._cyc: continue
            seen.add(v); work.append((v, True))
            work.extend((d, False) for d in self._deps[v])
        for v in order: self._cell(v)
        v = self._cell(k)
        return v.code if isinstance(v, _Err) else v

    def _cell(self, k):
        if k in self._memo: return self._memo[k]
        r = self.raw.get(k)
        if r is None: v = None
        elif r.startswith("="):
            if k in self._cyc: v = CYC
            else:
                a = self._asts[k]
                v = PARSE if a[0] == "parse" else self._ev(a)
                if v is None: v = 0.0
        elif NUM_RE.fullmatch(r.strip()): v = float(r.strip())
        else: v = r
        self._memo[k] = v
        return v

    # ---- evaluation
    @staticmethod
    def _num(v):
        if isinstance(v, _Err): return v
        if isinstance(v, bool): return 1.0 if v else 0.0
        if v is None: return 0.0
        if isinstance(v, float): return v
        return VAL

    def _ev(self, n):
        t = n[0]
        if t == "lit": return n[1]
        if t == "ref": return REF if n[1] is None else self._cell(n[1])
        if t == "range": return REF if (n[1] is None or n[2] is None) else VAL
        if t == "name": return NAME
        if t in ("neg", "pos"):
            v = self._num(self._ev(n[1]))
            if isinstance(v, _Err): return v
            return -v if t == "neg" else v
        if t == "bin":
            a = self._num(self._ev(n[2]))
            if isinstance(a, _Err): return a
            b = self._num(self._ev(n[3]))
            if isinstance(b, _Err): return b
            op = n[1]
            try:
                if op == "+": r = a + b
                elif op == "-": r = a - b
                elif op == "*": r = a * b
                elif op == "/":
                    if b == 0: return DIV0
                    r = a / b
                else:
                    if a == 0 and b < 0: return DIV0
                    r = a ** b
            except OverflowError:
                return VAL
            if isinstance(r, complex) or not math.isfinite(r): return VAL
            return float(r)
        if t == "cat":
            a = self._ev(n[1])
            if isinstance(a, _Err): return a
            b = self._ev(n[2])
            if isinstance(b, _Err): return b
            return text(a) + text(b)
        if t == "cmp":
            a = self._ev(n[2])
            if isinstance(a, _Err): return a
            b = self._ev(n[3])
            if isinstance(b, _Err): return b
            if isinstance(a, bool): a = 1.0 if a else 0.0
            if isinstance(b, bool): b = 1.0 if b else 0.0
            if a is None: a = "" if isinstance(b, str) else 0.0
            if b is None: b = "" if isinstance(a, str) else 0.0
            if type(a) is not type(b): return VAL
            if isinstance(a, str): a, b = a.lower(), b.lower()
            return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[n[1]]
        if t == "fn": return self._fn(n[1], n[2])
        return VAL

    def _range_cells(self, node):
        if node[0] == "ref":
            return REF if node[1] is None else [node[1]]
        if node[1] is None or node[2] is None: return REF
        return list(_cells(node[1], node[2]))

    def _fn(self, f, args):
        if f in ("SUM", "AVERAGE", "MIN", "MAX", "COUNT"):
            nums, cnt = [], f == "COUNT"
            for a in args:
                if a[0] in ("ref", "range"):
                    cells = self._range_cells(a)
                    if isinstance(cells, _Err):
                        if cnt: continue
                        return cells
                    for c in cells:
                        v = self._cell(c)
                        if isinstance(v, _Err):
                            if cnt: continue
                            return v
                        if isinstance(v, float): nums.append(v)
                else:
                    v = self._ev(a)
                    if isinstance(v, _Err):
                        if cnt: continue
                        return v
                    if isinstance(v, bool): nums.append(1.0 if v else 0.0)
                    elif isinstance(v, float): nums.append(v)
                    elif v is None: nums.append(0.0)
                    elif cnt: continue
                    else: return VAL
            if f == "SUM": return float(sum(nums))
            if f == "COUNT": return float(len(nums))
            if f == "AVERAGE": return DIV0 if not nums else float(sum(nums) / len(nums))
            if not nums: return 0.0
            return float(min(nums) if f == "MIN" else max(nums))
        if f == "IF":
            if len(args) not in (2, 3): return VAL
            if args[0][0] == "range": return VAL
            c = self._ev(args[0])
            if isinstance(c, _Err): return c
            if isinstance(c, str): return VAL
            if c:
                return VAL if args[1][0] == "range" else self._ev(args[1])
            if len(args) == 2: return False
            return VAL if args[2][0] == "range" else self._ev(args[2])
        if f == "CONCAT":
            out = ""
            for a in args:
                if a[0] in ("ref", "range"):
                    cells = self._range_cells(a)
                    if isinstance(cells, _Err): return cells
                    for c in cells:
                        v = self._cell(c)
                        if isinstance(v, _Err): return v
                        out += text(v)
                else:
                    v = self._ev(a)
                    if isinstance(v, _Err): return v
                    out += text(v)
            return out
        if f in ("LEN", "ABS"):
            if len(args) != 1 or args[0][0] == "range": return VAL
            v = self._ev(args[0])
            if isinstance(v, _Err): return v
            if f == "LEN": return float(len(text(v)))
            v = self._num(v)
            return v if isinstance(v, _Err) else abs(v)
        if f == "ROUND":
            if len(args) not in (1, 2) or any(a[0] == "range" for a in args): return VAL
            x = self._num(self._ev(args[0]))
            if isinstance(x, _Err): return x
            d = 0.0
            if len(args) == 2:
                d = self._num(self._ev(args[1]))
                if isinstance(d, _Err): return d
            q = Decimal(1).scaleb(-int(d))
            return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))
        return NAME

    # ---- graph queries / export
    def dependents(self, ref):
        k = _key(ref); self._analyse()
        small, big = {}, []
        for f, rects in self._rects.items():
            for rect in rects:
                (r1, c1), (r2, c2) = rect
                if (abs(r1 - r2) + 1) * (abs(c1 - c2) + 1) <= 4096:
                    for c in _cells(*rect): small.setdefault(c, set()).add(f)
                else:
                    big.append((rect, f))
        found, work = set(), [k]
        while work:
            x = work.pop()
            hits = set(small.get(x, ())) | {f for rect, f in big if _inrect(x, rect)}
            for f in hits:
                if f not in found:
                    found.add(f); work.append(f)
        found.discard(k)
        return [_name(x) for x in sorted(found)]

    def to_csv(self):
        if not self.raw: return ""
        mr = max(k[0] for k in self.raw); mc = max(k[1] for k in self.raw)
        self._analyse()
        lines = []
        for r in range(1, mr + 1):
            fields = []
            for c in range(1, mc + 1):
                if (r, c) in self.raw:
                    v = self.get(_name((r, c)))
                else:
                    v = None
                s = text(v)
                if any(ch in s for ch in ',"\n'): s = '"' + s.replace('"', '""') + '"'
                fields.append(s)
            lines.append(",".join(fields))
        return "\n".join(lines)
