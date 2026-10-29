import unittest,json,threading,urllib.request,urllib.error,hashlib,subprocess,sys
from pathlib import Path
from http.server import ThreadingHTTPServer
from app import Handler
from lettuce_evidence import get_lettuce_evidence
from crop22_comparison import compare_crop22
from chemistry_comparison import compare
class LettuceTests(unittest.TestCase):
 def test_studies_and_units(self):
  d=get_lettuce_evidence();self.assertEqual(len(d['studies']),4);self.assertFalse(d['growth_model_fitted']);self.assertIsNone(d['similarity_score'])
  e=d['studies'][0];self.assertEqual(len(e['tables'][0]['rows']),4);self.assertEqual(len(e['tables'][0]['rows'][0]),10);self.assertEqual(e['tables'][1]['rows'][-1][3],25.5)
  br=d['studies'][2];self.assertEqual(len(br['tables'][0]['rows']),48);self.assertTrue(any(r[3]=='k' and r[4] is None and r[5]==0 for r in br['tables'][0]['rows']))
  self.assertIn('not relabeled g/plant',br['tables'][1]['note']['en'])
 def test_ph_and_missing(self):
  for s,v in [('RR',7.7),('S1',7.6),('S2',None)]:
   d=get_lettuce_evidence(s);p=d['ph_comparison'];self.assertEqual(p['value'],v);self.assertEqual(p['observed_readings'],220);self.assertEqual(p['point_inside'],None if s=='S2' else True)
   self.assertEqual(p['numerical_overlap'],None if s=='S2' else True)
 def test_coverage(self):
  d=get_lettuce_evidence();self.assertEqual(len(d['parameter_coverage']),8);p=next(r for r in d['parameter_coverage'] if r['analyte']=='P / phosphate');self.assertIn('No equivalent available P',p['phoenix']['en']);self.assertIn('Curiosity',p['phoenix']['en'])
  self.assertEqual(len(d['phoenix_chemistry_rows']),11)
  for row in d['parameter_coverage']:
   for k in ['terrestrial','phoenix','comparability']:self.assertEqual(set(row[k]),{'pt','en'})
 def test_validation(self):
  for v in ['',None,True,1,[],{},'Mars']:
   with self.assertRaises(ValueError):get_lettuce_evidence(v)
 def test_reproducible(self):
  root=Path(__file__).parent;p=root/'data/lettuce_evidence.json';before=p.read_bytes();subprocess.run([sys.executable,str(root/'research/lettuce/build_evidence.py')],check=True);self.assertEqual(before,p.read_bytes())
 def test_baselines_not_mutated(self):
  before=(compare_crop22(),compare());get_lettuce_evidence('S2');self.assertEqual(before,(compare_crop22(),compare()))
 def test_http(self):
  srv=ThreadingHTTPServer(('127.0.0.1',0),Handler);t=threading.Thread(target=srv.serve_forever,daemon=True);t.start();base='http://127.0.0.1:'+str(srv.server_port)
  try:
   for path in ['/api/lettuce-evidence','/lettuce-evidence.js']:
    with urllib.request.urlopen(base+path) as r:self.assertEqual(r.status,200)
   for data,status in [({'sample':'S2'},200),({'sample':[]},400),({'ece':3},400),([],400)]:
    req=urllib.request.Request(base+'/api/lettuce-evidence',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    try:
     with urllib.request.urlopen(req) as r:self.assertEqual(r.status,status)
    except urllib.error.HTTPError as e:self.assertEqual(e.code,status)
  finally:srv.shutdown();srv.server_close();t.join()
if __name__=='__main__':unittest.main()
