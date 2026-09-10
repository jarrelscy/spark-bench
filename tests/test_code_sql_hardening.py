"""SQL reference queries and deliberate mutants, not model-run evidence."""
import unittest
import eval_suite as suite
import code_sql_hardening as upgrade

REVENUE = '''WITH refund_totals AS (
 SELECT order_id, SUM(COALESCE(refund_amount,0)) AS refunded FROM refunds GROUP BY order_id
), nets AS (
 SELECT c.id AS customer_id, c.name AS customer_name,
 SUM(COALESCE(o.amount,0)-COALESCE(r.refunded,0)) AS net_revenue
 FROM customers c JOIN orders o ON o.customer_id=c.id
 LEFT JOIN refund_totals r ON r.order_id=o.id
 WHERE o.status='completed'
 GROUP BY c.id,c.name
)
SELECT customer_id,customer_name,net_revenue FROM nets
WHERE net_revenue>100 ORDER BY net_revenue DESC,customer_id ASC'''
SALES = '''SELECT id,region,month,amount,
 SUM(COALESCE(amount,0)) OVER(PARTITION BY region ORDER BY month,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
 RANK() OVER(PARTITION BY region ORDER BY amount DESC NULLS LAST) AS amount_rank
 FROM sales ORDER BY region ASC,month ASC,id ASC'''
SOLUTIONS = {'CODE-02': REVENUE, 'CODE-08': SALES}
MUTATIONS = {
 'CODE-02': [
  ('includes-cancelled', "WHERE o.status='completed'", 'WHERE 1=1'),
  ('merges-duplicate-names', 'GROUP BY c.id,c.name', 'GROUP BY c.name'),
  ('inclusive-threshold', 'net_revenue>100', 'net_revenue>=100'),
  ('refund-fanout', 'LEFT JOIN refund_totals r ON r.order_id=o.id', 'LEFT JOIN refunds r ON r.order_id=o.id'),
  ('missing-null-defaults', 'COALESCE(r.refunded,0)', 'r.refunded'),
 ],
 'CODE-08': [
  ('row-number-not-rank', 'RANK()', 'ROW_NUMBER()'),
  ('dense-rank-no-gaps', 'RANK()', 'DENSE_RANK()'),
  ('month-peer-frame', 'ORDER BY month,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW', 'ORDER BY month'),
  ('nulls-ranked-first', 'DESC NULLS LAST', 'DESC NULLS FIRST'),
  ('cross-region-running-total', 'PARTITION BY region ORDER BY month,id', 'ORDER BY month,id'),
 ]
}

class SQLHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.graders=upgrade.build_graders(suite.expect_sql_code)

    def test_reference_queries(self):
        for sid,query in SOLUTIONS.items():
            with self.subTest(scenario=sid):
                score,reason=self.graders[sid]({'text':query})
                self.assertEqual(score,1,reason)

    def test_mutants_rejected(self):
        for sid,mutations in MUTATIONS.items():
            for name,old,new in mutations:
                with self.subTest(scenario=sid,defect=name):
                    query=SOLUTIONS[sid].replace(old,new)
                    if name=='refund-fanout': query=query.replace('r.refunded','r.refund_amount')
                    score,reason=self.graders[sid]({'text':query})
                    self.assertLess(score,1,reason)

    def test_empty_malformed_and_constant_queries(self):
        for sid,grade in self.graders.items():
            for query in ['', 'SELECT FROM', "SELECT 1,'Same',200", 'SELECT 1,2,3,4,5,6']:
                with self.subTest(scenario=sid,query=query):
                    self.assertEqual(grade({'text':query})[0],0)

    def test_fixture_generators_deterministic(self):
        self.assertEqual(upgrade.revenue_fixtures(),upgrade.revenue_fixtures())
        self.assertEqual(upgrade.sales_fixtures(),upgrade.sales_fixtures())

if __name__ == '__main__': unittest.main()
