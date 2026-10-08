"""Full-result SQL graders using multiple deterministic databases.

Expected rows are computed independently in Python, never by a second SQL query.
All candidate execution uses the existing SQLite sandbox in eval_suite.
"""
import random

PROMPTS = {
 'CODE-02': '''Write one SQLite SELECT query (WITH/CTEs allowed). Schema: customers(id INTEGER PRIMARY KEY, name TEXT, region TEXT); orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, status TEXT); refunds(order_id INTEGER, refund_amount REAL). Return exactly customer_id, customer_name, net_revenue for customers with net_revenue STRICTLY greater than100. Count only orders whose status is 'completed'. Each qualifying order's net is COALESCE(amount,0) minus the sum of ALL its refund rows (NULL refund values count0; no refunds count0). Multiple refunds must not multiply the order amount; refunds of non-completed orders do not count. Over-refunds and negative order amounts remain negative contributions; do not clamp. Customers with identical names remain separate by id. Exclude customers with no qualifying revenue. Order by net_revenue descending, then customer_id ascending. Return only SQL, no hardcoded customer names or result rows.''',
 'CODE-08': '''Write one SQLite SELECT query (WITH/CTEs allowed) for sales(id INTEGER PRIMARY KEY, region TEXT, month INTEGER NOT NULL, amount REAL). Return exactly id, region, month, amount, running_total, amount_rank for EVERY input row. running_total is a cumulative sum of COALESCE(amount,0) within each region in (month ASC,id ASC) order, using a ROWS frame from unbounded preceding through the current row. amount_rank is SQL RANK within region by amount descending, NULL amounts LAST; equal amounts share rank with gaps afterward. Preserve the original amount (including NULL), negative values, and every row. NULL region values form one partition. Output ordered by region ASC (NULL first), month ASC, id ASC. Input insertion order is arbitrary and months/amounts can tie. Return only SQL, no hardcoded result rows.'''
}

def _literal(value):
    if value is None: return 'NULL'
    if isinstance(value,str): return "'"+value.replace("'","''")+"'"
    return repr(value)

def _insert(table, rows):
    if not rows: return ''
    return 'INSERT INTO '+table+' VALUES '+','.join('('+','.join(map(_literal,r))+')' for r in rows)+';'

def _revenue_fixture(customers, orders, refunds):
    totals = {}
    for order_id, amount in refunds:
        totals[order_id] = totals.get(order_id,0)+(amount or 0)
    nets = {r[0]:0 for r in customers}
    for oid,cid,amount,status in orders:
        if status == 'completed' and cid in nets:
            nets[cid] += (amount or 0)-totals.get(oid,0)
    expected = sorted([(cid,name,nets[cid]) for cid,name,region in customers if nets[cid]>100],
                      key=lambda r:(-r[2],r[0]))
    schema = ('CREATE TABLE customers(id INTEGER PRIMARY KEY,name TEXT,region TEXT);'
              'CREATE TABLE orders(id INTEGER PRIMARY KEY,customer_id INTEGER,amount REAL,status TEXT);'
              'CREATE TABLE refunds(order_id INTEGER,refund_amount REAL);')
    schema += _insert('customers',customers)+_insert('orders',orders)+_insert('refunds',refunds)
    return schema, expected


def revenue_fixtures():
    customers=[(1,'Same','E'),(2,'Same','W'),(3,'Boundary','N'),(4,'No orders','S'),
               (5,'Cancelled','W'),(6,"O'Brien",None),(7,'Nulls','N')]
    orders=[(10,1,300,'completed'),(11,1,50,'completed'),(12,2,220,'completed'),
            (13,3,100,'completed'),(14,5,900,'cancelled'),(15,6,200,'completed'),
            (16,7,None,'completed'),(17,7,300,'completed'),(18,1,1000,'pending'),
            (19,2,-20,'completed')]
    refunds=[(10,40),(10,60),(10,None),(12,20),(15,None),(17,100),(18,1),(14,5)]
    result=[_revenue_fixture(customers,orders,refunds)]
    # Generated, fully specified DBs force the query to generalize beyond one
    # convenient list of names/ids. Small integers avoid floating-sum ambiguity.
    for seed in (208, 209, 210):
        rng=random.Random(seed)
        cs=[(100+i, 'duplicate' if i%2 else 'client-'+str(i), None) for i in range(8)]
        os=[]; rs=[]
        for i in range(28):
            oid=seed*100+i; cid=100+rng.randrange(8)
            os.append((oid,cid,rng.choice([None,-50,0,100,150,300,600]),rng.choice(['completed','completed','cancelled',None])))
            for _ in range(rng.randrange(4)): rs.append((oid,rng.choice([None,0,25,100,250])))
        rng.shuffle(os); rng.shuffle(rs)
        result.append(_revenue_fixture(cs,os,rs))
    result.append(_revenue_fixture([(1,'Empty',None)],[],[]))
    return result


def _sales_fixture(rows):
    groups={}
    for row in rows: groups.setdefault(row[1],[]).append(row)
    expected=[]
    for region in sorted(groups,key=lambda r:(r is not None, r or '')):
        group=groups[region]; running=0
        for oid,reg,month,amount in sorted(group,key=lambda r:(r[2],r[0])):
            running += amount or 0
            rank=1+sum(1 for r in group if r[3] is not None and (amount is None or r[3]>amount))
            expected.append((oid,reg,month,amount,running,rank))
    schema='CREATE TABLE sales(id INTEGER PRIMARY KEY,region TEXT,month INTEGER NOT NULL,amount REAL);'
    return schema+_insert('sales',rows),expected


def sales_fixtures():
    result=[_sales_fixture([(9,'N',2,None),(3,'N',1,100),(2,'N',1,100),(7,'N',2,-10),
                            (1,'S',1,0),(4,'S',1,None),(6,'S',2,200),(5,None,1,30),
                            (10,None,1,30),(12,'N',3,None)])]
    for seed in (808,809,810):
        rng=random.Random(seed)
        rows=[(i,rng.choice(['E','W',None]),rng.randrange(1,5),rng.choice([None,-20,0,40,40,100])) for i in range(1,25)]
        rng.shuffle(rows); result.append(_sales_fixture(rows))
    result.append(_sales_fixture([]))
    return result


def build_graders(expect_sql_code):
    result={}
    for sid,fixtures in [('CODE-02',revenue_fixtures()),('CODE-08',sales_fixtures())]:
        # Bind each dataset and output width independently.
        width=3 if sid=='CODE-02' else 6
        checks=[expect_sql_code(schema_sql=schema,test_queries=[
            ('entire-ordered-result', lambda rows,cursor,expected=expected,width=width: rows==expected and len(cursor.description)==width)
        ]) for schema,expected in fixtures]
        def grade(resp, checks=checks):
            outcomes=[check(resp) for check in checks]
            successes=sum(score==1 for score,why in outcomes)
            return successes/len(checks), f'{successes}/{len(checks)} complete SQL datasets: '+ '; '.join(
                f'db{i+1}:{why}' for i,(score,why) in enumerate(outcomes))
        result[sid]=grade
    return result
