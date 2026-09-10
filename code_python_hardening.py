"""Executable edge-case contracts for six refreshed coding scenarios.

The prompts define every tested requirement. Fixtures are grader-side only.
No model generation, network calls or wall-clock sleeps occur here.
"""
import math
import random
import threading
import time

PROMPTS = {
 'CODE-06': '''Implement Python KVCache(capacity, ttl_seconds, clock=None), preserving get(key), put(key,value), delete(key)->bool. clock is an injectable zero-argument seconds clock, default time.monotonic. Capacity must be a non-bool integer >=0; TTL must be a finite non-bool int/float >=0; invalid constructor arguments raise ValueError. TTL starts/resets on put, not get; an item expires exactly when now >= expiry. Before evicting a live LRU entry, remove ALL expired entries, including entries recently accessed. Successful get and put mark an entry most recently used. Missing/expired get returns None and delete returns False; deleting a live entry returns True. Updating a key must not evict another live entry. Capacity zero and TTL zero store nothing. Support falsy keys and values, independent instances, and do not sleep. Output only Python code.''',
 'CODE-07': '''Implement extract_leaves(value, with_paths=False) for nested Python JSON-like dict/list/scalar structures. Return scalars in depth-first order, dict insertion order and list index order; preserve duplicates and scalar types (str,int,float,bool,None). Empty containers contribute no leaves. With with_paths=True return (JSON_pointer, scalar) tuples; root scalar has path "", list indices are decimal, dict keys escape ~ as ~0 and / as ~1. Dict keys must be strings. Unsupported objects or non-string dict keys raise TypeError. Cycles on the CURRENT ancestor path raise ValueError; a shared but acyclic child must be traversed each time it appears, not deduplicated. Support nesting depth at least 2500 without changing the interpreter recursion limit. Never mutate the input. Output only Python code.''',
 'CODE-09': '''Implement retry_with_backoff(func, max_retries=3, initial_delay=0.1, backoff_factor=2, *, retry_on=(Exception,), max_delay=None, sleep=None). max_retries means ADDITIONAL calls after the first: 0 still calls once. Retry only exceptions matching retry_on; never retry BaseException subclasses outside Exception (e.g. KeyboardInterrupt). Re-raise the exact last exception object on exhaustion and immediately propagate non-retryable exceptions. After retryable failure number i (zero-based), sleep min(initial_delay * backoff_factor**i, max_delay) if a cap is supplied, otherwise the uncapped delay. No sleep after success, a non-retryable exception or the final failed attempt. sleep defaults to time.sleep and is injectable. Return successful values unchanged, including None/False. Validate BEFORE calling func: max_retries a non-bool integer >=0; initial_delay finite non-bool number >=0; backoff_factor finite non-bool number >=1; max_delay None or finite non-bool number >=0; retry_on a nonempty tuple of Exception subclass types. Invalid values raise ValueError. Do not use jitter. Output only Python code.''',
 'CODE-10': '''Implement StateMachine(transitions, initial_state, *, guards=None, actions=None). transitions maps (state,event) to next_state; guards/actions optionally map the same keys to callbacks. Copy these mappings so later caller mutations do not alter the machine. current() returns state. can_trigger(event) reports ONLY whether the transition exists, without invoking callbacks. trigger(event, **payload) first rejects missing transitions with ValueError. A guard, if present, is called as guard(old_state,event,payload_dict); false raises ValueError. Then an action, if present, is called as action(old_state,new_state,event,payload_dict). Only after both succeed commit new_state and return it. Callback exceptions propagate without changing state; falsy states/targets are valid. During a callback, a nested trigger on the SAME instance must raise RuntimeError without changing state; current and can_trigger remain usable. After rejection or exception the machine must still work normally. Instances are independent. Output only Python code.''',
 'CODE-11': '''Refactor the legacy functions below to use _apply_discount(price, discount_type, value), with discount_type "percentage", "fixed", or "bogo". Preserve EXACT legacy results and exceptions for finite int/float inputs (including negative discounts, percentages above100, fractional quantities and Python round behavior). Unknown discount_type raises ValueError. Each public wrapper must dynamically call the shared helper, not copy the calculations. Add chained_discounts(price, steps), where steps is any iterable of (discount_type,value): apply the helper in order, rounding at EACH step as the legacy functions do; an empty chain returns price unchanged after the same negative-price validation. Do not mutate inputs. Output only Python code.

def percentage_discount(price, percent):
    if price < 0: raise ValueError('negative price')
    return round(price * (1 - percent / 100), 2)
def fixed_discount(price, amount):
    if price < 0: raise ValueError('negative price')
    result = price - amount
    return round(max(result, 0), 2)
def bogo_discount(price, quantity):
    if price < 0: raise ValueError('negative price')
    if quantity < 1: return 0
    paid = (quantity // 2 + quantity % 2) * price
    return round(paid, 2)''',
 'CODE-12': '''Fix and extend a thread-safe Python SafeCounter, initially zero. Use exactly one per-instance threading.Lock created in __init__, no global locks and no reliance on the GIL. Protect increment(n=1), decrement(n=1), and value() with `with self.<lock_attribute>:` using the same lock. increment/decrement accept signed integers and return None; value returns the integer. Add compare_and_set(expected,new)->bool: atomically replace only if the current value equals expected. Add transfer_to(other,n)->None: atomically subtract n from self and add n to other, locking both instances in a deterministic global order to prevent opposite-direction deadlock; negative balances are allowed. n must be a non-bool integer >=0, otherwise raise ValueError before changing either counter. A transfer to self is a validated no-op. Other method numeric arguments are integers. No lock may remain held after an exception; different instances must have different locks. Output only Python code.'''
}

