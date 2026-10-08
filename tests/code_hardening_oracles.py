"""Hand-authored grader oracles, NOT model benchmark results."""
import textwrap

SOLUTIONS = {}
SOLUTIONS['CODE-06'] = '''
import time, math
from collections import OrderedDict
class KVCache:
    def __init__(self, capacity, ttl_seconds, clock=None):
        if type(capacity) is not int or capacity < 0: raise ValueError()
        if type(ttl_seconds) not in (int,float) or not math.isfinite(ttl_seconds) or ttl_seconds < 0: raise ValueError()
        self.capacity=capacity; self.ttl=ttl_seconds; self.clock=clock if clock is not None else time.monotonic
        self.data=OrderedDict()
    def purge(self, now):
        for k in list(self.data):
            if now >= self.data[k][1]: del self.data[k]
    def get(self,key):
        self.purge(self.clock())
        if key not in self.data: return None
        self.data.move_to_end(key); return self.data[key][0]
    def put(self,key,value):
        now=self.clock(); self.purge(now)
        self.data.pop(key,None)
        if not self.capacity or not self.ttl: return
        while len(self.data)>=self.capacity: self.data.popitem(last=False)
        self.data[key]=(value,now+self.ttl)
    def delete(self,key):
        self.purge(self.clock())
        if key not in self.data: return False
        del self.data[key]; return True
'''
SOLUTIONS['CODE-07'] = '''
def extract_leaves(value, with_paths=False):
    out=[]; active=set(); stack=[(value,'',False)]
    while stack:
        item,path,leave=stack.pop()
        if leave:
            active.remove(id(item)); continue
        if isinstance(item,(dict,list)):
            if id(item) in active: raise ValueError('cycle')
            active.add(id(item)); stack.append((item,path,True))
            if isinstance(item,dict):
                children=[]
                for k,v in item.items():
                    if not isinstance(k,str): raise TypeError('key')
                    children.append((v,path+'/'+k.replace('~','~0').replace('/','~1'),False))
            else: children=[(v,path+'/'+str(i),False) for i,v in enumerate(item)]
            stack.extend(reversed(children))
        else:
            if item is not None and not isinstance(item,(str,int,float,bool)): raise TypeError('scalar')
            out.append((path,item) if with_paths else item)
    return out
'''
SOLUTIONS['CODE-09'] = '''
import time, math
def retry_with_backoff(func,max_retries=3,initial_delay=0.1,backoff_factor=2,*,retry_on=(Exception,),max_delay=None,sleep=None):
    if type(max_retries) is not int or max_retries<0: raise ValueError()
    for x,lower in [(initial_delay,0),(backoff_factor,1)]+([] if max_delay is None else [(max_delay,0)]):
        if type(x) not in (int,float) or not math.isfinite(x) or x<lower: raise ValueError()
    if not isinstance(retry_on,tuple) or not retry_on or any(not isinstance(t,type) or not issubclass(t,Exception) for t in retry_on): raise ValueError()
    sleeper=time.sleep if sleep is None else sleep
    delay=initial_delay
    for i in range(max_retries+1):
        try: return func()
        except retry_on:
            if i==max_retries: raise
            sleeper(delay if max_delay is None else min(delay,max_delay))
            delay*=backoff_factor
'''
SOLUTIONS['CODE-10'] = '''
class StateMachine:
    def __init__(self,transitions,initial_state,*,guards=None,actions=None):
        self.transitions=dict(transitions); self.guards=dict(guards or {}); self.actions=dict(actions or {})
        self.state=initial_state; self.busy=False
    def current(self): return self.state
    def can_trigger(self,event): return (self.state,event) in self.transitions
    def trigger(self,event,**payload):
        if self.busy: raise RuntimeError('nested')
        key=(self.state,event)
        if key not in self.transitions: raise ValueError('unknown')
        old=self.state; new=self.transitions[key]; self.busy=True
        try:
            if key in self.guards and not self.guards[key](old,event,payload): raise ValueError('guard')
            if key in self.actions: self.actions[key](old,new,event,payload)
            self.state=new
            return new
        finally: self.busy=False
'''
SOLUTIONS['CODE-11'] = '''
def _apply_discount(price,discount_type,value):
    if price<0: raise ValueError('negative price')
    if discount_type=='percentage': return round(price*(1-value/100),2)
    if discount_type=='fixed': return round(max(price-value,0),2)
    if discount_type=='bogo': return 0 if value<1 else round((value//2+value%2)*price,2)
    raise ValueError('unknown discount')
def percentage_discount(price,percent): return _apply_discount(price,'percentage',percent)
def fixed_discount(price,amount): return _apply_discount(price,'fixed',amount)
def bogo_discount(price,quantity): return _apply_discount(price,'bogo',quantity)
def chained_discounts(price,steps):
    if price<0: raise ValueError('negative price')
    for kind,value in steps: price=_apply_discount(price,kind,value)
    return price
'''
SOLUTIONS['CODE-12'] = '''
import threading
class SafeCounter:
    def __init__(self): self._value=0; self.lock=threading.Lock()
    def increment(self,n=1):
        with self.lock: self._value+=n
    def decrement(self,n=1):
        with self.lock: self._value-=n
    def value(self):
        with self.lock: return self._value
    def compare_and_set(self,expected,new):
        with self.lock:
            if self._value!=expected: return False
            self._value=new; return True
    def transfer_to(self,other,n):
        if type(n) is not int or n<0: raise ValueError()
        if self is other: return
        first,second=sorted((self,other),key=id)
        with first.lock:
            with second.lock:
                self._value-=n; other._value+=n
'''
SOLUTIONS = {k:textwrap.dedent(v) for k,v in SOLUTIONS.items()}

