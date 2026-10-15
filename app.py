"""Minimal, dependency-free project landing page and health endpoint."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            body = json.dumps({'status': 'ok'}).encode()
            content_type = 'application/json'
        elif self.path == '/':
            body = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mars Crop VOI</title><style>body{background:#101826;color:#edf2f7;font:18px system-ui;max-width:850px;margin:10vh auto;padding:24px}h1{color:#f7ad80}p{line-height:1.7}a{color:#9bdacc}</style>
<h1>Mars Crop VOI</h1><p>Exploratory crop similarity and experimental-design research.</p>
<p>Project author: Lissandra Kruse Fuganti.</p>
<h2>Evidence</h2><p>Embedded terrestrial Crop Recommendation data and real Curiosity/APXS geochemical observations are available in the project notebook. Bulk chemistry is not plant-available nutrient content.</p>
<h2>Research status</h2><p>Greenhouse similarity scenarios are hypothetical. Mars cultivation probabilities and value-of-information calculations have not yet been implemented or validated.</p>
<p>This initial service provides project information and a health endpoint. Interactive analyses are the next development stage.</p>
<p><a href="https://doi.org/10.17189/1519050">NASA PDS APXS source</a></p></html>'''
            content_type = 'text/html; charset=utf-8'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', int(os.environ.get('PORT', '10000'))), Handler).serve_forever()