def _assert(condition, detail='wrong result'):
    if not condition:
        raise AssertionError(detail)


def _raises(kind, fn):
    try:
        fn()
    except kind as exc:
        return exc
    raise AssertionError('expected ' + kind.__name__)


def _score(cases):
    passed = 0
    reasons = []
    for name, fn in cases:
        try:
            fn()
            passed += 1
            reasons.append(name + ':pass')
        except Exception as exc:
            reasons.append(name + ':fail(' + type(exc).__name__ + ')')
    return passed / len(cases), f'{passed}/{len(cases)} behavioral groups: ' + ', '.join(reasons)


class _Clock:
    def __init__(self):
        self.now = 0.0
    def __call__(self):
        return self.now


def test_cache(ns):
    C = ns.get('KVCache')
    def expiry():
        t = _Clock(); c = C(2, 10, clock=t)
        c.put('a', 1); t.now = 9; _assert(c.get('a') == 1)
        t.now = 10; _assert(c.get('a') is None); _assert(c.delete('a') is False)
    def purge_before_evict():
        t = _Clock(); c = C(2, 10, clock=t)
        c.put('old', 1); t.now = 5; c.put('live', 2); t.now = 9; c.get('old')
        t.now = 10; c.put('new', 3)
        _assert(c.get('live') == 2 and c.get('new') == 3 and c.get('old') is None)
    def update_lru():
        t = _Clock(); c = C(2, 10, clock=t)
        c.put('a', 1); c.put('b', 2); t.now = 5; c.put('a', 3)
        _assert(c.get('b') == 2); c.get('a'); c.put('c', 4)
        _assert(c.get('b') is None and c.get('a') == 3)
        t.now = 11; _assert(c.get('a') == 3); t.now = 15; _assert(c.get('a') is None)
        c = C(2, 10, clock=t)
        c.put('a', 1); c.put('b', 2); c.get('a'); c.put('c', 3)
        _assert(c.get('a') == 1 and c.get('b') is None and c.get('c') == 3)
    def edge():
        t = _Clock()
        for cap, ttl in [(0, 5), (2, 0)]:
            c = C(cap, ttl, clock=t); c.put(0, False)
            _assert(c.get(0) is None and c.delete(0) is False)
        c = C(2, 9, clock=t); c.put('', False); c.put(None, 0)
        _assert(c.get('') is False and c.get(None) == 0)
        _assert(c.delete('') is True and c.delete('') is False)
        _assert(C(2, 9, clock=t).get(None) is None)
        for cap in [-1, 1.5, True]: _raises(ValueError, lambda: C(cap, 1))
        for ttl in [-1, float('nan'), float('inf'), True]: _raises(ValueError, lambda: C(1, ttl))
    def model_trace():
        rng = random.Random(604); t = _Clock(); c = C(3, 4, clock=t); model = {}
        for _ in range(100):
            t.now += rng.choice([0, 0.5, 2]); key = rng.randrange(5); op = rng.randrange(3)
            model = {k:v for k,v in model.items() if t.now < v[1]}
            if op == 0:
                value = rng.randrange(50); c.put(key, value); model.pop(key, None)
                while len(model) >= 3: model.pop(next(iter(model)))
                model[key] = (value, t.now + 4)
            elif op == 1:
                expected = model.pop(key, None)
                _assert(c.get(key) == (expected[0] if expected else None), 'trace get')
                if expected: model[key] = expected
            else:
                _assert(c.delete(key) == (model.pop(key, None) is not None), 'trace delete')
    return _score([('expiry-boundary', expiry), ('purge-before-LRU', purge_before_evict),
                   ('update-recency-TTL', update_lru), ('validation-falsy', edge), ('mixed-trace', model_trace)])


