"""No extra dependencies beyond requirements.txt. Run python -m unittest -v test_chemistry_comparison."""
import hashlib
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from app import Handler
from chemistry_comparison import compare
from success_model import estimate, SPECIES, ENDPOINTS

class ComparisonTests(unittest.TestCase):
    def test_default_and_reference(self):
        d = compare()
        self.assertIsNone(d['ece_scenario_ds_m'])
        self.assertFalse(d['phoenix_ec_converted'])
        self.assertFalse(d['crop_success_probabilities_changed'])
        self.assertTrue(all(r['exceeds_threshold'] is None for r in d['rows']))
        for sample in ('RR', 'S1', 'S2'):
            d = compare(sample=sample)
            self.assertEqual(d['sample'], sample)
            ph = next(r for r in d['phoenix_reference'] if r['analyte'] == 'pH')
            self.assertEqual(ph['value'], {'RR':7.7,'S1':7.6,'S2':None}[sample])
        self.assertIsNone(next(r for r in compare()['phoenix_reference'] if r['analyte']=='EC_25C')['value'])
    def test_conditional_change(self):
        rows = {r['name']:r for r in compare(3)['rows']}
        self.assertTrue(rows['Carrot']['exceeds_threshold'])
        self.assertTrue(rows['Tomato']['exceeds_threshold'])
        self.assertFalse(rows['Rye']['exceeds_threshold'])
        self.assertIsNone(rows['Garden cress']['exceeds_threshold'])
    def test_boundary_and_endpoint(self):
        for r in compare()['rows']:
            if r['ece_threshold_ds_m'] is not None:
                actual = next(x for x in compare(r['ece_threshold_ds_m'])['rows'] if x['species']==r['species'])
                self.assertFalse(actual['exceeds_threshold'])
        rye = next(r for r in compare(8)['rows'] if r['name']=='Rye')
        self.assertEqual(rye['endpoint'], 'grain yield')
        self.assertEqual(rye['ece_threshold_ds_m'], 11.4)
        self.assertFalse(rye['exceeds_threshold'])
    def test_invalid_inputs(self):
        for x in [10**400,-1,41,float('nan'),float('inf'),True,'3','bad',[],{}]:
            with self.assertRaises((ValueError, TypeError)): compare(x)
        for sample in ['mars','',None]:
            with self.assertRaises(ValueError): compare(sample=sample)
    def test_baseline_and_missing_cutoffs(self):
        for ece in [None,0,1,3,8,12,40]:
            for r in compare(ece)['rows']:
                expected = estimate(r['species'],'alive50',3)['results']['Mars']
                self.assertEqual(r['baseline']['posterior_mean'], expected['posterior_mean'])
                self.assertEqual(r['baseline']['successes'], expected['successes'])
                self.assertIsNone(r['ph_cutoff'])
                self.assertIsNone(r['perchlorate_growth_cutoff'])
    def test_frozen_60_original_results(self):
        # Generated in the recovered, unchanged 7291c237 reference checkout;
        # all success_model/data files identical to original 057cd105 tree.
        results = [estimate(s,e,n) for s in SPECIES for e in ENDPOINTS for n in range(1,6)]
        digest = hashlib.sha256(json.dumps(results,sort_keys=True,allow_nan=False).encode()).hexdigest()
        self.assertEqual(digest, 'ce4750167414887872c1cbcc33088f58e0e4607bc48020148f8c9e612d7b76c4')

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_port)
        cls.worker = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join()
    def post(self,payload):
        req = urllib.request.Request(self.url+'/api/chemistry-comparison',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        return json.load(urllib.request.urlopen(req))
    def test_routes_and_scenario(self):
        for route in ['/','/health','/api/options','/api/mars','/api/candidates','/api/crop-reference','/api/phoenix-reference','/phoenix.js','/api/chemistry-comparison','/chemistry-comparison.js']:
            with urllib.request.urlopen(self.url+route) as response:self.assertEqual(response.status,200)
        d = self.post({'ece':3,'sample':'S2'})
        self.assertEqual(d['sample'],'S2');self.assertEqual(d['ece_scenario_ds_m'],3)
        self.assertEqual(len(d['rows']),4)
        self.assertEqual(set(d['method']),set(d['method_en']))
        for row in d['rows']:
            for field in ['ph_evidence_en','caveat_en','perchlorate_evidence_en']: self.assertTrue(row[field])
        for source in d['sources']: self.assertTrue(source['label_en'])
    def test_bad_requests(self):
        for payload in [{'ece':10**400},{'ece':-1},{'ece':True},{'ece':'3'},{'sample':'bad'},{'ph':7.7},[],{'ece':float('nan')}]:
            with self.assertRaises(urllib.error.HTTPError) as err:self.post(payload)
            self.assertEqual(err.exception.code,400)
    def test_original_success_route(self):
        for species in SPECIES:
            for endpoint in ENDPOINTS:
                req = urllib.request.Request(self.url+'/api/success',data=json.dumps({'species':species,'endpoint':endpoint,'minimum':3}).encode(),headers={'Content-Type':'application/json'})
                actual = json.load(urllib.request.urlopen(req));expected=estimate(species,endpoint,3)
                self.assertEqual(actual['results'],expected['results'])

if __name__=='__main__':unittest.main(verbosity=2)
