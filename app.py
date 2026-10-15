import json,os
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import pandas as pd
from success_model import estimate,ranking,SPECIES,ENDPOINTS
ROOT=Path(__file__).parent
class Handler(BaseHTTPRequestHandler):
    def respond(self,body,kind='application/json',status=200):
        if not isinstance(body,bytes):body=json.dumps(body,allow_nan=False).encode()
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=='/health':self.respond({'status':'ok','model':'pot-level-cultivation-success-v2'})
        elif self.path=='/api/crop-reference':
            crop=pd.read_csv(ROOT/'data/Crop_recommendation.csv')
            rows=[]
            for label,g in crop.groupby('label'):
                row={'crop':label}
                for f in ['N','P','K','temperature','humidity','ph','rainfall']:
                    row[f]={'min':float(g[f].min()),'median':float(g[f].median()),'max':float(g[f].max())}
                row['phoenix_ph_matching_rows']=int(g.ph.between(7.2,8.2).sum())
                row['dataset_rows']=len(g)
                rows.append(row)
            self.respond({'phoenix_ph':{'point':7.7,'reported_uncertainty':0.5,'screen_window':[7.2,8.2],'source':'https://pubmed.ncbi.nlm.nih.gov/19574385/','meaning':'One landing site and measurement method; not a global Mars soil distribution or confidence interval'},'rows':rows,'interpretation':'Observed terrestrial ranges, not physiological limits or Mars success probabilities','overlap_with_trial_crops':[]})
        elif self.path=='/api/options':self.respond({'species':SPECIES,'endpoints':{k:v[1] for k,v in ENDPOINTS.items()}})
        elif self.path=='/api/mars':
            m=pd.read_csv(ROOT/'data/ds01_2020je006536rr.csv',encoding='latin1')
            s=m[m.Strat_group.eq('Soil')][['Sol','Target','P2O5','K2O','Comments/Interpretation']].fillna('')
            self.respond({'source':'https://doi.org/10.17189/1519050','units':'Bulk oxide wt%; not plant-available nutrients','rows':s.to_dict('records')})
        elif self.path=='/':self.respond((ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
        else:self.respond({'error':'Not found'},status=404)
    def do_POST(self):
        if self.path!='/api/success':self.respond({'error':'Not found'},status=404);return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=10000:raise ValueError('Invalid request size')
            p=json.loads(self.rfile.read(size))
            if not isinstance(p,dict):raise ValueError('Expected JSON object')
            minimum=float(p.get('minimum',3));transfer=p.get('transfer')
            d=estimate(str(p.get('species','S. lycopersicum')),str(p.get('endpoint','alive50')),minimum,transfer)
            d['crop_comparison']=ranking(d['endpoint'],d['minimum']);self.respond(d)
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.respond({'error':str(e)},status=400)
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','10000'))),Handler).serve_forever()