# Plausible implementation defects: each must lose at least one tested group.
MUTATIONS = {
 'CODE-06': [
  ('expiry-boundary', 'now >= self.data[k][1]', 'now > self.data[k][1]'),
  ('no-expiry-purge-before-eviction', 'now=self.clock(); self.purge(now)', 'now=self.clock()'),
  ('FIFO-not-LRU', 'self.data.move_to_end(key); return', 'return'),
 ],
 'CODE-07': [
  ('reversed-order', 'stack.extend(reversed(children))', 'stack.extend(children)'),
  ('global-visited-not-ancestors', 'active.remove(id(item)); continue', 'continue'),
  ('wrong-pointer-escape', "k.replace('~','~0').replace('/','~1')", 'k'),
 ],
 'CODE-09': [
  ('retry-count-off-by-one', 'range(max_retries+1)', 'range(max_retries)'),
  ('ignores-retry-filter', 'except retry_on:', 'except Exception:'),
  ('ignores-max-delay', 'delay if max_delay is None else min(delay,max_delay)', 'delay'),
 ],
 'CODE-10': [
  ('retains-caller-dict', 'self.transitions=dict(transitions)', 'self.transitions=transitions'),
  ('commits-before-action', 'if key in self.actions: self.actions[key](old,new,event,payload)', 'self.state=new\n            if key in self.actions: self.actions[key](old,new,event,payload)'),
  ('busy-never-cleared', 'finally: self.busy=False', 'finally: pass'),
 ],
 'CODE-11': [
  ('clamps-percentage', 'round(price*(1-value/100),2)', 'round(max(0,price*(1-value/100)),2)'),
  ('wrapper-duplicates-logic', "return _apply_discount(price,'fixed',amount)", "return round(max(price-amount,0),2)"),
  ('empty-chain-rounding-drift', 'return price\n', 'return round(price,2)\n'),
 ],
 'CODE-12': [
  ('missing-CAS-update', 'self._value=new; return True', 'return True'),
  ('unlocked-CAS', '        with self.lock:\n            if self._value!=expected: return False\n            self._value=new; return True', '        if self._value!=expected: return False\n        self._value=new; return True'),
  ('non-atomic-transfer', '        with first.lock:\n            with second.lock:\n                self._value-=n; other._value+=n', '        self.decrement(n); other.increment(n)'),
  ('transfer-creates-value', 'self._value-=n; other._value+=n', 'self._value+=n; other._value+=n'),
  ('self-transfer-deadlock', 'if self is other: return', 'if self is other: self.lock.acquire(); self.lock.acquire(); return'),
 ]
}