def test_leaves(ns):
    f = ns.get('extract_leaves')
    def order_types():
        value = {'z': [False, 0, None, '', 2.5], 'a': {'x': 'ok'}, 'empty': {}}
        got = f(value); want = [False, 0, None, '', 2.5, 'ok']
        _assert(got == want and list(map(type, got)) == list(map(type, want)))
        _assert(value == {'z': [False, 0, None, '', 2.5], 'a': {'x': 'ok'}, 'empty': {}})
    def pointers():
        _assert(f({'a/b': {'~k': [7, {}, 8]}, '': 9}, with_paths=True) ==
                [('/a~1b/~0k/0', 7), ('/a~1b/~0k/2', 8), ('/', 9)])
        _assert(f(None, with_paths=True) == [('', None)])
        _assert(f([], with_paths=True) == [])
    def deep():
        import sys
        limit = sys.getrecursionlimit()
        value = 17
        for _ in range(2600): value = [value]
        try:
            _assert(f(value) == [17])
            _assert(sys.getrecursionlimit() == limit, 'changed recursion limit')
        finally:
            sys.setrecursionlimit(limit)
    def aliases_cycles():
        shared = {'x': [1, 2]}
        _assert(f([shared, shared]) == [1, 2, 1, 2])
        cycle = []; cycle.append(cycle); _raises(ValueError, lambda: f(cycle))
        a = {}; b = [a]; a['b'] = b; _raises(ValueError, lambda: f(a))
    def invalid():
        _raises(TypeError, lambda: f({'x': object()}))
        _raises(TypeError, lambda: f({2: 'x'}))
        _raises(TypeError, lambda: f((1, 2)))
    return _score([('ordered-typed-leaves', order_types), ('escaped-pointers', pointers),
                   ('deep-without-recursion', deep), ('aliases-vs-cycles', aliases_cycles), ('invalid-input', invalid)])


