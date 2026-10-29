"""Offline regression and browser checks; run: python test_phoenix_v2.py."""
import json,pathlib,subprocess,sys,time,urllib.request,unittest
ROOT=pathlib.Path(__file__).parent
BASE=ROOT.parent/'mars_crop_baseline_057cd105'
class PhoenixTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import os
  cls.server=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,env={**os.environ,'PORT':'10081'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for i in range(50):
   try:urllib.request.urlopen('http://127.0.0.1:10081/health');break
   except OSError:time.sleep(.1)
 @classmethod
 def tearDownClass(cls):cls.server.terminate();cls.server.wait()
 def test_reference_integrity(self):
  data=json.load(urllib.request.urlopen('http://127.0.0.1:10081/api/phoenix-reference'));rows=data['rows'];self.assertEqual(len(rows),33)
  def row(id):return next(r for r in rows if r['id']==id)
  self.assertIsNone(row('PHX_018')['uncertainty_plus']);self.assertIsNone(row('PHX_027')['value']);self.assertIsNone(row('PHX_033')['value']);self.assertIsNone(row('PHX_014')['value']);self.assertEqual(row('PHX_003')['value'],.55)
  self.assertFalse(data['outcome_model_changed'])
 def test_crop_baseline_unchanged(self):
  if not BASE.exists():self.skipTest('External pinned baseline copy unavailable')
  for f in BASE.rglob('*'):
   if f.is_file() and f.name not in ('app.py','index.html','README.md') and '__pycache__' not in f.parts:self.assertEqual(f.read_bytes(),(ROOT/f.relative_to(BASE)).read_bytes(),str(f))
  base=(BASE/'app.py').read_text();updated=(ROOT/'app.py').read_text();self.assertIn(base[base.index('    def do_POST'):],updated)
 def test_existing_http_routes(self):
  for route in ['/','/health','/api/options','/api/mars','/api/candidates','/api/crop-reference','/phoenix.js']:
   self.assertEqual(urllib.request.urlopen('http://127.0.0.1:10081'+route).status,200)
  from success_model import SPECIES,ENDPOINTS
  for species in SPECIES:
   for endpoint in ENDPOINTS:
    req=urllib.request.Request('http://127.0.0.1:10081/api/success',data=json.dumps({'species':species,'endpoint':endpoint,'minimum':3}).encode(),headers={'Content-Type':'application/json'})
    self.assertEqual(urllib.request.urlopen(req).status,200)
 def test_ui_and_download(self):
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900},accept_downloads=True)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:10081');page.wait_for_selector('#phxSample');self.assertEqual(page.locator('#easyCounts .easy-card').count(),3)
   page.locator('#phxSample').select_option('Sorceress 2');self.assertIn('unreliable_sensor',page.locator('#phxContent').inner_text());self.assertIn('reported_value_upper_uncertainty_unresolved',page.locator('#phxContent').inner_text())
   page.locator('#phx_ph').fill('8.1');page.locator('#phx_ec').fill('1500');page.locator('#phxLanguage').select_option('en');self.assertEqual(page.locator('#phx_ph').input_value(),'8.1')
   page.locator('#phxSample').select_option('Sorceress 1');self.assertEqual(page.locator('#phx_ph').input_value(),'8.1');self.assertIn('not_detected',page.locator('#phxContent').inner_text())
   with page.expect_download() as d:page.locator('#phxForm button[type=submit]').click()
   output=json.load(open(d.value.path()));self.assertEqual(output['hypothesis']['values']['ph']['value'],8.1);self.assertIsNone(output['hypothesis']['values']['na']['value']);self.assertFalse(output['hypothesis']['affects_crop_model'])
   page.locator('#phxReset').click();self.assertEqual(page.locator('#phx_ph').input_value(),'');page.locator('#phxReset').click();page.locator('#phxLanguage').select_option('pt');page.locator('#phxSample').select_option('Rosy Red')
   page.screenshot(path=str(ROOT.parent/'phoenix-v2-desktop.png'),full_page=False)
   page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT.parent/'phoenix-v2-mobile.png'),full_page=False)
   self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'),390)
   self.assertEqual(errors,[]);browser.close()
if __name__=='__main__':unittest.main(verbosity=2)
