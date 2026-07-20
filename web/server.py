#!/usr/bin/env python3
"""
Servidor HTTP con CORS y soporte Range Requests para desarrollo local.
Sirve el visor web y los PMTiles desde la raiz del repositorio.

Uso:
    python3 web/server.py
    python3 web/server.py --port 3000
"""
import os
import sys
from RangeHTTPServer import RangeRequestHandler
from http.server import HTTPServer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO_ROOT)


class CORSRequestHandler(RangeRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()


if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])

    print(f"Servidor optimizado para PMTiles en http://localhost:{port}")
    print(f"Visor: http://localhost:{port}/web/index.html")
    server = HTTPServer(('localhost', port), CORSRequestHandler)
    server.serve_forever()
