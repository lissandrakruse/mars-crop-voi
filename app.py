import json,os
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from interval_model import analyze,DATA
ROOT=Path(__file__).parent
class Handler(BaseHTTPRequestHandler):
    def respond(self,body,kind='application/json',status=200):
        if not isinstance(body,bytes):body=json.dumps(body,allow_nan=False).encode()
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=='/health':self.respond({'status':'ok'})
        elif self.path=='/api/crops':self.respond(sorted(DATA.label.unique().tolist()))
        elif self.path=='/api/mars':
            m=pd.read_csv(ROOT/'data/ds01_2020je006536rr.csv',encoding='latin1')
            s=m[m.Strat_group.eq('Soil')][['Sol','Target','P2O5','K2O','Comments/Interpretation']].fillna('')
            self.respond({'source':'https://doi.org/10.17189/1519050','units':'P2O5 and K2O: wt% bulk oxides, not bioavailable nutrients','rows':s.to_dict('records')})
        elif self.path=='/':self.respond((ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
        else:self.respond({'error':'Not found'},status=404)
    def do_POST(self):
        if self.path!='/api/analyze':self.respond({'error':'Not found'},status=404);return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=10000:raise ValueError('Invalid request size')
            p=json.loads(self.rfile.read(size));self.respond(analyze(str(p['crop']),float(p['temperature']),float(p['humidity']),float(p['ph']),int(p.get('budget',6))))
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.respond({'error':str(e)},status=400)
import pandas as pd
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','10000'))),Handler).serve_forever()
