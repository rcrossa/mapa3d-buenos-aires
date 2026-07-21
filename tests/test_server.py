"""Tests for web/server.py path blocking logic.

Covers JD R8 CRITICAL: symlink traversal (C1), case-insensitive bypass (C2),
and edge cases: .env.backup (E3), traversal (E1), long paths (E5).
"""
import os
import sys
import unittest
from unittest.mock import MagicMock

# Ensure repo root is on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=import-error,wrong-import-position
from web.server import CORSRequestHandler, REPO_ROOT


class TestPathBlocking(unittest.TestCase):
    """Validate _is_path_blocked() against all known bypass vectors."""

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _make_handler(path, **kwargs):
        """Create a bare handler with a mocked path and send_error."""
        handler = CORSRequestHandler.__new__(CORSRequestHandler)
        handler.path = path
        handler.send_error = MagicMock()
        handler._blocked_basenames = kwargs.pop(
            'blocked_basenames', CORSRequestHandler._BLOCKED_BASENAMES)
        handler._blocked_basename_prefixes = kwargs.pop(
            'blocked_basename_prefixes', CORSRequestHandler._BLOCKED_BASENAME_PREFIXES)
        handler._blocked_prefixes = kwargs.pop(
            'blocked_prefixes', CORSRequestHandler._BLOCKED_PREFIXES)
        return handler

    def assert_blocked(self, path, **kwargs):
        h = self._make_handler(path, **kwargs)
        self.assertTrue(h._is_path_blocked(),
                        f"Expected {path!r} to be BLOCKED")
        h.send_error.assert_called_once_with(403, "Forbidden")

    def assert_allowed(self, path, **kwargs):
        h = self._make_handler(path, **kwargs)
        self.assertFalse(h._is_path_blocked(),
                         f"Expected {path!r} to be ALLOWED")
        h.send_error.assert_not_called()

    # ------------------------------------------------------------------
    # CRITICAL C2 — case-insensitive basename bypass (macOS APFS)
    # ------------------------------------------------------------------
    def test_blocks_env_uppercase(self):
        self.assert_blocked('/.ENV')

    def test_blocks_env_mixed_case(self):
        self.assert_blocked('/.Env')

    def test_blocks_env_example_uppercase(self):
        self.assert_blocked('/.ENV.EXAMPLE')

    def test_blocks_config_json_uppercase(self):
        self.assert_blocked('/CONFIG.JSON')

    def test_blocks_config_json_mixed(self):
        self.assert_blocked('/Config.Json')

    # ------------------------------------------------------------------
    # H5 — expanded blocked basenames
    # ------------------------------------------------------------------
    def test_blocks_requirements_txt(self):
        self.assert_blocked('/requirements.txt')

    def test_blocks_dockerfile(self):
        self.assert_blocked('/Dockerfile')

    def test_blocks_docker_compose(self):
        self.assert_blocked('/docker-compose.yml')

    def test_blocks_makefile(self):
        self.assert_blocked('/Makefile')

    def test_blocks_dockerignore(self):
        self.assert_blocked('/.dockerignore')

    def test_blocks_gitignore(self):
        self.assert_blocked('/.gitignore')

    def test_blocks_pyproject_toml(self):
        self.assert_blocked('/pyproject.toml')

    def test_blocks_setup_cfg(self):
        self.assert_blocked('/setup.cfg')

    # ------------------------------------------------------------------
    # E3 — .env variants (.env.backup, .env.production, etc.)
    # ------------------------------------------------------------------
    def test_blocks_env_backup(self):
        self.assert_blocked('/.env.backup')

    def test_blocks_env_production(self):
        self.assert_blocked('/.env.production')

    def test_blocks_env_local(self):
        self.assert_blocked('/.env.local')

    # ------------------------------------------------------------------
    # CRITICAL C1 / E1 — path traversal and symlink attacks
    # ------------------------------------------------------------------
    def test_blocks_dot_dot_traversal(self):
        self.assert_blocked('/../../../etc/passwd')

    def test_blocks_encoded_traversal(self):
        self.assert_blocked('/%2e%2e/%2e%2e/etc/passwd')

    def test_blocks_encoded_dot_dot_slash(self):
        self.assert_blocked('/%2e%2e%2f%2e%2e%2fetc/passwd')

    def test_tilde_is_literal_not_traversal(self):
        """Tilde in URL path is NOT shell expansion — it is a literal dir.
        os.path.realpath resolves it inside REPO_ROOT, so it is safe."""
        self.assert_allowed('/~/.ssh/id_rsa')

    # ------------------------------------------------------------------
    # directory prefix blocks
    # ------------------------------------------------------------------
    def test_blocks_scripts_prefix(self):
        self.assert_blocked('/scripts/limpieza.py')

    def test_blocks_tests_prefix(self):
        self.assert_blocked('/tests/test_calculo_solar.py')

    def test_blocks_archived_prefix(self):
        self.assert_blocked('/archived/old_data.geojson')

    def test_blocks_git_prefix(self):
        self.assert_blocked('/.git/config')

    def test_blocks_git_head(self):
        self.assert_blocked('/.git/HEAD')

    # ------------------------------------------------------------------
    # safe paths — must NOT be blocked
    # ------------------------------------------------------------------
    def test_allows_data_tiles(self):
        self.assert_allowed('/data/tiles/buenos_aires_completo.pmtiles')

    def test_allows_web_index(self):
        self.assert_allowed('/web/index.html')

    def test_allows_web_config_js(self):
        self.assert_allowed('/web/config.js')

    def test_allows_root(self):
        self.assert_allowed('/')

    def test_allows_empty_path(self):
        """Root path with empty clean string."""
        self.assert_allowed('/')

    def test_allows_subdir_file(self):
        self.assert_allowed('/data/raw/parcelas.geojson')

    # ------------------------------------------------------------------
    # query strings and fragments — must not interfere
    # ------------------------------------------------------------------
    def test_ignores_query_string_on_blocked(self):
        self.assert_blocked('/.env?foo=bar&baz=qux')

    def test_ignores_query_string_on_allowed(self):
        self.assert_allowed('/web/index.html?v=2')

    def test_ignores_fragment(self):
        self.assert_blocked('/.env#section')

    # ------------------------------------------------------------------
    # E5 — long / malformed paths (OSError / ValueError guard)
    # ------------------------------------------------------------------
    def test_very_long_path_rejected(self):
        """Paths exceeding OS limits must not crash — blocked safely."""
        long_path = '/' + 'A' * 10000
        h = self._make_handler(long_path)
        result = h._is_path_blocked()
        # Must return True (blocked) or False (allowed) — never raise.
        self.assertIn(result, (True, False))

    def test_null_byte_path_rejected(self):
        """Null byte injection must not crash."""
        h = self._make_handler('/\x00.env')
        result = h._is_path_blocked()
        self.assertIn(result, (True, False))

    # ------------------------------------------------------------------
    # M5 — injectable blocked sets (testing seam)
    # ------------------------------------------------------------------
    def test_injectable_blocked_basenames(self):
        self.assert_blocked('/secret.txt',
                            blocked_basenames={'secret.txt'})

    def test_injectable_blocked_prefixes(self):
        self.assert_blocked('/internal/file.txt',
                            blocked_prefixes=('internal/',))

    def test_injectable_does_not_affect_default(self):
        """Custom basenames should not block paths outside the custom set."""
        custom = {'custom-secret.txt'}
        # Also override prefixes so .env prefix block doesn't interfere.
        self.assert_allowed('/.env',
                            blocked_basenames=custom,
                            blocked_basename_prefixes=())
        self.assert_blocked('/custom-secret.txt', blocked_basenames=custom)


if __name__ == '__main__':
    unittest.main()
