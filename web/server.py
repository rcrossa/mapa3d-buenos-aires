#!/usr/bin/env python3
"""
Development HTTP server with CORS + Range Requests for PMTiles.
Serves the web viewer and PMTiles from the repo root.

Usage:
    python3 web/server.py
    python3 web/server.py --port 3000

Note: Uses ThreadingHTTPServer for basic concurrency.
Wildcard CORS is intentional — dev-only server, never expose to networks.
For production, use a proper WSGI/ASGI server (gunicorn, uvicorn).
"""
import os
import sys
from http.server import ThreadingHTTPServer

from RangeHTTPServer import RangeRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CORSRequestHandler(RangeRequestHandler):
    # Sensitive paths that must never be served over HTTP.
    _BLOCKED_PATHS = frozenset({
        '.env', '.env.example', 'config.json',
    })
    _BLOCKED_PREFIXES = ('scripts/', 'tests/', 'archived/', '.git/')

    def do_GET(self):
        path = self.path.lstrip('/')
        if path in self._BLOCKED_PATHS:
            self.send_error(403, "Forbidden")
            return
        for prefix in self._BLOCKED_PREFIXES:
            if path.startswith(prefix):
                self.send_error(403, "Forbidden")
                return
        super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()


def _parse_port(argv):
    """Parse --port from argv. Returns 8000 as default."""
    try:
        for i, arg in enumerate(argv):
            if arg == '--port' and i + 1 < len(argv):
                return int(argv[i + 1])
        return 8000
    except (ValueError, IndexError):
        print("ERROR: --port requires a valid integer, e.g. --port 3000")
        sys.exit(1)


if __name__ == '__main__':
    os.chdir(REPO_ROOT)

    if '--host' in sys.argv:
        print(
            "WARNING: Binding to non-localhost. "
            "CORS is wildcard \u2014 never expose to untrusted networks."
        )

    port = _parse_port(sys.argv)

    print(f"PMTiles dev server at http://localhost:{port}")
    print(f"Viewer: http://localhost:{port}/web/index.html")
    server = ThreadingHTTPServer(('localhost', port), CORSRequestHandler)
    server.serve_forever()
