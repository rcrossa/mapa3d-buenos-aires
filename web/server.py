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
    """HTTP handler with path-blocking, CORS, and cache-aware headers."""

    # Sensitive basenames — case-insensitive match (macOS APFS default).
    _BLOCKED_BASENAMES = frozenset({
        '.env', '.env.example', 'config.json',
        'requirements.txt', 'dockerfile', 'docker-compose.yml',
        'makefile', '.dockerignore', '.gitignore',
        'pyproject.toml', 'setup.cfg',
    })
    # Basename prefixes that block variants: .env, .env.backup, .env.production.
    _BLOCKED_BASENAME_PREFIXES = ('.env',)
    # Directory prefixes never served.
    _BLOCKED_PREFIXES = ('scripts/', 'tests/', 'archived/', '.git/')

    def __init__(self, *args, **kwargs):
        # Injectable for testing — pop before passing to base class.
        self._blocked_basenames = kwargs.pop(
            'blocked_basenames', self._BLOCKED_BASENAMES)
        self._blocked_basename_prefixes = kwargs.pop(
            'blocked_basename_prefixes', self._BLOCKED_BASENAME_PREFIXES)
        self._blocked_prefixes = kwargs.pop(
            'blocked_prefixes', self._BLOCKED_PREFIXES)
        super().__init__(*args)

    def _is_path_blocked(self):
        """Return True if self.path is blocked (403 already sent).

        Always resolves the real filesystem path so symlinks and case-
        insensitive filesystems cannot bypass the block list.  The one
        ``realpath`` syscall is unavoidable — ``translate_path`` inside
        ``super().do_GET`` also calls it.
        """
        raw = self.path.split('?')[0].split('#')[0]
        decoded = unquote(raw)
        clean = decoded.lstrip('/')

        if not clean:
            return False  # root — allow directory listing

        # Resolve the real on-disk path (catches symlinks, case differences,
        # .. traversal, and Unicode normalisation in one shot).
        try:
            candidate = os.path.join(REPO_ROOT, clean)
            resolved = os.path.realpath(candidate)
        except (OSError, ValueError):
            self.send_error(403, "Forbidden")
            return True

        # Block any path that escapes REPO_ROOT.
        if os.path.commonpath([resolved, REPO_ROOT]) != REPO_ROOT:
            self.send_error(403, "Forbidden")
            return True

        rel = os.path.relpath(resolved, REPO_ROOT)
        basename_lower = os.path.basename(rel).lower()

        # Exact basename block (case-insensitive).
        if basename_lower in self._blocked_basenames:
            self.send_error(403, "Forbidden")
            return True

        # Prefix block — catches .env.backup, .env.production, etc.
        for prefix in self._blocked_basename_prefixes:
            if basename_lower.startswith(prefix):
                self.send_error(403, "Forbidden")
                return True

        # Directory prefix block.
        for prefix in self._blocked_prefixes:
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
        # Immutable cache for PMTiles tile data; no-store for everything else.
        if '/data/tiles/' in self.path:
            self.send_header('Cache-Control',
                             'public, max-age=31536000, immutable')
        else:
            self.send_header('Cache-Control',
                             'no-store, no-cache, must-revalidate')
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
    try:
        os.chdir(REPO_ROOT)
    except OSError as exc:
        print(f"ERROR: Cannot change to repo root {REPO_ROOT}: {exc}")
        sys.exit(1)

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
