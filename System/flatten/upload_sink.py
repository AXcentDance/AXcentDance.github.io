#!/usr/bin/env python3
"""CORS sink for the critical.html harness (port 3001).

The harness runs in the browser and cannot write files; it POSTs its result
here. Run alongside the static server, then in the harness console:
  await runCritical()   // POSTs ids to /save automatically (see critical.html)
Writes System/flatten/critical_ids.json, then feed scripts/critical_css.py apply.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import pathlib

DEST = pathlib.Path(__file__).resolve().parent / 'critical_ids.json'


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'content-type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path != '/save':
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        length = int(self.headers.get('Content-Length', 0))
        DEST.write_bytes(self.rfile.read(length))
        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(b'saved')

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    print(f'critical-ids sink on :3001 -> {DEST}')
    HTTPServer(('127.0.0.1', 3001), Handler).serve_forever()
