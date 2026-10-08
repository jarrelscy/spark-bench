import pathlib,sys,unittest
from unittest.mock import patch
sys.path[:0]=[str(pathlib.Path(__file__).resolve().parents[1]/'tools')]
import provisional_score as p

class Tests(unittest.TestCase):
 def test_matches_live_aggregator_with_latency_efficiency_and_agentic_rule(self):
  scenarios=[];records=[];responses=[]
  for i,(sid,domain,group,agentic) in enumerate([
      ('X','code','capability',False),('Y','robustness','calibration',False),
      ('SA-03','safety','calibration',False),('A','agentic','capability',True)]):
   scenarios.append(dict(id=sid,domain=domain,group=group,difficulty=i+1,messages=[],max_tokens=100,
    agentic=agentic,grade=lambda r:(r['score'],'ok')))
   for repeat in (1,2):
    score=1. if repeat==1 else .4
    latency=10.*(i+1)*repeat
    resp=dict(text='a'*40,reasoning='b'*120,total=latency,score=score,finish='stop')
    records.append(dict(scenario_id=sid,repeat=repeat,score=score,domain=domain,group=group,
      difficulty=i+1,latency_s=latency,efficiency=1. if agentic else .25,error=False))
    responses.append(resp)
  it=iter(responses)
  def chat(*args):return next(it)
  def agent(*args,**kw):
   r=next(it);return (r['score'],'ok',r['total'],r['text'],1.,{'finish':'stop','completion_tokens':10})
  with patch.object(p.ev,'SCENARIOS',scenarios),patch.object(p.ev,'_run_agentic',agent):
   expected=p.ev.run_suite(chat,repeats=2,uncapped=True)['overall']
  actual=p.aggregate(records)
  for k,v in actual['components'].items():self.assertAlmostEqual(v,expected[k],places=12)
  self.assertAlmostEqual(actual['truescore'],expected['truescore'],places=12)
 def test_partial_excluded_duplicate_refused(self):
  row=dict(scenario_id='x',repeat=1,score=1.,domain='code',group='capability',difficulty=1,
    latency_s=10.,efficiency=.5,error=False)
  with self.assertRaises(ValueError):p.aggregate([row])
  with self.assertRaises(ValueError):p.aggregate([row,row])
  both=[row,dict(row,repeat=2)]
  self.assertEqual(p.aggregate(both+[dict(row,scenario_id='partial')]),p.aggregate(both))

if __name__=='__main__':unittest.main()
