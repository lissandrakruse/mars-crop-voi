import json
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from app import Handler
from crop22_comparison import compare_crop22, ph_position

class Crop22Tests(unittest.TestCase):
    def rows(self, **kwargs): return {r['crop']:r for r in compare_crop22(**kwargs)['rows']}
    def test_coverage_and_defaults(self):
        d=compare_crop22();self.assertEqual(len(d['rows']),22)
        self.assertEqual(sum(r['crop_observed_ph']['n'] for r in d['rows']),2200)
        self.assertEqual({r['crop'] for r in d['rows'] if r['selected_taxon'] is None},{'banana','cotton','jute','coffee'})
        self.assertIsNone(d['ece_scenario_ds_m']);self.assertFalse(d['wamelink_results_changed']);self.assertFalse(d['phoenix_ec_converted']);self.assertIsNone(d['combined_rank'])
    def test_ph_is_position_not_growth(self):
        r=self.rows();self.assertEqual(r['chickpea']['ph_position'],'within_optimal');self.assertEqual(r['watermelon']['ph_position'],'outside_absolute')
        for row in self.rows(sample='S2').values():self.assertIn(row['ph_position'],['unknown','taxon_unresolved'])
        self.assertEqual(compare_crop22(sample='S1')['phoenix_ph']['value'],7.6)
        self.assertEqual(r['watermelon']['ph_uncertainty_endpoint_positions'],['within_absolute','outside_absolute'])
    def test_explicit_species_selection(self):
        r=self.rows(ece=3,selections={'cotton':1160});self.assertEqual(r['cotton']['selected_taxon']['scientific_name'],'Gossypium hirsutum');self.assertEqual(r['cotton']['scenario_status'],'not_above_reported_threshold')
        other=next(t['ecoport_id'] for t in r['cotton']['candidates'] if t['ecoport_id']!=1160)
        self.assertEqual(self.rows(ece=3,selections={'cotton':other})['cotton']['scenario_status'],'no_comparable_threshold')
        self.assertIsNone(self.rows(selections={'maize':None})['maize']['selected_taxon'])
    def test_salt_exceptions_and_boundary(self):
        r=self.rows(ece=3)
        self.assertEqual(r['rice']['scenario_status'],'no_comparable_threshold');self.assertFalse(r['rice']['salinity_evidence']['comparison_eligible'])
        for crop,value in [('kidneybeans',1),('maize',1.7)]:
            self.assertEqual(r[crop]['scenario_status'],'above_reported_threshold')
            self.assertEqual(self.rows(ece=value)[crop]['scenario_status'],'not_above_reported_threshold')
        self.assertEqual(r['mungbean']['scenario_status'],'no_comparable_threshold')
    def test_input_validation(self):
        for value in [10**400,True,'3',-1,41,float('nan'),float('inf'),[],{}]:
            with self.assertRaises(ValueError):compare_crop22(ece=value)
        for sel in [{'maize':True},{'maize':'2175'},{'maize':1160},{'fake':1},[],3]:
            with self.assertRaises(ValueError):compare_crop22(selections=sel)
        for sample in ['Mars',None,[],True]:
            with self.assertRaises(ValueError):compare_crop22(sample=sample)
    def test_no_missing_range_inference(self):
        t={'ph_absolute_min':None,'ph_absolute_max':8,'ph_optimal_min':6,'ph_optimal_max':7}
        self.assertEqual(ph_position(6.5,t),'unknown')
    def test_licence_and_methods(self):
        d=compare_crop22();self.assertEqual(d['sources']['ecocrop']['license']['id'],'CC-BY-4.0')
        for row in d['rows']:
            for t in row['candidates']:self.assertIn('Not specified',t['measurement_method']['soil_ph'])
    def test_http(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://127.0.0.1:'+str(server.server_port)
        try:
            with urllib.request.urlopen(base+'/api/crop22-comparison') as res:self.assertEqual(len(json.load(res)['rows']),22)
            for payload,code in [({'sample':'S2','ece':3,'selections':{'cotton':1160}},200),({'ph':7.7},400),({'ece':10**400},400),({'selections':{'maize':True}},400),([],400)]:
                req=urllib.request.Request(base+'/api/crop22-comparison',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(req) as res:self.assertEqual(res.status,code)
                except urllib.error.HTTPError as e:self.assertEqual(e.code,code)
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
