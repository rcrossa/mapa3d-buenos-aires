#!/usr/bin/env python3
"""
Development HTTP server with CORS + Range Requests for PMTiles.
Serves the web viewer and PMTiles from the repo root.

Usage:
    python3 web/server.py
    python3 web/server.py --port 3000

Note: Uses ThreadingHTTPServer for basic concurrency.
For production, use a proper WSGI/ASGI server (gunicorn, uvicorn).
"""
import os
import sys
from http.server import ThreadingHTTPServer

from RangeHTTPServer import RangeRequestHandler

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

    print(f"PMTiles dev server at http://localhost:{port}")
    print(f"Viewer: http://localhost:{port}/web/index.html")
    server = ThreadingHTTPServer(('localhost', port), CORSRequestHandler)
    server.serve_forever()