def test_retry(ns):
    f = ns.get('retry_with_backoff')
    def attempt_delays():
        seen = []; delays = []; err = RuntimeError('original')
        def fail(): seen.append(1); raise err
        got = _raises(RuntimeError, lambda: f(fail, 4, 0.25, 3, max_delay=1, sleep=delays.append))
        _assert(got is err and len(seen) == 5 and delays == [0.25, 0.75, 1, 1])
    def zero_and_success():
        for value in [False, None, 0, 'ok']:
            seen = []; delays = []
            def call(): seen.append(1); return value
            _assert(f(call, 0, sleep=delays.append) is value)
            _assert(len(seen) == 1 and not delays)
        seen = []; delays = []
        def eventually():
            seen.append(1)
            if len(seen) < 3: raise LookupError('retry')
            return 42
        _assert(f(eventually, 3, 0.5, 2, retry_on=(LookupError,), sleep=delays.append) == 42)
        _assert(delays == [0.5, 1])
    def exception_filter():
        for error in [ValueError('fatal'), KeyboardInterrupt('cancel')]:
            seen = []; delays = []
            def call(): seen.append(1); raise error
            got = _raises(type(error), lambda: f(call, retry_on=(RuntimeError,), sleep=delays.append))
            _assert(got is error and len(seen) == 1 and not delays)
    def validation():
        bad = [{'max_retries': v} for v in [-1, 1.5, True]]
        bad += [{'initial_delay': v} for v in [-1, float('nan'), True]]
        bad += [{'backoff_factor': v} for v in [0.5, float('inf')]]
        bad += [{'max_delay': v} for v in [-1, float('nan')]]
        bad += [{'retry_on': v} for v in [(), [Exception], (BaseException,), (1,)]]
        calls = []
        for kw in bad: _raises(ValueError, lambda: f(lambda: calls.append(1), sleep=lambda _: None, **kw))
        _assert(not calls)
    return _score([('attempt-count-and-capped-delays', attempt_delays), ('success-and-zero-retries', zero_and_success),
                   ('exception-identity-filter-cancel', exception_filter), ('validate-before-side-effects', validation)])


def test_machine(ns):
    C = ns.get('StateMachine')
    def basic_snapshot():
        table = {('idle','go'): 0, (0,'next'): False}; m = C(table,'idle'); table[('idle','go')] = 'bad'
        _assert(m.trigger('go') == 0 and m.current() == 0)
        _assert(m.trigger('next') is False)
        _raises(ValueError, lambda: m.trigger('unknown')); _assert(m.current() is False)
        _assert(C({('idle','go'): 1}, 'idle').current() == 'idle')
    def callbacks():
        calls = []
        def guard(s,e,p): calls.append(('g',s,e,p.copy())); return p['allow']
        def action(s,n,e,p): calls.append(('a',s,n,e,p.copy()))
        guards = {('a','go'): guard}; actions = {('a','go'): action}
        m = C({('a','go'): 'b'}, 'a', guards=guards, actions=actions)
        guards.clear(); actions.clear()
        _assert(m.can_trigger('go') is True and not calls)
        _raises(ValueError, lambda: m.trigger('go', allow=False)); _assert(m.current() == 'a')
        _assert(len(calls) == 1); calls.clear(); _assert(m.trigger('go', allow=True, x=9) == 'b')
        _assert(calls == [('g','a','go',{'allow':True,'x':9}), ('a','a','b','go',{'allow':True,'x':9})])
    def rollback_reentrant():
        err = LookupError('action failed'); count = []
        def action(s,n,e,p):
            _assert(m.current() == 'a' and m.can_trigger('go'))
            count.append(1)
            if len(count) == 1: raise err
            _raises(RuntimeError, lambda: m.trigger('go'))
        m = C({('a','go'): 'b'}, 'a', actions={('a','go'): action})
        _assert(_raises(LookupError, lambda: m.trigger('go')) is err)
        _assert(m.current() == 'a'); _assert(m.trigger('go') == 'b')
    def guard_exception():
        err = RuntimeError('guard'); calls = []
        def guard(*a):
            calls.append(1)
            if len(calls) == 1: raise err
            return True
        m = C({('a','go'): 'b'}, 'a', guards={('a','go'): guard})
        _assert(_raises(RuntimeError, lambda: m.trigger('go')) is err)
        _assert(m.current() == 'a' and m.trigger('go') == 'b')
    return _score([('snapshot-and-falsy-states', basic_snapshot), ('callback-order-purity', callbacks),
                   ('rollback-and-reentrant-trigger', rollback_reentrant), ('guard-exception-recovery', guard_exception)])


