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

REPO_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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

    @classmethod
    def _setup_blocked_sets(cls, basenames, basename_prefixes, prefixes):
        """Normalise and validate blocked sets — shared by __init__ and tests."""
        if isinstance(basenames, str):
            raise TypeError(
                'blocked_basenames must be a set/frozenset, not a string')
        if isinstance(basename_prefixes, str):
            raise TypeError(
                'blocked_basename_prefixes must be a tuple, not a string')
        if isinstance(prefixes, str):
            raise TypeError(
                'blocked_prefixes must be a tuple, not a string')
        return (
            {b.lower() for b in basenames},
            tuple(p.lower() for p in basename_prefixes),
            tuple(p.lower() for p in prefixes),
        )

    def __init__(self, *args, **kwargs):
        # Injectable for testing — pop before passing to base class.
        # Force lowercase for case-insensitive matching (macOS APFS).
        basenames = kwargs.pop('blocked_basenames', self._BLOCKED_BASENAMES)
        prefix_tup = kwargs.pop(
            'blocked_basename_prefixes', self._BLOCKED_BASENAME_PREFIXES)
        prefixes = kwargs.pop(
            'blocked_prefixes', self._BLOCKED_PREFIXES)
        (self._blocked_basenames,
         self._blocked_basename_prefixes,
         self._blocked_prefixes) = self._setup_blocked_sets(
            basenames, prefix_tup, prefixes)
        super().__init__(*args, **kwargs)

    def _is_path_blocked(self):
        """Return True if self.path is blocked (403 already sent).

        Resolves the real filesystem path so symlinks and case-insensitive
        filesystems cannot bypass the block list.  The resolved path is
        cached on ``self._resolved_path`` so ``translate_path()`` reuses it
        — avoiding a wasteful second ``realpath()`` syscall.
        """
        raw = self.path.split('?')[0].split('#')[0]
        decoded = unquote(raw)
        clean = decoded.lstrip('/')

        if not clean:
            self._resolved_path = REPO_ROOT  # cache root for translate_path
            return False

        # Single realpath() syscall per request (catches symlinks, case
        # differences, .. traversal, and Unicode normalisation in one shot).
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

        try:
            rel = os.path.relpath(resolved, REPO_ROOT)
            basename_lower = os.path.basename(rel).lower()
        except (OSError, ValueError):
            self.send_error(403, "Forbidden")
            return True

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

        # Cache so translate_path() reuses this — no second realpath().
        self._resolved_path = resolved
        return False

    def translate_path(self, path):
        """Resolve against REPO_ROOT, reusing cached path when available.

        Overrides SimpleHTTPRequestHandler.translate_path() which uses
        os.getcwd() (process-global mutable state).  When _is_path_blocked()
        has already resolved the path we return the cached value directly.
        """
        cached = getattr(self, '_resolved_path', None)
        if cached is not None:
            del self._resolved_path
            return cached
        # Fallback — guarded with same containment as _is_path_blocked().
        path = path.split('?', 1)[0].split('#', 1)[0]
        path = unquote(path).lstrip('/')
        if not path:
            return REPO_ROOT
        try:
            resolved = os.path.realpath(os.path.join(REPO_ROOT, path))
        except (OSError, ValueError):
            return REPO_ROOT
        if os.path.commonpath([resolved, REPO_ROOT]) != REPO_ROOT:
            return REPO_ROOT
        return resolved

    def do_GET(self):
        if self._is_path_blocked():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._is_path_blocked():
            return
        super().do_HEAD()

    def do_OPTIONS(self):
        if self._is_path_blocked():
            return
        super().do_OPTIONS()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        # Immutable cache for PMTiles tile data; no-store for everything else.
        if self.path.split('?')[0].startswith('/data/tiles/'):
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
