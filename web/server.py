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
from urllib.parse import unquote

from RangeHTTPServer import RangeRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CORSRequestHandler(RangeRequestHandler):
    # Sensitive paths that must never be served over HTTP.
    _BLOCKED_PATHS = frozenset({
        '.env', '.env.example', 'config.json',
    })
    _BLOCKED_PREFIXES = ('scripts/', 'tests/', 'archived/', '.git/')

    def _is_path_blocked(self):
        """Return True if self.path is blocked (403 already sent)."""
        raw = self.path.split('?')[0].split('#')[0]
        decoded = unquote(raw)

        # Fast-path: no suspicious chars — string-check directly,
        # avoiding filesystem syscalls on every PMTiles tile request.
        if '..' not in decoded and '%' not in raw and '~' not in decoded:
            clean = decoded.lstrip('/')
            if os.path.basename(clean) in self._BLOCKED_PATHS:
                self.send_error(403, "Forbidden")
                return True
            for prefix in self._BLOCKED_PREFIXES:
                if clean.startswith(prefix.rstrip('/')):
                    self.send_error(403, "Forbidden")
                    return True
            return False

        # Slow-path: paths with .., %, or ~ need realpath resolution.
        candidate = os.path.join(REPO_ROOT, decoded.lstrip('/'))
        resolved = os.path.realpath(candidate)

        # Block traversal outside REPO_ROOT (e.g., /../../../etc/passwd).
        if os.path.commonpath([resolved, REPO_ROOT]) != REPO_ROOT:
            self.send_error(403, "Forbidden")
            return True

        rel = os.path.relpath(resolved, REPO_ROOT)
        if os.path.basename(rel) in self._BLOCKED_PATHS:
            self.send_error(403, "Forbidden")
            return True
        for prefix in self._BLOCKED_PREFIXES:
            if rel.startswith(prefix.rstrip('/')):
                self.send_error(403, "Forbidden")
                return True
        return False

    def do_GET(self):
        if self._is_path_blocked():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._is_path_blocked():
            return
        super().do_HEAD()

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