def _legacy(price, kind, value):
    if price < 0: raise ValueError('negative price')
    if kind == 'percentage': return round(price * (1 - value / 100), 2)
    if kind == 'fixed': return round(max(price - value, 0), 2)
    if kind == 'bogo': return 0 if value < 1 else round((value // 2 + value % 2) * price, 2)
    raise ValueError('unknown discount')


def test_discounts(ns):
    names = {'percentage': 'percentage_discount', 'fixed': 'fixed_discount', 'bogo': 'bogo_discount'}
    def legacy_matrix():
        rng = random.Random(1106)
        prices = [0, 2.675, 19.99, 100] + [rng.uniform(0, 500) for _ in range(15)]
        for kind, name in names.items():
            for price in prices:
                for value in [-20, 0, 0.5, 1, 2.5, 3, 100, 150]:
                    _assert(ns[name](price, value) == _legacy(price, kind, value), kind)
            _assert(str(_raises(ValueError, lambda: ns[name](-1, 0))) == 'negative price')
    def helper_validation():
        h = ns['_apply_discount']
        for kind in names: _assert(h(19.99, kind, 3) == _legacy(19.99, kind, 3))
        _raises(ValueError, lambda: h(10, 'unknown', 2))
    def delegate():
        calls = []; original = ns['_apply_discount']; marker = object()
        def spy(*args): calls.append(args); return marker
        ns['_apply_discount'] = spy
        try:
            for kind, name in names.items():
                _assert(ns[name](15, 7) is marker)
                _assert(calls[-1] == (15, kind, 7))
        finally: ns['_apply_discount'] = original
    def chains():
        f = ns['chained_discounts']; steps = [('percentage', 12.5), ('fixed', 1.01), ('bogo', 3)]
        expected = 19.99
        for kind, v in steps: expected = _legacy(expected, kind, v)
        _assert(f(19.99, iter(steps)) == expected and len(steps) == 3)
        _assert(f(2.675, []) == 2.675); _raises(ValueError, lambda: f(-1, []))
        _raises(ValueError, lambda: f(5, [('unknown', 2)]))
        _raises(ValueError, lambda: f(5, [('percentage', 150), ('fixed', 1)]))
        calls = []; original = ns['_apply_discount']
        def spy(p,k,v): calls.append((p,k,v)); return p+1
        ns['_apply_discount'] = spy
        try: _assert(f(10, [('fixed',2), ('percentage',3)]) == 12 and calls == [(10,'fixed',2),(11,'percentage',3)])
        finally: ns['_apply_discount'] = original
    return _score([('legacy-edge-and-random-matrix', legacy_matrix), ('helper-validation', helper_validation),
                   ('real-helper-delegation', delegate), ('ordered-chains-and-rounding', chains)])


def test_counter(ns):
    C = ns.get('SafeCounter')
    def api():
        a=C(); b=C(); _assert(a.value()==0)
        _assert(a.increment(9) is None and a.decrement(2) is None and a.value()==7)
        _assert(a.compare_and_set(8,1) is False and a.value()==7)
        _assert(a.compare_and_set(7,-2) is True and a.value()==-2)
        _assert(a.transfer_to(b,3) is None and a.value()==-5 and b.value()==3)
        a.transfer_to(a,10); _assert(a.value()==-5)
    def validation():
        a=C(); b=C(); a.increment(5)
        for n in [-1, 1.5, True]:
            _raises(ValueError, lambda: a.transfer_to(b,n))
            _raises(ValueError, lambda: a.transfer_to(a,n))
        _assert(a.value()==5 and b.value()==0); a.transfer_to(b,2)
        _assert(a.value()==3 and b.value()==2)
    def concurrent():
        a=C(); b=C(); a.increment(100); b.increment(100); errors=[]
        barrier=threading.Barrier(4)
        def worker(x,y):
            try:
                barrier.wait(timeout=1)
                for _ in range(120): x.transfer_to(y,1)
            except BaseException as exc: errors.append(repr(exc))
        workers=[threading.Thread(target=worker,args=(a,b),daemon=True) for _ in range(2)]
        workers += [threading.Thread(target=worker,args=(b,a),daemon=True) for _ in range(2)]
        for t in workers: t.start()
        deadline=time.monotonic()+1.5
        for t in workers: t.join(max(0,deadline-time.monotonic()))
        _assert(not errors and all(not t.is_alive() for t in workers),'transfer error/deadlock')
        _assert(a.value()==100 and b.value()==100)
    def cas_contended():
        c=C(); errors=[]; barrier=threading.Barrier(4)
        def worker():
            try:
                barrier.wait(timeout=1)
                for _ in range(80):
                    for attempt in range(10000):
                        old=c.value()
                        if c.compare_and_set(old,old+1): break
                    else: raise AssertionError('CAS no progress')
            except BaseException as exc: errors.append(repr(exc))
        workers=[threading.Thread(target=worker,daemon=True) for _ in range(4)]
        for t in workers: t.start()
        deadline=time.monotonic()+1.5
        for t in workers: t.join(max(0,deadline-time.monotonic()))
        _assert(not errors and all(not t.is_alive() for t in workers),'CAS error/deadlock')
        _assert(c.value()==320)
    def lock_scope():
        # Instrument the declared instance locks: do not depend on the GIL
        # happening to schedule threads between a read and write.
        a=C(); b=C(); native_type=type(threading.Lock()); events=[]; held=set()
        locks=[]
        for obj in (a,b):
            attrs=[k for k in dir(obj) if isinstance(getattr(obj,k),native_type)]
            _assert(len(attrs)==1, 'exactly one instance lock')
            locks.append(getattr(obj,attrs[0]))
            owner=id(obj); native=getattr(obj,attrs[0])
            class TracedLock:
                def __init__(self, native, owner): self.native=native; self.owner=owner
                def acquire(self,*args,**kw):
                    ok=self.native.acquire(*args,**kw)
                    if ok:
                        held.add(self.owner); events.append(('acquire',self.owner,len(held)))
                    return ok
                def release(self):
                    held.remove(self.owner); self.native.release()
                def __enter__(self): self.acquire(); return self
                def __exit__(self,*args): self.release()
            setattr(obj,attrs[0],TracedLock(native,owner))
        _assert(locks[0] is not locks[1], 'shared instance lock')
        _assert(a.compare_and_set(0,10) is True)
        _assert(events and not held, 'CAS must acquire and release the lock')
        events.clear(); a.transfer_to(b,1)
        _assert(max((e[2] for e in events),default=0)==2 and not held, 'transfer must hold both locks')
        order=[e[1] for e in events]
        events.clear(); b.transfer_to(a,1)
        _assert([e[1] for e in events]==order and not held, 'opposite transfers must use same lock order')
    return _score([('atomic-API',api),('transfer-validation',validation),('instrumented-lock-scope',lock_scope),
                   ('opposite-transfers',concurrent),('contended-CAS',cas_contended)])

TESTERS = {'CODE-06':test_cache, 'CODE-07':test_leaves, 'CODE-09':test_retry,
           'CODE-10':test_machine, 'CODE-11':test_discounts, 'CODE-12':test_counter}

def build_graders(expect_executable_code, extract_python, counter_contract):
    graders = {sid: expect_executable_code(test_fn=fn) for sid,fn in TESTERS.items()}
    counter_exec = graders['CODE-12']
    def counter(resp):
        code = extract_python(resp)
        if not code:
            return 0.0, 'no Python code found'
        score, why = counter_contract(code)
        if score < 1: return score, why
        return counter_exec(resp)
    graders['CODE-12'] = counter
    return graders
